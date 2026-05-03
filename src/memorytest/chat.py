from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from memorytest.adapters import ChatMessage, create_backend
from memorytest.adapters.base import LLMBackend
from memorytest.config import DEFAULT_DB_PATH, env_default
from memorytest.prompts import SYSTEM_PROMPT
from memorytest.storage import ConversationStore
from memorytest.summary_prompt_v1_2 import (
    build_chunk_candidate_request,
    build_summary_request,
)


SUMMARY_CHUNK_CHAR_BUDGET = 12000
SUMMARY_CHUNK_MAX_TOKENS = 1800
SUMMARY_FINAL_MAX_TOKENS = 2600


@dataclass(slots=True)
class SummaryRunResult:
    content: str
    latency_seconds: float
    chunk_count: int


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Terminal chat for memorytest.")
    parser.add_argument("--backend", default="ollama", help="Backend name.")
    parser.add_argument(
        "--model",
        default=env_default("MEMORYTEST_MODEL", "qwen3.5:35b-a3b-q4_K_M"),
        help="Model name for the selected backend.",
    )
    parser.add_argument(
        "--base-url",
        default=env_default("MEMORYTEST_BASE_URL"),
        help="Override backend base URL.",
    )
    parser.add_argument(
        "--api-key",
        default=env_default("MEMORYTEST_API_KEY"),
        help="API key for OpenAI-compatible backends.",
    )
    parser.add_argument(
        "--db-path",
        default=str(DEFAULT_DB_PATH),
        help="SQLite database path.",
    )
    parser.add_argument(
        "--session-id",
        type=int,
        help="Resume an existing session id.",
    )
    parser.add_argument(
        "--think",
        action="store_true",
        help="Allow reasoning-capable models to use thinking mode.",
    )
    parser.add_argument(
        "--summary-max-tokens",
        type=int,
        help="Legacy override that applies the same token budget to both chunk extraction and final consolidation.",
    )
    parser.add_argument(
        "--summary-chunk-max-tokens",
        type=int,
        default=SUMMARY_CHUNK_MAX_TOKENS,
        help="Max output tokens to allow for each chunk during /summarize.",
    )
    parser.add_argument(
        "--summary-final-max-tokens",
        type=int,
        default=SUMMARY_FINAL_MAX_TOKENS,
        help="Max output tokens to allow for the final merged daily memory during /summarize.",
    )
    return parser


def derive_title(first_message: str) -> str:
    title = " ".join(first_message.strip().split())
    if not title:
        return "New Session"
    return title[:60]


def load_conversation(store: ConversationStore, session_id: int) -> list[ChatMessage]:
    return [{"role": "system", "content": SYSTEM_PROMPT}, *store.get_messages(session_id)]


def transcript_text(messages: list[ChatMessage]) -> str:
    lines = []
    for message in messages:
        speaker = "User" if message["role"] == "user" else "Assistant"
        lines.append(f"{speaker}: {message['content']}")
    return "\n".join(lines)


def chunk_messages(
    messages: list[ChatMessage],
    *,
    max_chars: int = SUMMARY_CHUNK_CHAR_BUDGET,
) -> list[list[ChatMessage]]:
    chunks: list[list[ChatMessage]] = []
    current_chunk: list[ChatMessage] = []
    current_chars = 0

    for message in messages:
        message_chars = len(message["content"]) + 16
        if current_chunk and current_chars + message_chars > max_chars:
            chunks.append(current_chunk)
            current_chunk = []
            current_chars = 0

        if not current_chunk and message_chars > max_chars:
            chunks.append([message])
            continue

        current_chunk.append(message)
        current_chars += message_chars

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def summarize_messages(
    backend: LLMBackend,
    messages: list[ChatMessage],
    *,
    max_chunk_chars: int = SUMMARY_CHUNK_CHAR_BUDGET,
    summary_chunk_max_tokens: int = SUMMARY_CHUNK_MAX_TOKENS,
    summary_final_max_tokens: int = SUMMARY_FINAL_MAX_TOKENS,
    summary_max_tokens: int | None = None,
) -> SummaryRunResult:
    chunks = chunk_messages(messages, max_chars=max_chunk_chars)
    candidate_outputs: list[str] = []
    total_latency = 0.0
    original_max_tokens = backend.max_tokens

    if summary_max_tokens is not None:
        summary_chunk_max_tokens = summary_max_tokens
        summary_final_max_tokens = summary_max_tokens

    try:
        backend.max_tokens = max(summary_chunk_max_tokens, original_max_tokens)

        for index, chunk in enumerate(chunks, start=1):
            response = backend.chat(
                build_chunk_candidate_request(
                    chunk,
                    chunk_index=index,
                    chunk_total=len(chunks),
                )
            )
            candidate_outputs.append(response.content)
            total_latency += response.latency_seconds

        backend.max_tokens = max(summary_final_max_tokens, original_max_tokens)
        final_response = backend.chat(build_summary_request(candidate_outputs))
        total_latency += final_response.latency_seconds
        return SummaryRunResult(
            content=final_response.content,
            latency_seconds=total_latency,
            chunk_count=len(chunks),
        )
    finally:
        backend.max_tokens = original_max_tokens


def print_session_details(store: ConversationStore, session_id: int) -> None:
    session = store.get_session(session_id)
    if session is None:
        print(f"Session {session_id} not found.")
        return
    print(f"id: {session.id}")
    print(f"title: {session.title}")
    print(f"backend: {session.backend}")
    print(f"model: {session.model}")
    print(f"messages: {session.message_count}")
    print(f"user_messages: {session.user_message_count}")
    print(f"assistant_messages: {session.assistant_message_count}")
    print(f"created_at: {session.created_at}")
    print(f"updated_at: {session.updated_at}")
    if session.last_user_message_at:
        print(f"last_user_message_at: {session.last_user_message_at}")
    if session.last_assistant_message_at:
        print(f"last_assistant_message_at: {session.last_assistant_message_at}")
    if session.summary:
        print("summary:")
        print(session.summary)
    else:
        print("summary: <none>")


def print_help() -> None:
    print("Commands: /exit, /quit, /history, /sessions, /session, /summarize, /help")


def main() -> None:
    args = build_parser().parse_args()
    store = ConversationStore(Path(args.db_path))

    if args.session_id is not None:
        session = store.get_session(args.session_id)
        if session is None:
            raise SystemExit(f"Session {args.session_id} does not exist.")
        session_id = session.id
    else:
        session_id = store.create_session(backend=args.backend, model=args.model)
        session = store.get_session(session_id)
        assert session is not None

    backend = create_backend(
        args.backend,
        model=args.model,
        base_url=args.base_url,
        api_key=args.api_key,
        think=args.think,
    )

    print(f"Session {session_id} | backend={args.backend} | model={args.model}")
    print_help()

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return

        if not user_input:
            continue

        if user_input in {"/exit", "/quit"}:
            print("Exiting.")
            return
        if user_input == "/help":
            print_help()
            continue
        if user_input == "/sessions":
            for item in store.list_sessions():
                print(f"{item.id}: {item.title} [{item.backend} / {item.model}]")
            continue
        if user_input == "/session":
            print_session_details(store, session_id)
            continue
        if user_input == "/history":
            for message in store.get_messages(session_id):
                print(f"{message['role']}: {message['content']}")
            continue
        if user_input == "/summarize":
            messages = store.get_messages(session_id)
            if not messages:
                print("No conversation to summarize yet.")
                continue
            try:
                summary = summarize_messages(
                    backend,
                    messages,
                    summary_chunk_max_tokens=(
                        args.summary_max_tokens
                        if args.summary_max_tokens is not None
                        else args.summary_chunk_max_tokens
                    ),
                    summary_final_max_tokens=(
                        args.summary_max_tokens
                        if args.summary_max_tokens is not None
                        else args.summary_final_max_tokens
                    ),
                )
            except RuntimeError as exc:
                print(f"Summary error: {exc}")
                continue
            store.set_summary(session_id, summary.content)
            print(
                f"Summary ({summary.latency_seconds:.2f}s across {summary.chunk_count} chunk(s)):\n"
                f"{summary.content}"
            )
            continue

        if not store.get_messages(session_id):
            store.set_title(session_id, derive_title(user_input))

        store.append_message(session_id, "user", user_input)
        conversation = load_conversation(store, session_id)

        try:
            response = backend.chat(conversation)
        except RuntimeError as exc:
            print(f"Assistant error: {exc}")
            continue

        store.append_message(session_id, "assistant", response.content)
        print(f"Assistant ({response.latency_seconds:.2f}s): {response.content}")


if __name__ == "__main__":
    main()

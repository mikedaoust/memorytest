from __future__ import annotations

import unittest

from memorytest.adapters.base import ChatResponse
from memorytest.chat import chunk_messages, summarize_messages
from memorytest.summary_prompt_v1 import (
    build_chunk_candidate_request,
    build_summary_request,
)


class ChatPromptTests(unittest.TestCase):
    def test_chunk_candidate_request_uses_candidate_structure(self) -> None:
        request = build_chunk_candidate_request(
            [{"role": "user", "content": "Good morning"}],
            chunk_index=1,
            chunk_total=3,
        )
        self.assertEqual(len(request), 2)
        self.assertIn("chunk 1 of 3", request[1]["content"])
        self.assertIn("## Relationship Candidates", request[1]["content"])
        self.assertIn("## Project Candidates", request[1]["content"])
        self.assertIn("## Event Candidates", request[1]["content"])
        self.assertIn("## Ritual Signals", request[1]["content"])
        self.assertIn("felt_meaning", request[1]["content"])
        self.assertIn("confidence: explicit|strong_inference|weak_inference", request[1]["content"])
        self.assertIn("Do not add romantic", request[1]["content"])

    def test_summary_request_uses_daily_memory_structure(self) -> None:
        request = build_summary_request(["## Relationship Candidates\n- none"])
        self.assertEqual(len(request), 2)
        self.assertIn("## Morning", request[1]["content"])
        self.assertIn("## Workday", request[1]["content"])
        self.assertIn("## Afternoon And Evening", request[1]["content"])
        self.assertIn("## Carry-Forward", request[1]["content"])
        self.assertIn("Chunk 1 Candidates", request[1]["content"])
        self.assertIn("Start each bullet with tags in square brackets", request[1]["content"])
        self.assertIn("Observed: ... Felt/Meaning: ... Confidence:", request[1]["content"])

    def test_chunk_messages_splits_large_transcript(self) -> None:
        messages = [
            {"role": "user", "content": "a" * 30},
            {"role": "assistant", "content": "b" * 30},
            {"role": "user", "content": "c" * 30},
        ]
        chunks = chunk_messages(messages, max_chars=70)
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0], [messages[0]])
        self.assertEqual(chunks[1], [messages[1]])
        self.assertEqual(chunks[2], [messages[2]])

    def test_summarize_messages_uses_candidate_then_consolidation_pipeline(self) -> None:
        class FakeBackend:
            def __init__(self) -> None:
                self.calls: list[list[dict[str, str]]] = []
                self.max_tokens = 512

            def chat(self, messages: list[dict[str, str]]) -> ChatResponse:
                self.calls.append(messages)
                return ChatResponse(
                    content=f"response {len(self.calls)}",
                    latency_seconds=0.5,
                )

        backend = FakeBackend()
        messages = [
            {"role": "user", "content": "a" * 30},
            {"role": "assistant", "content": "b" * 30},
            {"role": "user", "content": "c" * 30},
        ]
        result = summarize_messages(backend, messages, max_chunk_chars=70)

        self.assertEqual(result.content, "response 4")
        self.assertEqual(result.chunk_count, 3)
        self.assertAlmostEqual(result.latency_seconds, 2.0)
        self.assertEqual(len(backend.calls), 4)
        self.assertIn("chunk 1 of 3", backend.calls[0][1]["content"])
        self.assertIn("Do not treat this chunk as a full day", backend.calls[0][1]["content"])
        self.assertIn("Chunk 1 Candidates", backend.calls[3][1]["content"])
        self.assertIn("response 1", backend.calls[3][1]["content"])

    def test_summarize_messages_restores_backend_max_tokens(self) -> None:
        class FakeBackend:
            def __init__(self) -> None:
                self.calls = 0
                self.max_tokens = 128

            def chat(self, messages: list[dict[str, str]]) -> ChatResponse:
                self.calls += 1
                return ChatResponse(content=f"response {self.calls}", latency_seconds=0.25)

        backend = FakeBackend()
        summarize_messages(
            backend,
            [{"role": "user", "content": "Good morning"}],
            summary_max_tokens=1800,
        )

        self.assertEqual(backend.max_tokens, 128)


if __name__ == "__main__":
    unittest.main()

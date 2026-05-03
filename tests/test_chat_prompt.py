from __future__ import annotations

import unittest

from memorytest.adapters.base import ChatResponse
from memorytest.chat import summarize_messages


class ChatPromptTests(unittest.TestCase):
    def test_summarize_messages_uses_separate_chunk_and_final_token_budgets(self) -> None:
        class FakeBackend:
            def __init__(self) -> None:
                self.calls = 0
                self.max_tokens = 128
                self.max_tokens_seen: list[int] = []

            def chat(self, messages: list[dict[str, str]]) -> ChatResponse:
                self.calls += 1
                self.max_tokens_seen.append(self.max_tokens)
                return ChatResponse(content=f"response {self.calls}", latency_seconds=0.25)

        backend = FakeBackend()
        summarize_messages(
            backend,
            [
                {"role": "user", "content": "a" * 30},
                {"role": "assistant", "content": "b" * 30},
                {"role": "user", "content": "c" * 30},
            ],
            max_chunk_chars=70,
            summary_chunk_max_tokens=900,
            summary_final_max_tokens=1400,
        )

        self.assertEqual(backend.max_tokens_seen, [900, 900, 900, 1400])


if __name__ == "__main__":
    unittest.main()

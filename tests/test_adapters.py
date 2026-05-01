from __future__ import annotations

import io
import json
import unittest
from unittest.mock import patch

from memorytest.adapters.factory import create_backend
from memorytest.adapters.ollama import OllamaBackend
from memorytest.adapters.openai_compat import OpenAICompatBackend


class FakeHTTPResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self) -> "FakeHTTPResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class AdapterTests(unittest.TestCase):
    def test_factory_creates_expected_backends(self) -> None:
        self.assertIsInstance(create_backend("ollama", model="qwen3.5:9b"), OllamaBackend)
        self.assertIsInstance(
            create_backend("openai-compat", model="qwen3.5-35b-a3b"),
            OpenAICompatBackend,
        )

    @patch("urllib.request.urlopen")
    def test_ollama_backend_parses_chat_response(self, mock_urlopen) -> None:
        mock_urlopen.return_value = FakeHTTPResponse(
            {"message": {"content": "hello from ollama"}}
        )
        backend = OllamaBackend(model="qwen3.5:9b")
        response = backend.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(response.content, "hello from ollama")

    @patch("urllib.request.urlopen")
    def test_openai_compat_backend_parses_chat_response(self, mock_urlopen) -> None:
        mock_urlopen.return_value = FakeHTTPResponse(
            {"choices": [{"message": {"content": "hello from compat"}}]}
        )
        backend = OpenAICompatBackend(model="qwen3.5-35b-a3b")
        response = backend.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(response.content, "hello from compat")


if __name__ == "__main__":
    unittest.main()

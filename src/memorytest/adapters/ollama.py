from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from memorytest.adapters.base import ChatMessage, ChatResponse, LLMBackend


class OllamaBackend(LLMBackend):
    def __init__(
        self,
        *,
        model: str,
        base_url: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
        think: bool = False,
    ) -> None:
        super().__init__(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            think=think,
        )
        self.base_url = (base_url or "http://127.0.0.1:11434").rstrip("/")

    def chat(self, messages: list[ChatMessage]) -> ChatResponse:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "think": self.think,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
        )

        start = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                parsed = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Ollama request failed with status {exc.code}: {body}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Could not reach Ollama at {self.base_url}. Is the server running?"
            ) from exc

        latency = time.perf_counter() - start
        message = parsed.get("message", {})
        content = message.get("content", "").strip()
        if not content:
            raise RuntimeError("Ollama returned an empty response.")

        return ChatResponse(content=content, latency_seconds=latency, raw=parsed)

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from memorytest.adapters.base import ChatMessage, ChatResponse, LLMBackend


class OpenAICompatBackend(LLMBackend):
    def __init__(
        self,
        *,
        model: str,
        base_url: str | None = None,
        api_key: str | None = None,
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
        self.base_url = (base_url or "http://127.0.0.1:1234/v1").rstrip("/")
        self.api_key = api_key or "not-needed"

    def chat(self, messages: list[ChatMessage]) -> ChatResponse:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        start = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                parsed = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"OpenAI-compatible request failed with status {exc.code}: {body}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Could not reach an OpenAI-compatible server at {self.base_url}."
            ) from exc

        latency = time.perf_counter() - start
        choices = parsed.get("choices") or []
        if not choices:
            raise RuntimeError("OpenAI-compatible backend returned no choices.")

        message = choices[0].get("message", {})
        content = (message.get("content") or "").strip()
        if not content:
            raise RuntimeError("OpenAI-compatible backend returned an empty response.")

        return ChatResponse(content=content, latency_seconds=latency, raw=parsed)

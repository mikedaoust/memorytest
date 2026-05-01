from __future__ import annotations

from memorytest.adapters.base import LLMBackend
from memorytest.adapters.ollama import OllamaBackend
from memorytest.adapters.openai_compat import OpenAICompatBackend


def create_backend(
    backend: str,
    *,
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 512,
    think: bool = False,
    base_url: str | None = None,
    api_key: str | None = None,
) -> LLMBackend:
    normalized = backend.strip().lower()
    common = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "think": think,
    }

    if normalized == "ollama":
        return OllamaBackend(base_url=base_url, **common)

    if normalized in {"openai", "openai-compat", "lmstudio"}:
        return OpenAICompatBackend(base_url=base_url, api_key=api_key, **common)

    raise ValueError(f"Unsupported backend: {backend}")

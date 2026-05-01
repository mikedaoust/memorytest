from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypedDict


class ChatMessage(TypedDict):
    role: str
    content: str


@dataclass(slots=True)
class ChatResponse:
    content: str
    latency_seconds: float
    raw: dict | None = None


class LLMBackend(ABC):
    def __init__(
        self,
        *,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
        think: bool = False,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.think = think

    @abstractmethod
    def chat(self, messages: list[ChatMessage]) -> ChatResponse:
        raise NotImplementedError

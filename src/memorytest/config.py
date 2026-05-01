from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_DB_PATH = Path("data/memorytest.db")


@dataclass(slots=True)
class BackendConfig:
    backend: str
    model: str
    base_url: str | None = None
    api_key: str | None = None
    think: bool = False
    temperature: float = 0.7
    max_tokens: int = 512


def env_default(name: str, fallback: str | None = None) -> str | None:
    value = os.getenv(name)
    if value:
        return value
    return fallback

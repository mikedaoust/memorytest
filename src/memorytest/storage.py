from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from memorytest.adapters.base import ChatMessage


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class SessionRecord:
    id: int
    title: str
    backend: str
    model: str
    summary: str
    message_count: int
    user_message_count: int
    assistant_message_count: int
    created_at: str
    updated_at: str
    last_user_message_at: str | None = None
    last_assistant_message_at: str | None = None


class ConversationStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    backend TEXT NOT NULL,
                    model TEXT NOT NULL,
                    summary TEXT NOT NULL DEFAULT '',
                    message_count INTEGER NOT NULL DEFAULT 0,
                    user_message_count INTEGER NOT NULL DEFAULT 0,
                    assistant_message_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_user_message_at TEXT,
                    last_assistant_message_at TEXT
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                );
                """
            )
            self._ensure_column(
                connection,
                "sessions",
                "summary",
                "TEXT NOT NULL DEFAULT ''",
            )
            self._ensure_column(
                connection,
                "sessions",
                "message_count",
                "INTEGER NOT NULL DEFAULT 0",
            )
            self._ensure_column(
                connection,
                "sessions",
                "user_message_count",
                "INTEGER NOT NULL DEFAULT 0",
            )
            self._ensure_column(
                connection,
                "sessions",
                "assistant_message_count",
                "INTEGER NOT NULL DEFAULT 0",
            )
            self._ensure_column(connection, "sessions", "last_user_message_at", "TEXT")
            self._ensure_column(connection, "sessions", "last_assistant_message_at", "TEXT")

    def _ensure_column(
        self,
        connection: sqlite3.Connection,
        table_name: str,
        column_name: str,
        column_definition: str,
    ) -> None:
        existing = {
            row["name"]
            for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
        }
        if column_name in existing:
            return
        connection.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        )

    def create_session(self, *, backend: str, model: str, title: str = "New Session") -> int:
        timestamp = utc_now()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO sessions (
                    title,
                    backend,
                    model,
                    summary,
                    message_count,
                    user_message_count,
                    assistant_message_count,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, '', 0, 0, 0, ?, ?)
                """,
                (title, backend, model, timestamp, timestamp),
            )
            return int(cursor.lastrowid)

    def get_session(self, session_id: int) -> SessionRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return SessionRecord(**dict(row))

    def list_sessions(self) -> list[SessionRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM sessions ORDER BY updated_at DESC"
            ).fetchall()
        return [SessionRecord(**dict(row)) for row in rows]

    def set_title(self, session_id: int, title: str) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE sessions
                SET title = ?, updated_at = ?
                WHERE id = ?
                """,
                (title, utc_now(), session_id),
            )

    def set_summary(self, session_id: int, summary: str) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE sessions
                SET summary = ?, updated_at = ?
                WHERE id = ?
                """,
                (summary, utc_now(), session_id),
            )

    def append_message(self, session_id: int, role: str, content: str) -> None:
        timestamp = utc_now()
        is_user = 1 if role == "user" else 0
        is_assistant = 1 if role == "assistant" else 0
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO messages (session_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, role, content, timestamp),
            )
            connection.execute(
                """
                UPDATE sessions
                SET
                    message_count = message_count + 1,
                    user_message_count = user_message_count + ?,
                    assistant_message_count = assistant_message_count + ?,
                    last_user_message_at = CASE
                        WHEN ? = 1 THEN ?
                        ELSE last_user_message_at
                    END,
                    last_assistant_message_at = CASE
                        WHEN ? = 1 THEN ?
                        ELSE last_assistant_message_at
                    END,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    is_user,
                    is_assistant,
                    is_user,
                    timestamp,
                    is_assistant,
                    timestamp,
                    timestamp,
                    session_id,
                ),
            )

    def get_messages(self, session_id: int) -> list[ChatMessage]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT role, content
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()
        return [ChatMessage(role=row["role"], content=row["content"]) for row in rows]

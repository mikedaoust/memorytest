from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sqlite3

from memorytest.storage import ConversationStore


class ConversationStoreTests(unittest.TestCase):
    def test_session_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ConversationStore(Path(tmpdir) / "memorytest.db")
            session_id = store.create_session(backend="ollama", model="qwen3.5:9b")
            store.set_title(session_id, "Test Session")
            store.append_message(session_id, "user", "Hello")
            store.append_message(session_id, "assistant", "Hi there")
            store.set_summary(session_id, "- user greeted\n- assistant replied\n- no blockers")

            session = store.get_session(session_id)
            messages = store.get_messages(session_id)

        self.assertIsNotNone(session)
        assert session is not None
        self.assertEqual(session.title, "Test Session")
        self.assertEqual(session.message_count, 2)
        self.assertEqual(session.user_message_count, 1)
        self.assertEqual(session.assistant_message_count, 1)
        self.assertEqual(session.summary, "- user greeted\n- assistant replied\n- no blockers")
        self.assertEqual(
            messages,
            [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there"},
            ],
        )

    def test_migrates_old_session_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "memorytest.db"
            connection = sqlite3.connect(db_path)
            connection.executescript(
                """
                CREATE TABLE sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    backend TEXT NOT NULL,
                    model TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            connection.close()

            store = ConversationStore(db_path)
            session_id = store.create_session(backend="ollama", model="qwen3.5:35b-a3b-q4_K_M")
            store.append_message(session_id, "user", "Hello")
            session = store.get_session(session_id)

        self.assertIsNotNone(session)
        assert session is not None
        self.assertEqual(session.message_count, 1)
        self.assertEqual(session.user_message_count, 1)
        self.assertEqual(session.assistant_message_count, 0)


if __name__ == "__main__":
    unittest.main()

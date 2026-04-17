from pathlib import Path

from database.db import DatabaseManager


def test_init_db_creates_events_table(tmp_path):
    db_file = tmp_path / "events.db"
    manager = DatabaseManager(str(db_file))

    manager.init_db()

    conn = manager.get_connection()
    try:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='events'"
        ).fetchone()
    finally:
        conn.close()

    assert row is not None


def test_connection_can_insert_and_read(tmp_path):
    db_file = Path(tmp_path) / "events.db"
    manager = DatabaseManager(str(db_file))
    manager.init_db()

    conn = manager.get_connection()
    try:
        conn.execute(
            "INSERT INTO events (timestamp, predicted_label, confidence, alert) VALUES (?, ?, ?, ?)",
            ("2026-01-01T00:00:00", 1, 0.65, "warn"),
        )
        conn.commit()
        row = conn.execute(
            "SELECT predicted_label, confidence, alert FROM events"
        ).fetchone()
    finally:
        conn.close()

    assert row == (1, 0.65, "warn")

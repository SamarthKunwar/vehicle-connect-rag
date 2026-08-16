"""Loads connect_events.csv into a SQLite database for structured querying.

This is the "structured half" of retrieval: time-range, module, and
error-code filters run as indexed SQL queries instead of scanning the CSV.
"""
import csv
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    session_id TEXT NOT NULL,
    module TEXT NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    error_code TEXT,
    message TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_timestamp ON events (timestamp);
CREATE INDEX IF NOT EXISTS idx_module ON events (module);
CREATE INDEX IF NOT EXISTS idx_error_code ON events (error_code);
CREATE INDEX IF NOT EXISTS idx_session_id ON events (session_id);
"""


def load(csv_path=Path("data/logs/connect_events.csv"), db_path=Path("data/logs/connect_events.db")):
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    conn.execute("DELETE FROM events")  # idempotent: safe to re-run after regenerating logs

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (r["timestamp"], r["session_id"], r["module"], r["event_type"],
             r["severity"], r["error_code"] or None, r["message"])
            for r in reader
        ]

    conn.executemany(
        """INSERT INTO events (timestamp, session_id, module, event_type, severity, error_code, message)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    print(f"Loaded {count} events into {db_path}")
    conn.close()


if __name__ == "__main__":
    load()

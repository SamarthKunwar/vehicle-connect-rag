import sqlite3
from pathlib import Path

DB_PATH = Path("data/logs/connect_events.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def find_events_by_error_code(error_code, limit=5):
    """Most recent occurrences of a specific error code."""
    conn = _connect()
    rows = conn.execute(
        """SELECT timestamp, session_id, module, message
           FROM events
           WHERE error_code = ?
           ORDER BY timestamp DESC
           LIMIT ?""",
        (error_code, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_session_trace(session_id):
    """Full ordered sequence of events for one session."""
    conn = _connect()
    rows = conn.execute(
        """SELECT timestamp, module, event_type, severity, error_code, message
           FROM events
           WHERE session_id = ?
           ORDER BY timestamp""",
        (session_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_context_for_error_code(error_code, limit=3):
    """The real payoff function: find recent occurrences of an error code,
    and for each one, pull the FULL session trace around it -- not just
    the error line, but what led up to it and what happened after.
    """
    occurrences = find_events_by_error_code(error_code, limit=limit)
    results = []
    for occ in occurrences:
        trace = get_session_trace(occ["session_id"])
        results.append({"session_id": occ["session_id"], "trace": trace})
    return results


if __name__ == "__main__":
    error_code = "E-BT-207"
    contexts = get_context_for_error_code(error_code, limit=2)
    print(f"Error code: {error_code}\n")
    for c in contexts:
        print(f"=== session {c['session_id']} ===")
        for e in c["trace"]:
            print(f"  {e['timestamp']}  {e['event_type']:16} {e['severity']:5} {e['error_code'] or '':10} {e['message']}")
        print()

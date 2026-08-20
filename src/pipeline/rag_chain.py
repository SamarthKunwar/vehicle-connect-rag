import re
import sqlite3
import sys
import ollama
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "retrieval"))

from semantic_search import semantic_search
from structured_query import get_context_for_error_code

VECTOR_DB_PATH = Path("data/vector_store/chunks.db")
ERROR_CODE_PATTERN = re.compile(r"E-[A-Z]+-\d+")

MODEL_NAME = "llama3.1:8b"


def format_log_sessions(log_sessions):
    if not log_sessions:
        return "(no matching log events found)"

    log_text = ""
    for session in log_sessions:
        log_text += f"\nSession {session['session_id']}:\n"
        for e in session["trace"]:
            log_text += f"  {e['timestamp']} | {e['event_type']} | {e['severity']} | {e['message']}\n"
    return log_text


def build_prompt(query, doc_chunk, log_sessions):
    doc_text = doc_chunk["text"] if doc_chunk else "(no matching documentation found)"
    log_text = format_log_sessions(log_sessions)

    return f"""You are a diagnostics assistant for a connected-vehicle infotainment platform.
Answer the user's question using ONLY the documentation and log evidence below.
Cite specific timestamps and session IDs from the log evidence when explaining what happened.
If the evidence doesn't fully answer the question, say what's missing rather than guessing.

# User question
{query}

# Documentation
{doc_text}

# Log evidence
{log_text}

# Answer
"""


def synthesize_answer(query, doc_chunk, log_sessions):
    prompt = build_prompt(query, doc_chunk, log_sessions)
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]



def find_doc_chunk_by_error_code(error_code):
    conn = sqlite3.connect(VECTOR_DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM chunks WHERE error_codes LIKE ? LIMIT 1",
        (f"%{error_code}%",),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def answer_query(query, top_k=1, synthesize=True):
    explicit_match = ERROR_CODE_PATTERN.search(query.upper())

    if explicit_match:
        error_code = explicit_match.group(0)
        path = "explicit error code in query"
    else:
        doc_hits = semantic_search(query, top_k=top_k)
        top_hit = doc_hits[0] if doc_hits else None
        error_code = None
        if top_hit and top_hit["primary_error_code"]:
            error_code = top_hit["primary_error_code"]
        path = "inferred from semantic search"

    doc_chunk = find_doc_chunk_by_error_code(error_code) if error_code else None
    log_context = get_context_for_error_code(error_code, limit=2) if error_code else []

    answer = synthesize_answer(query, doc_chunk, log_context) if synthesize else None

    return {
        "query": query,
        "resolution_path": path,
        "error_code": error_code,
        "doc_chunk": doc_chunk,
        "log_sessions": log_context,
        "answer": answer,
    }



if __name__ == "__main__":
    query = "why does bluetooth lose signal"
    result = answer_query(query)
    print(f"Query: {result['query']}")
    print(f"Resolution path: {result['resolution_path']}")
    print(f"Error code: {result['error_code']}\n")

    if result["doc_chunk"]:
        print("--- Doc explanation ---")
        print(result["doc_chunk"]["text"][:300])
        print()

    print("--- Log evidence ---")
    for session in result["log_sessions"]:
        print(f"session {session['session_id']}:")
        for e in session["trace"]:
            print(f"  {e['timestamp']}  {e['event_type']:16} {e['severity']:5} {e['message']}")
        print()
    print("--- Synthesized answer ---")
    print(result["answer"])


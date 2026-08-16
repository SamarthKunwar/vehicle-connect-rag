import sqlite3
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
VECTOR_STORE_DIR = Path("data/vector_store")

_model = None
_index = None


def _load_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _load_index():
    global _index
    if _index is None:
        _index = faiss.read_index(str(VECTOR_STORE_DIR / "faiss_index.bin"))
    return _index


def semantic_search(query, top_k=3):
    model = _load_model()
    index = _load_index()

    query_vec = model.encode([query]).astype("float32")
    faiss.normalize_L2(query_vec)

    scores, ids = index.search(query_vec, top_k)

    conn = sqlite3.connect(VECTOR_STORE_DIR / "chunks.db")
    conn.row_factory = sqlite3.Row

    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx == -1:
            continue
        row = conn.execute("SELECT * FROM chunks WHERE id = ?", (int(idx),)).fetchone()
        results.append({
            "score": float(score),
            "section_title": row["section_title"],
            "module": row["module"],
            "error_codes": row["error_codes"],
            "primary_error_code": row["primary_error_code"],
            "text": row["text"],
        })
    conn.close()
    return results


if __name__ == "__main__":
    query = "my phone keeps randomly disconnecting from the car while driving"
    results = semantic_search(query)
    print(f"Query: {query}\n")
    for r in results:
        print(f"[{r['score']:.3f}] {r['section_title']} (module={r['module']}, error_codes={r['error_codes'] or 'none'})")
        print(r["text"][:150].replace("\n", " ") + "...")
        print()

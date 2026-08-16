import sqlite3
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from doc_chunker import chunk_all_docs

MODEL_NAME = "all-MiniLM-L6-v2"
VECTOR_STORE_DIR = Path("data/vector_store")


def build_index():
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

    chunks = chunk_all_docs()
    texts = [c["text"] for c in chunks]

    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings, dtype="float32")

    # normalize so inner product == cosine similarity
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    faiss.write_index(index, str(VECTOR_STORE_DIR / "faiss_index.bin"))

    db_path = VECTOR_STORE_DIR / "chunks.db"
    conn = sqlite3.connect(db_path)
    conn.execute("DROP TABLE IF EXISTS chunks")
    conn.execute("""
        CREATE TABLE chunks (
            id INTEGER PRIMARY KEY,
            source_file TEXT,
            module TEXT,
            section_title TEXT,
            error_codes TEXT,
            text TEXT
        )
    """)
    rows = [
        (i, c["metadata"]["source_file"], c["metadata"]["module"],
         c["metadata"]["section_title"], c["metadata"]["error_codes"], c["text"])
        for i, c in enumerate(chunks)
    ]
    conn.executemany("INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?)", rows)
    conn.commit()
    conn.close()

    print(f"Indexed {len(chunks)} chunks")
    print(f"  FAISS index -> {VECTOR_STORE_DIR / 'faiss_index.bin'}")
    print(f"  Metadata db -> {db_path}")


if __name__ == "__main__":
    build_index()

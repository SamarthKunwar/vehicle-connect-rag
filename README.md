# Vehicle Connect RAG

A retrieval-augmented trace analysis assistant for a connected-vehicle
infotainment/connect platform. Built as a portfolio project exploring how
RAG applies to systems/trace data, not just document Q&A.

## What it does

Combines two retrieval modes over connect-module event data (bluetooth,
wifi, infotainment boot, cloud sync, navigation, voice assistant):

- **Structured retrieval** — indexed SQL queries over event logs (time
  range, module, error code, session).
- **Semantic retrieval** — embedding-based search over troubleshooting
  documentation, chunked by section so each error code's cause/diagnosis/
  resolution stays intact as one retrievable unit.

The two are joined by `error_code`: a log event tells you *what happened
and when*; the matching doc section tells you *why it happens and what to
do about it*. Neither alone answers a real trace-analysis question.

## Data

The event logs and documentation in `data/` are **synthetic**, generated
by scripts in this repo (`src/ingest/generate_logs.py`). Real connected-
vehicle telemetry is proprietary, and no public dataset pairs raw traces
with matching documentation for a specific manufacturer's platform — so
this is an intentional proof-of-concept built on realistic, self-authored
data rather than a claim of real vehicle data.

## Status

Work in progress. Current pipeline:

1. Synthetic log generation (`src/ingest/generate_logs.py`)
2. Structured log store — SQLite, indexed on timestamp/module/error_code/
   session_id (`src/ingest/log_loader.py`)
3. Documentation chunking — structural (heading-based) chunking with
   metadata extraction, including error-code cross-referencing
   (`src/ingest/doc_chunker.py`)
4. Embeddings + vector store — in progress
5. Hybrid retrieval pipeline — planned
6. Evaluation harness — planned

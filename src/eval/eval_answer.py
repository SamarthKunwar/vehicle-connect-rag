import re
import sys
from pathlib import Path

import ollama

sys.path.append(str(Path(__file__).parent.parent / "pipeline"))

from rag_chain import answer_query, format_log_sessions, MODEL_NAME
from eval_set import EVAL_SET

VERDICT_PATTERN = re.compile(r"VERDICT:\s*(GROUNDED|PARTIALLY_GROUNDED|UNGROUNDED)", re.IGNORECASE)


def build_judge_prompt(query, doc_chunk, log_sessions, answer):
    doc_text = doc_chunk["text"] if doc_chunk else "(no matching documentation found)"
    log_text = format_log_sessions(log_sessions)

    return f"""You are grading whether an AI-generated answer stays grounded in the
evidence it was given -- not whether the answer is well-written or the
retrieval was correct.

# Original question
{query}

# Evidence available to the AI (documentation)
{doc_text}

# Evidence available to the AI (log sessions)
{log_text}

# The AI's answer
{answer}

# Your task
Both the documentation and the log sessions above count as evidence --
they are not two separate tiers. A claim about *why* something happens,
what it means, or what to do about it is grounded if it matches the
documentation, even if that exact wording never appears in the logs. A
claim about a *specific event* -- a timestamp, a duration, a session ID,
whether something did or didn't happen in this instance -- must match the
log evidence specifically; the documentation alone cannot support it.

Step 1: List each distinct factual claim in the AI's answer as a numbered
list. For any claim involving a number (a duration, a time gap, a count),
recompute that number yourself directly from the raw timestamps/text in
the evidence above -- do not trust the AI's arithmetic, redo it.

Step 2: For each claim, write one line: quote the exact evidence (from
either the documentation or the logs, whichever applies) that supports or
contradicts it, or write "NOT IN EVIDENCE" only if neither source
addresses it at all.

Step 3: Based only on what you wrote in Step 2 -- not on how the answer
reads -- give your final verdict.

Respond in exactly this format:
CLAIMS:
1. <claim> -> <matching evidence quote, recomputed number, or "NOT IN EVIDENCE">
2. <claim> -> <...>
(one line per distinct claim)

VERDICT: <GROUNDED, PARTIALLY_GROUNDED, or UNGROUNDED>
"""


def judge_faithfulness(query, doc_chunk, log_sessions, answer):
    prompt = build_judge_prompt(query, doc_chunk, log_sessions, answer)
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )
    verdict_text = response["message"]["content"]

    match = VERDICT_PATTERN.search(verdict_text)
    verdict = match.group(1).upper() if match else "UNPARSEABLE"

    return verdict, verdict_text


def run_eval(limit=None):
    cases = EVAL_SET[:limit] if limit else EVAL_SET
    results = []

    for case in cases:
        result = answer_query(case["query"], synthesize=True)
        verdict, raw_judgement = judge_faithfulness(
            case["query"], result["doc_chunk"], result["log_sessions"], result["answer"]
        )
        results.append({
            "query": case["query"],
            "answer": result["answer"],
            "verdict": verdict,
            "raw_judgement": raw_judgement,
        })
        print(f"[{verdict}] {case['query']}")

    print()
    counts = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    total = len(results)
    for verdict, count in sorted(counts.items()):
        print(f"{verdict}: {count}/{total} ({count / total:.1%})")

    return results


if __name__ == "__main__":
    results = run_eval()

    print("\n\n=== Full judgements for non-GROUNDED answers ===")
    for r in results:
        if r["verdict"] != "GROUNDED":
            print(f"\nQuery: {r['query']}")
            print(f"Answer: {r['answer']}")
            print(f"Judgement:\n{r['raw_judgement']}")

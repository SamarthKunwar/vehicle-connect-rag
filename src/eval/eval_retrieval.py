import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "pipeline"))

from rag_chain import answer_query
from eval_set import EVAL_SET


def run_eval():
    results = []
    for case in EVAL_SET:
        result = answer_query(case["query"], synthesize=False)
        got = result["error_code"]
        is_correct = got == case["expected_error_code"]
        results.append((case["query"], case["expected_error_code"], got, is_correct))

    for query, expected, got, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {query}")
        if not ok:
            print(f"         expected={expected}  got={got}")

    correct = sum(1 for *_, ok in results if ok)
    print(f"\nRetrieval accuracy: {correct}/{len(EVAL_SET)} = {correct / len(EVAL_SET):.1%}")


if __name__ == "__main__":
    run_eval()

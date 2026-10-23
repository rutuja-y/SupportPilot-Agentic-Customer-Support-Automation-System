
from evaluation.evaluation_dataset import EVALUATION_CASES
from support_graph import run_support_workflow


def evaluate_answers():
    passed = 0

    print("\n=== SupportPilot Answer Evaluation ===")

    for case in EVALUATION_CASES:
        try:
            result = run_support_workflow(case["question"])

            answer = result["answer"].strip()
            sources = result.get("sources", [])

            source_found = case["expected_source"] in sources
            answer_present = bool(answer)

            # Basic sanity check, not a semantic correctness test.
            keywords_found = any(
                keyword.lower() in answer.lower()
                for keyword in case["expected_keywords"]
            )

            success = (
                answer_present
                and source_found
                and keywords_found
            )

            if success:
                passed += 1

            status = "PASS" if success else "REVIEW"

            print(f"\n[{status}] {case['question']}")
            print(f"Category: {result.get('category')}")
            print(f"Sources: {sources}")
            print(f"Answer: {answer}")
            print(f"Expected source found: {source_found}")
            print(f"Keyword check passed: {keywords_found}")

        except Exception as exc:
            print(f"\n[ERROR] {case['question']}: {exc}")

    total = len(EVALUATION_CASES)

    print(f"\nBasic answer checks: {passed}/{total} ({passed / total:.1%})")


if __name__ == "__main__":
    evaluate_answers()

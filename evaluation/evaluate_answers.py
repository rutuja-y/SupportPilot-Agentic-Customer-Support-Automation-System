
from evaluation.evaluation_dataset import EVALUATION_CASES
from support_graph import run_support_workflow


def evaluate_answers():
    results = []

    print("\n=== SupportPilot Answer Evaluation ===")

    for case in EVALUATION_CASES:
        case_id = case["id"]
        question = case["question"]

        try:
            result = run_support_workflow(question)

            answer = result.get("answer", "").strip()
            sources = set(result.get("sources", []))
            expected_sources = set(case["expected_sources"])
            expected_keywords = case["expected_keywords"]
            expected_behavior = case["expected_behavior"]

            actual_category = result.get("category", "")
            expected_category = case["expected_category"]

            # Check that an answer was generated.
            answer_present = bool(answer)

            # Check that all expected sources were retrieved.
            source_check = expected_sources.issubset(sources)

            # Basic keyword check. This is a sanity check, not
            # a complete semantic correctness evaluation.
            keywords_found = any(
                keyword.lower() in answer.lower()
                for keyword in expected_keywords
            )

            # "other" is used for multi-topic questions in this
            # dataset, so don't enforce it as a classification label.
            category_check = (
                True
                if expected_category == "other"
                else actual_category == expected_category
            )

            
            if expected_behavior == "abstain":
                uncertainty_phrases = [
                    "cannot confirm",
                    "can't confirm",
                    "cannot determine",
                    "can't determine",
                    "don't have access",
                    "doesn't specify",
                    "not specified",
                    "can't say whether",
                    "cannot say whether",
                    "can't guarantee",
                    "cannot guarantee",
                    "not guaranteed",
                    "without confirmation",
                    "don't have the exact",
                    "don't have access to the specific",
                ]

                answer_lower = answer.lower()
                behavior_check = (
                    answer_present
                    and any(
                        phrase in answer_lower
                        for phrase in uncertainty_phrases
                    )
                )
            else:
                behavior_check = answer_present and keywords_found


            passed = (
                answer_present
                and source_check
                and category_check
                and behavior_check
            )

            results.append({
                "id": case_id,
                "passed": passed,
                "error": None,
            })

            status = "PASS" if passed else "REVIEW"

            print(f"\n[{status}] {case_id}: {question}")
            print(f"  Category: {actual_category} "
                  f"(expected: {expected_category})")
            print(f"  Sources: {sorted(sources)}")
            print(f"  Expected sources found: {source_check}")
            print(f"  Keyword check: {keywords_found}")
            print(f"  Behavior check: {behavior_check}")

            if not passed:
                print(f"  Answer: {answer}")

        except Exception as exc:
            results.append({
                "id": case_id,
                "passed": False,
                "error": str(exc),
            })
            print(f"\n[ERROR] {case_id}: {question}: {exc}")

    total = len(results)
    passed_count = sum(item["passed"] for item in results)
    errors = sum(item["error"] is not None for item in results)

    print("\n=== Evaluation Summary ===")
    print(f"Passed: {passed_count}/{total}")
    print(f"Failed/review: {total - passed_count}/{total}")
    print(f"Errors: {errors}")

    if total:
        print(f"Basic check pass rate: {passed_count / total:.1%}")

    return results


if __name__ == "__main__":
    evaluate_answers()

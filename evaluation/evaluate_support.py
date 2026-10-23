
from evaluation.evaluation_dataset import EVALUATION_CASES
from vector_store import search_knowledge


def evaluate_retrieval():
    results = []

    for case in EVALUATION_CASES:
        chunks = search_knowledge(case["question"], top_k=3)

        retrieved_sources = {
            chunk.get("metadata", {}).get("source", "")
            for chunk in chunks
            if chunk.get("metadata", {}).get("source")
        }

        expected_sources = set(case["expected_sources"])
        behavior = case["expected_behavior"]

        # A source is relevant if it is one of the expected sources.
        relevant_sources = expected_sources & retrieved_sources

        # Unanswerable cases with no expected sources are not retrieval
        # failures just because no source matches.
        if behavior == "abstain" and not expected_sources:
            passed = True
            metric = "N/A (no expected source)"
        else:
            passed = bool(expected_sources) and bool(relevant_sources)
            metric = (
                f"{len(relevant_sources)}/{len(expected_sources)} "
                "expected sources found"
            )

        results.append({
            "id": case["id"],
            "question": case["question"],
            "expected_sources": sorted(expected_sources),
            "retrieved_sources": sorted(retrieved_sources),
            "relevant_sources": sorted(relevant_sources),
            "passed": passed,
            "metric": metric,
            "behavior": behavior,
        })

    # Evaluate only cases that have an expected source.
    source_cases = [
        item for item in results if item["expected_sources"]
    ]
    passed = sum(item["passed"] for item in source_cases)
    total = len(source_cases)

    print("\n=== SupportPilot Retrieval Evaluation ===")

    for item in results:
        status = "PASS" if item["passed"] else "FAIL"

        print(f"\n[{status}] {item['id']}: {item['question']}")
        print(f"Expected sources: {item['expected_sources']}")
        print(f"Retrieved sources: {item['retrieved_sources']}")
        print(f"Relevant sources: {item['relevant_sources']}")
        print(f"Result: {item['metric']}")

    if total:
        print(
            f"\nSource hit rate: {passed}/{total} "
            f"({passed / total:.1%})"
        )
    else:
        print("\nNo cases with expected sources to evaluate.")

    return results


if __name__ == "__main__":
    evaluate_retrieval()

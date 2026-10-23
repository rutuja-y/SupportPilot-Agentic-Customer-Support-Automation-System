
from evaluation.evaluation_dataset import EVALUATION_CASES
from vector_store import search_knowledge


def evaluate_retrieval():
    results = []

    for case in EVALUATION_CASES:
        chunks = search_knowledge(case["question"], top_k=3)

        retrieved_sources = {
            chunk.get("metadata", {}).get("source", "")
            for chunk in chunks
        }

        source_found = case["expected_source"] in retrieved_sources

        results.append({
            "question": case["question"],
            "expected_source": case["expected_source"],
            "retrieved_sources": sorted(retrieved_sources),
            "source_found": source_found,
        })

    passed = sum(item["source_found"] for item in results)
    total = len(results)

    print("\n=== SupportPilot Retrieval Evaluation ===")
    for item in results:
        status = "PASS" if item["source_found"] else "FAIL"
        print(f"\n[{status}] {item['question']}")
        print(f"Expected: {item['expected_source']}")
        print(f"Retrieved: {item['retrieved_sources']}")

    print(f"\nSource hit rate: {passed}/{total} ({passed / total:.1%})")

    return results


if __name__ == "__main__":
    evaluate_retrieval()

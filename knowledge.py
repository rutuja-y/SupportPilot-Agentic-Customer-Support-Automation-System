
from dataclasses import dataclass
from datetime import date
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = PROJECT_DIR / "knowledge_base"


@dataclass
class KnowledgeDocument:
    document_id: str
    title: str
    category: str
    source: str
    updated_at: str
    content: str


# Metadata for the fictional demo-store policies.
DOCUMENT_METADATA = {
    "shipping.md": {
        "document_id": "KB001",
        "title": "Shipping and Delivery Policy",
        "category": "shipping",
    },
    "returns_refunds.md": {
        "document_id": "KB002",
        "title": "Returns and Refunds Policy",
        "category": "returns",
    },
    "warranty.md": {
        "document_id": "KB003",
        "title": "Warranty Policy",
        "category": "warranty",
    },
    "troubleshooting.md": {
        "document_id": "KB004",
        "title": "Basic Product Troubleshooting Guide",
        "category": "troubleshooting",
    },
}


def load_documents():
    """Load Markdown files and attach their metadata."""
    documents = []

    for filename, metadata in DOCUMENT_METADATA.items():
        file_path = KNOWLEDGE_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Knowledge document not found: {file_path}"
            )

        content = file_path.read_text(encoding="utf-8").strip()

        if not content:
            raise ValueError(f"Knowledge document is empty: {filename}")

        documents.append(
            KnowledgeDocument(
                document_id=metadata["document_id"],
                title=metadata["title"],
                category=metadata["category"],
                source=filename,
                updated_at=date.today().isoformat(),
                content=content,
            )
        )

    return documents


def validate_documents(documents):
    """Check basic corpus quality before indexing."""
    if not documents:
        raise ValueError("The knowledge base contains no documents.")

    document_ids = [doc.document_id for doc in documents]

    if len(document_ids) != len(set(document_ids)):
        raise ValueError("Duplicate document IDs found.")

    for doc in documents:
        if not doc.content.strip():
            raise ValueError(f"Empty content in {doc.source}")

        if not doc.title.strip():
            raise ValueError(f"Missing title in {doc.source}")

    return True


if __name__ == "__main__":
    documents = load_documents()
    validate_documents(documents)

    print(f"Loaded and validated {len(documents)} documents.")

    for doc in documents:
        print(
            f"{doc.document_id} | {doc.category} | "
            f"{doc.title} | {len(doc.content)} characters"
        )

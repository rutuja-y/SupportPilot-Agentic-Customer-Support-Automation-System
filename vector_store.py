
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from chunking import chunk_text
from knowledge import load_documents, validate_documents


PROJECT_DIR = Path(__file__).resolve().parent
CHROMA_DIR = PROJECT_DIR / "chroma_db"
COLLECTION_NAME = "supportpilot_knowledge"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def build_vector_store():
    documents = load_documents()
    validate_documents(documents)

    model = SentenceTransformer(EMBEDDING_MODEL)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Rebuild this small demo collection from the current source documents.
    # This avoids stale chunks when the Markdown files change.
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    chunk_ids = []
    chunk_texts = []
    metadatas = []

    for document in documents:
        chunks = chunk_text(document.content)

        for index, chunk in enumerate(chunks):
            chunk_ids.append(f"{document.document_id}_chunk_{index}")
            chunk_texts.append(chunk)
            metadatas.append(
                {
                    "document_id": document.document_id,
                    "title": document.title,
                    "category": document.category,
                    "source": document.source,
                    "chunk_index": index,
                }
            )

    if not chunk_texts:
        raise ValueError("No chunks were produced from the knowledge base.")

    embeddings = model.encode(
        chunk_texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).tolist()

    collection.add(
        ids=chunk_ids,
        documents=chunk_texts,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    return len(chunk_ids)


def search_knowledge(query, top_k=3):
    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = client.get_collection(name=COLLECTION_NAME)
    model = SentenceTransformer(EMBEDDING_MODEL)

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    matches = []

    for index, text in enumerate(results["documents"][0]):
        matches.append(
            {
                "text": text,
                "metadata": results["metadatas"][0][index],
                "distance": results["distances"][0][index],
            }
        )

    return matches


if __name__ == "__main__":
    count = build_vector_store()
    print(f"Indexed {count} knowledge chunks.")

    query = "Can I return a product after delivery?"
    print(f"\nSearch query: {query}")

    for match in search_knowledge(query):
        print(f"\nSource: {match['metadata']['source']}")
        print(f"Distance: {match['distance']:.4f}")
        print(match["text"])

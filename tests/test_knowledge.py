
from knowledge import load_documents, validate_documents


def test_all_documents_load():
    documents = load_documents()

    assert len(documents) == 4


def test_document_metadata_is_present():
    documents = load_documents()

    for doc in documents:
        assert doc.document_id
        assert doc.title
        assert doc.category
        assert doc.source
        assert doc.updated_at
        assert doc.content


def test_document_ids_are_unique():
    documents = load_documents()

    ids = [doc.document_id for doc in documents]

    assert len(ids) == len(set(ids))


def test_corpus_validation_succeeds():
    documents = load_documents()

    assert validate_documents(documents) is True

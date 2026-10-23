
import pytest

from chunking import chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_short_text_returns_one_chunk():
    assert chunk_text("Shipping takes 3–5 business days.") == [
        "Shipping takes 3–5 business days."
    ]


def test_long_text_is_split():
    text = "A" * 1500
    chunks = chunk_text(text, chunk_size=500, overlap=50)

    assert len(chunks) > 1
    assert all(len(chunk) <= 500 for chunk in chunks)


def test_invalid_chunk_size_raises_error():
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=0)


def test_invalid_overlap_raises_error():
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=100, overlap=100)

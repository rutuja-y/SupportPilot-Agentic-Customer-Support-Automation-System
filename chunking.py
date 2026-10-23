
import re


def chunk_text(text, chunk_size=700, overlap=100):
    """
    Split text into overlapping character-based chunks.

    chunk_size: maximum approximate number of characters per chunk
    overlap: approximate characters shared between adjacent chunks
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size.")

    text = text.strip()
    if not text:
        return []

    # Preserve paragraphs while normalizing excess whitespace.
    paragraphs = [
        re.sub(r"\s+", " ", paragraph).strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]

    chunks = []
    current = ""

    for paragraph in paragraphs:
        # Split unusually long paragraphs into smaller pieces.
        while len(paragraph) > chunk_size:
            if current:
                chunks.append(current)
                current = ""

            chunks.append(paragraph[:chunk_size].strip())
            paragraph = paragraph[chunk_size - overlap :].strip()

        candidate = f"{current}\n{paragraph}".strip() if current else paragraph

        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)

            # Carry a small amount of context into the next chunk.
            prefix = chunks[-1][-overlap:] if chunks and overlap else ""
            current = f"{prefix}\n{paragraph}".strip() if prefix else paragraph

            # Avoid exceeding the size limit when overlap plus paragraph
            # would be too large.
            if len(current) > chunk_size:
                current = current[:chunk_size]

    if current:
        chunks.append(current)

    return [chunk for chunk in chunks if chunk]

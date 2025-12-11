# RAG-document-assistant/ingestion/chunker.py
"""
Text chunking utility for RAG ingestion.
Inputs: list of docs from load_docs.py
Output: list of chunks with metadata
"""

from typing import List, Dict

def chunk_text(
    text: str,
    max_tokens: int = 300,
    overlap: int = 50
) -> List[str]:
    """
    Simple whitespace-based chunking.
    Assumes ~1 token ≈ 4 chars (rough approximation).
    """
    approx_chars = max_tokens * 4
    approx_overlap = overlap * 4

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + approx_chars
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        # next window with overlap
        start = start + approx_chars - approx_overlap

    return chunks


def chunk_documents(docs: List[Dict], max_tokens: int = 300, overlap: int = 50):
    """
    docs = [{ filename, text, ... }]
    returns list of:
    {
      "filename": ...,
      "chunk_id": int,
      "text": ...,
      "chars": int
    }
    """
    all_chunks = []
    for d in docs:
        if d.get("status") != "OK":
            continue

        filename = d["filename"]
        text = d["text"]
        raw_chunks = chunk_text(text, max_tokens=max_tokens, overlap=overlap)

        for i, ch in enumerate(raw_chunks):
            all_chunks.append({
                "filename": filename,
                "chunk_id": i,
                "text": ch,
                "chars": len(ch)
            })
    return all_chunks


if __name__ == "__main__":
    # Minimal test
    sample = "This is a test text " * 200
    chunks = chunk_text(sample, max_tokens=50, overlap=10)
    print(f"Generated {len(chunks)} chunks")
    print(chunks[0])

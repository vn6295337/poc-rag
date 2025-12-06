# poc-rag/ingestion/cli_ingest.py
"""
CLI utility for testing ingestion pipeline.

Usage:
    python ingestion/cli_ingest.py <docs_dir>

Performs end-to-end ingestion test:
1. Loads markdown docs
2. Chunks them
3. Prints summary counts
"""

from load_docs import load_markdown_docs
from chunker import chunk_documents

import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python ingestion/cli_ingest.py <docs_dir>")
        sys.exit(1)

    docs_dir = sys.argv[1]
    docs = load_markdown_docs(docs_dir)

    chunks = chunk_documents(docs, max_tokens=300, overlap=50)

    total_docs = len([d for d in docs if d.get("status") == "OK"])
    total_chunks = len(chunks)

    print(f"Docs loaded: {total_docs}")
    print(f"Chunks generated: {total_chunks}")

    # Print a sample chunk for verification
    if chunks:
        print("\nSample chunk:")
        print(chunks[0]["text"][:300])

if __name__ == "__main__":
    main()

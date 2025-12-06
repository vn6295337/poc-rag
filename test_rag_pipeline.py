#!/usr/bin/env python3
"""Test the complete RAG pipeline locally"""

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.orchestrator import orchestrate_query
import json

def test_query(query_text):
    print("=" * 60)
    print(f"Testing RAG Pipeline: {query_text}")
    print("=" * 60)

    try:
        result = orchestrate_query(query_text, top_k=3)

        print("\n✅ ANSWER:")
        print("-" * 60)
        print(result.get("answer", "No answer generated"))

        print("\n📚 CITATIONS:")
        print("-" * 60)
        citations = result.get("citations", [])
        for i, c in enumerate(citations, 1):
            print(f"{i}. {c['id']} (Score: {c['score']:.4f})")

        print("\n📊 METADATA:")
        print("-" * 60)
        meta = result.get("meta", {})
        print(f"Provider: {meta.get('provider', 'N/A')}")
        print(f"Model: {meta.get('model', 'N/A')}")
        print(f"Elapsed: {meta.get('elapsed_s', 'N/A')}s")

        print("\n" + "=" * 60)
        return result

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Test with sample queries
    queries = [
        "what is GDPR",
        "how does data protection work",
        "what are privacy requirements"
    ]

    for query in queries:
        result = test_query(query)
        if result:
            print("\n✅ Pipeline test successful\n")
        else:
            print("\n❌ Pipeline test failed\n")
            sys.exit(1)
        print("\n" + "="*60 + "\n")

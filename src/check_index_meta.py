# poc-rag/src/check_index_meta.py
"""
Check Pinecone index metadata using pinecone>=5.x SDK.
Ensures dimension and metric match your ingestion pipeline.
"""

import os
import sys
from pinecone import Pinecone

# Add parent to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.config as cfg

def main():
    pc = Pinecone(api_key=cfg.PINECONE_API_KEY)

    index_name = cfg.PINECONE_INDEX_NAME
    idx = pc.Index(index_name)

    # Stats call provides useful metadata
    stats = idx.describe_index_stats()

    print("Index:", index_name)
    print("describe_index_stats():")
    print(stats)

if __name__ == "__main__":
    main()

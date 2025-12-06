"""
Core retrieval module for Pinecone vector search.

Functions:
- deterministic_embedding(text, dim): Generate deterministic pseudo-embeddings
- semantic_embedding(text, model_name): Generate semantic embeddings using sentence-transformers
- query_pinecone(query_text, top_k, index_name, use_semantic): Query Pinecone index
"""

import os
import hashlib
from typing import List, Dict, Any, Optional
from pinecone import Pinecone


# Default dimensions
DIM_DETERMINISTIC = 1024
DIM_SEMANTIC = 384  # for all-MiniLM-L6-v2

# Lazy-load sentence-transformers
_MODEL_CACHE = {}

def _get_sentence_transformer_model(model_name: str = "all-MiniLM-L6-v2"):
    """Lazy load and cache sentence transformer model."""
    if model_name not in _MODEL_CACHE:
        try:
            from sentence_transformers import SentenceTransformer
            _MODEL_CACHE[model_name] = SentenceTransformer(model_name)
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
    return _MODEL_CACHE[model_name]


def semantic_embedding(text: str, model_name: str = "all-MiniLM-L6-v2") -> List[float]:
    """
    Generate semantic embedding using sentence-transformers.

    Args:
        text: Input text to embed
        model_name: Name of sentence-transformers model (default: all-MiniLM-L6-v2)

    Returns:
        List of floats representing semantic embedding vector
    """
    model = _get_sentence_transformer_model(model_name)
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def deterministic_embedding(text: str, dim: int = DIM_DETERMINISTIC) -> List[float]:
    """
    Generate deterministic pseudo-embedding from text using SHA-256 hashing.

    This is NOT a semantic embedding - it's a consistent hash-based vector
    used for testing and development without external embedding API calls.

    Args:
        text: Input text to embed
        dim: Dimension of output vector (default: 1024)

    Returns:
        List of floats in range [-1, 1]
    """
    vec = []
    counter = 0

    while len(vec) < dim:
        h = hashlib.sha256((text + "|" + str(counter)).encode("utf-8")).digest()
        for i in range(0, len(h), 8):
            if len(vec) >= dim:
                break
            ull = int.from_bytes(h[i:i+8], "big", signed=False)
            f = (ull / (2**64 - 1)) * 2.0 - 1.0
            vec.append(float(f))
        counter += 1

    return vec[:dim]


def query_pinecone(
    query_text: str,
    top_k: int = 5,
    index_name: str = None,
    use_semantic: bool = True,
    model_name: str = "all-MiniLM-L6-v2"
) -> List[Dict[str, Any]]:
    """
    Query Pinecone index for similar chunks.

    Args:
        query_text: Query string to search for
        top_k: Number of results to return (default: 5)
        index_name: Pinecone index name (defaults to PINECONE_INDEX_NAME from config)
        use_semantic: Use semantic embeddings if True, deterministic if False (default: True)
        model_name: Model name for semantic embeddings (default: all-MiniLM-L6-v2)

    Returns:
        List of dicts with keys: id, score, metadata

    Raises:
        RuntimeError: If index_name not provided and PINECONE_INDEX_NAME not set
    """
    # Get index name from config if not provided
    if index_name is None:
        import src.config as cfg
        index_name = getattr(cfg, 'PINECONE_INDEX_NAME', None)
        if not index_name:
            raise RuntimeError(
                "index_name not provided and PINECONE_INDEX_NAME not set in config"
            )

    # Initialize Pinecone client
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        raise RuntimeError("PINECONE_API_KEY environment variable not set")

    pc = Pinecone(api_key=api_key)

    # Get index host
    idx_meta = pc.describe_index(index_name)
    host = getattr(idx_meta, "host", None) or (
        idx_meta.get("host") if isinstance(idx_meta, dict) else None
    )
    if not host:
        raise RuntimeError(f"Cannot determine host for index: {index_name}")

    # Connect to index
    index = pc.Index(host=host)

    # Generate query embedding
    if use_semantic:
        q_emb = semantic_embedding(query_text, model_name=model_name)
    else:
        q_emb = deterministic_embedding(query_text)

    # Query index
    res = index.query(
        vector=q_emb,
        top_k=top_k,
        include_metadata=True,
        include_values=False
    )

    # Normalize response format
    out = []
    matches = getattr(res, "matches", None) or res.get("matches", [])

    for m in matches:
        mid = getattr(m, "id", None) or m.get("id")
        score = getattr(m, "score", None) or m.get("score")
        meta = getattr(m, "metadata", None) or m.get("metadata", {})

        out.append({
            "id": mid,
            "score": score,
            "metadata": meta
        })

    return out

# poc-rag/ingestion/embeddings.py
"""
Simple embedding-function stub for Day-3.
- Supports provider names: "openai", "claude", "local"
- When provider == "local", returns deterministic pseudo-embeddings (no network).
- Exposes batch_embed_chunks(chunks, provider="local") -> list of dicts with 'chunk', 'embedding' (list[float])
"""

import hashlib
import struct
from typing import List, Dict

def _pseudo_vector_from_text(text: str, dim: int = 128) -> List[float]:
    """
    Deterministic pseudo-embedding: hash the text and expand into floats.
    Not a real embedding — used for pipeline testing.
    """
    h = hashlib.sha256(text.encode("utf-8")).digest()
    vec = []
    # expand by repeating hash bytes to reach dim; convert to float in [0,1)
    i = 0
    while len(vec) < dim:
        # take 4 bytes -> float
        chunk = h[i % len(h):(i % len(h)) + 4]
        if len(chunk) < 4:
            chunk = chunk.ljust(4, b"\0")
        val = struct.unpack("I", chunk)[0] / 2**32
        vec.append(float(val))
        i += 4
    return vec[:dim]

def get_embedding(text: str, provider: str = "local", dim: int = 128) -> List[float]:
    """
    Provider-agnostic embedding getter.
    - provider "local": returns pseudo-embedding
    - provider "openai" / "claude": raises NotImplementedError (placeholder)
    """
    provider = provider.lower()
    if provider == "local":
        return _pseudo_vector_from_text(text, dim=dim)
    elif provider in ("openai", "claude"):
        raise NotImplementedError(f"Provider '{provider}' is not configured in this stub.")
    else:
        raise ValueError(f"Unknown provider: {provider}")

def batch_embed_chunks(chunks: List[Dict], provider: str = "local", dim: int = 128) -> List[Dict]:
    """
    Input: chunks = [{"filename","chunk_id","text","chars"}...]
    Output: [{"filename","chunk_id","embedding","chars"}...]
    """
    out = []
    for c in chunks:
        emb = get_embedding(c["text"], provider=provider, dim=dim)
        out.append({
            "filename": c["filename"],
            "chunk_id": c["chunk_id"],
            "embedding": emb,
            "chars": c["chars"]
        })
    return out

if __name__ == "__main__":
    # Quick local smoke test
    sample_text = "This is a test document for embedding."
    v = get_embedding(sample_text, provider="local", dim=16)
    print("Embedding length:", len(v))
    print(v[:4])

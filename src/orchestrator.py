# src/orchestrator.py
from typing import List, Dict, Any
import re
import src.config as cfg
from src.ingestion.embeddings import get_embedding  # provider-agnostic embedding fn used for ingestion
from src.retrieval.retriever import query_pinecone as pinecone_search, deterministic_embedding

# -------------------------
# Citation snippet enrichment
# -------------------------
import json
from pathlib import Path as _Path

def _enrich_citations_with_snippets(result: dict, chunk_map: dict):
    """
    Mutates `result` in-place: for each citation where snippet is empty,
    set snippet to chunk_map[citation.id] if available.
    """
    if not isinstance(result, dict):
        return result
    for c in result.get("citations", []) + result.get("sources", []):
        if not isinstance(c, dict):
            continue
        if not c.get("snippet"):
            s = chunk_map.get(c.get("id"), "")
            if s:
                c["snippet"] = s
    return result

def _load_chunks_map(path: str = "data/chunks.jsonl") -> dict:
    """
    Load chunks map from JSONL file for citation enrichment.
    
    Args:
        path: Path to JSONL file containing chunk data
        
    Returns:
        Dictionary mapping chunk IDs to text content
    """
    m = {}
    pth = _Path(path)
    if not pth.exists():
        return m
        
    try:
        with pth.open("r", encoding="utf-8") as fh:
            for line_num, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    # Skip malformed JSON lines
                    continue
                    
                cid = obj.get("id") or obj.get("chunk_id") or None
                if not cid and "filename" in obj and "chunk_id" in obj:
                    cid = f"{obj['filename']}::{obj['chunk_id']}"
                text = obj.get("text") or obj.get("chunk") or obj.get("content") or ""
                if cid:
                    m[str(cid)] = text
    except Exception as e:
        # Don't fail if chunks file can't be loaded
        pass
        
    return m

_CHUNKS_MAP = _load_chunks_map()



import json
from pathlib import Path as _Path




# Try to import a provider wrapper; if missing, use a local deterministic fallback for offline tests.
try:
    from src.llm_providers import call_llm  # thin wrapper that chooses Gemini/Groq/OpenRouter per config
except Exception:
    def call_llm(prompt: str, temperature: float = 0.0, max_tokens: int = 512, **kwargs):
        """
        Simple deterministic offline responder: return prompt summary-like text and meta.
        
        Args:
            prompt: Prompt text
            temperature: Sampling temperature (ignored in fallback)
            max_tokens: Maximum tokens (ignored in fallback)
            **kwargs: Additional arguments (ignored in fallback)
            
        Returns:
            Dict with 'text' and 'meta' keys
        """
        # Simple deterministic offline responder: return prompt summary-like text and meta.
        summary = prompt.strip().split('\n')[-1] if prompt.strip() else "No prompt provided"
        resp_text = f"[offline-llm] Answer based on provided context: {summary}" 
        return {"text": resp_text, "meta": {"provider": "local-fallback", "temperature": temperature}}


PROMPT_TEMPLATE = """
You are given a user query and a set of context chunks. Use the context to answer concisely.
Provide a short answer and list the ids of chunks used as citations.

User query:
{query}

Context chunks (top {k} by score):
{context}

Answer:
"""

def _build_context(chunks: List[Dict[str, Any]]) -> str:
    """
    Build context string from retrieved chunks for LLM prompt.
    
    Args:
        chunks: List of chunk dictionaries with id, score, metadata, and text
        
    Returns:
        Formatted context string
    """
    lines = []
    for c in chunks:
        # Safely extract text, defaulting to empty string if not found
        text_content = c.get("text", "") if isinstance(c, dict) else ""
        snippet = text_content[:800].replace("\n", " ") if text_content else ""
        
        # Safely extract metadata
        meta = c.get("metadata", {}) if isinstance(c, dict) else {}
        
        # Extract ID safely
        chunk_id = c.get("id", "unknown") if isinstance(c, dict) else "unknown"
        
        # Extract score safely
        score_val = c.get("score", 0.0) if isinstance(c, dict) else 0.0
        
        lines.append(f"ID:{chunk_id} SCORE:{score_val:.4f} META:{meta}\n{snippet}")
    return "\n\n".join(lines)

def _extract_cited_ids_from_llm(text: str) -> List[str]:
    """
    Extract cited chunk IDs from LLM response text.
    
    Args:
        text: LLM response text
        
    Returns:
        List of cited chunk IDs
    """
    if not text or not isinstance(text, str):
        return []
        
    # find tokens like ID:some-id or ID:some-file::123
    ids = re.findall(r"ID:([A-Za-z0-9_\-:.]+)", text)
    return ids


def orchestrate_query(query: str, top_k: int = 3, llm_params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Orchestrate the full RAG query pipeline: retrieval → LLM generation → citation assembly.
    
    Args:
        query: User query string
        top_k: Number of top chunks to retrieve
        llm_params: Parameters for LLM call (temperature, max_tokens, etc.)
        
    Returns:
        Dict with answer, sources, citations, and metadata
        
    Raises:
        Exception: If any step in the pipeline fails
    """
    if not query or not isinstance(query, str):
        return {"answer": "", "sources": [], "citations": [], "llm_meta": {"error": "invalid_query"}}
        
    if llm_params is None:
        llm_params = {"temperature": 0.0, "max_tokens": 512}
        
    # Validate top_k
    if not isinstance(top_k, int) or top_k <= 0:
        top_k = 3

    # 1) retrieve top_k chunks from vector DB using the repo's deterministic embedding/query wrapper
    try:
        chunks = pinecone_search(query, top_k=top_k)
    except Exception as e:
        return {"answer": "", "sources": [], "citations": [], "llm_meta": {"error": f"retrieval_failed: {str(e)}"}}
        
    if not chunks:
        return {"answer": "", "sources": [], "citations": [], "llm_meta": {"error": "no_retrieval_results"}}

    # 2) build prompt
    context = _build_context(chunks)
    prompt = PROMPT_TEMPLATE.format(query=query, k=top_k, context=context)

    # 3) call LLM via unified provider wrapper
    try:
        llm_resp = call_llm(prompt=prompt, **llm_params)
    except Exception as e:
        return {"answer": "", "sources": [], "citations": [], "llm_meta": {"error": f"llm_call_failed: {str(e)}"}}

    # 4) build sources (ensure snippet comes from chunk text or fallback to local chunks map)
    sources: List[Dict[str, Any]] = []
    for c in chunks:
        # prefer chunk text from retrieval result; fallback to local chunk map
        text_from_chunk = c.get("text") or "" if isinstance(c, dict) else ""
        if not text_from_chunk:
            text_from_chunk = _CHUNKS_MAP.get(str(c.get("id"))) or _CHUNKS_MAP.get(str(c.get("chunk_id")), "") if isinstance(c, dict) else ""
        snippet = (text_from_chunk or "")[:400]
        sources.append({
            "id": c.get("id") if isinstance(c, dict) else None,
            "score": float(c.get("score", 0.0)) if isinstance(c, dict) else 0.0,
            "snippet": snippet
        })

    # 5) Build citations: prefer explicit IDs listed by LLM, else fallback to top sources
    cited_ids = _extract_cited_ids_from_llm(llm_resp.get("text", ""))
    citations: List[Dict[str, Any]] = []
    if cited_ids:
        id_map = {s["id"]: s for s in sources if s["id"]}
        for cid in cited_ids:
            if cid in id_map:
                citations.append(id_map[cid])
    if not citations:
        citations = sources

    # 6) assemble result dict, then enrich citation snippets in-place (best-effort)
    result = {
        "answer": llm_resp.get("text", "").strip() if isinstance(llm_resp, dict) else "",
        "sources": sources,
        "citations": citations,
        "llm_meta": llm_resp.get("meta", {}) if isinstance(llm_resp, dict) else {}
    }

    # Best-effort: enrich any empty snippets from the canonical _CHUNKS_MAP
    try:
        _enrich_citations_with_snippets(result, _CHUNKS_MAP)
    except Exception:
        # don't fail the whole call if enrichment breaks
        pass

    return result
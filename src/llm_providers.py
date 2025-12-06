
# src/llm_providers.py
# Priority: GEMINI → GROQ → OPENROUTER → fallback

import os
import json
import time
from typing import Optional, Dict, Any

try:
    import requests
    _HAS_REQUESTS = True
except Exception:
    import urllib.request as _urllib_request
    import urllib.error as _urllib_error
    _HAS_REQUESTS = False


def _http_post(url: str, headers: dict, payload: dict, timeout: int = 30):
    data = json.dumps(payload).encode("utf-8")
    if _HAS_REQUESTS:
        r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=timeout)
        r.raise_for_status()
        return r.json()
    else:
        req = _urllib_request.Request(url, data=data, headers=headers, method="POST")
        with _urllib_request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))


# GEMINI ------------------------------------------------------------

def _call_gemini(prompt: str, temperature: float, max_tokens: int, context: Optional[str]):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY missing")

    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    content = prompt
    if context:
        content = f"Context:\n{context}\n\nUser question:\n{prompt}"

    payload = {
        "contents": [{"parts": [{"text": content}]}],
        "generationConfig": {
            "temperature": float(temperature),
            "maxOutputTokens": int(max_tokens)
        }
    }

    start = time.time()
    j = _http_post(url, {"Content-Type": "application/json"}, payload)
    elapsed = time.time() - start

    try:
        text = j["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        text = json.dumps(j)[:1000]

    return {"text": text, "meta": {"provider": "gemini", "model": model, "elapsed_s": elapsed}}


# GROQ --------------------------------------------------------------

def _call_groq(prompt: str, temperature: float, max_tokens: int, context: Optional[str]):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY missing")

    url = "https://api.groq.com/openai/v1/chat/completions"
    model = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")

    system_msg = "You are a concise assistant. Include citations if context is provided."
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"Context:\n{context}\n\n{prompt}" if context else prompt}
    ]

    payload = {
        "model": model,
        "messages": messages,
        "temperature": float(temperature),
        "max_tokens": int(max_tokens)
    }

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    start = time.time()
    j = _http_post(url, headers, payload)
    elapsed = time.time() - start

    try:
        text = j["choices"][0]["message"]["content"]
    except Exception:
        text = json.dumps(j)[:1000]

    return {"text": text, "meta": {"provider": "groq", "model": model, "elapsed_s": elapsed}}


# OPENROUTER --------------------------------------------------------

def _call_openrouter(prompt: str, temperature: float, max_tokens: int, context: Optional[str]):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY missing")

    url = os.getenv("OPENROUTER_URL", "https://api.openrouter.ai/v1/chat/completions")
    model = os.getenv("OPENROUTER_MODEL", "gpt-4o-mini")

    system_msg = "You are a concise assistant. Use supplied context."

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"Context:\n{context}\n\n{prompt}" if context else prompt}
    ]

    payload = {
        "model": model,
        "messages": messages,
        "temperature": float(temperature),
        "max_tokens": int(max_tokens)
    }

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    start = time.time()
    j = _http_post(url, headers, payload)
    elapsed = time.time() - start

    try:
        text = j["choices"][0]["message"]["content"]
    except Exception:
        text = json.dumps(j)[:1000]

    return {"text": text, "meta": {"provider": "openrouter", "model": model, "elapsed_s": elapsed}}


# FALLBACK ----------------------------------------------------------

def _fallback(prompt: str, context: Optional[str]):
    ctx = (context or "")[:800]
    text = f"[offline] {prompt}\n\nContext snippet:\n{ctx}"
    return {"text": text, "meta": {"provider": "local-fallback"}}


# PUBLIC ENTRYPOINT -------------------------------------------------

def call_llm(prompt: str, temperature: float = 0.0, max_tokens: int = 512, context: Optional[str] = None, **kwargs):
    """
    Call LLM with automatic fallback cascade: Gemini → Groq → OpenRouter → Local.
    If one provider fails, automatically tries the next one.
    """
    errors = []

    # Try Gemini first
    if os.getenv("GEMINI_API_KEY"):
        try:
            return _call_gemini(prompt, temperature, max_tokens, context)
        except Exception as e:
            errors.append(f"gemini: {e}")
            # Continue to next provider

    # Try Groq second
    if os.getenv("GROQ_API_KEY"):
        try:
            return _call_groq(prompt, temperature, max_tokens, context)
        except Exception as e:
            errors.append(f"groq: {e}")
            # Continue to next provider

    # Try OpenRouter third
    if os.getenv("OPENROUTER_API_KEY"):
        try:
            return _call_openrouter(prompt, temperature, max_tokens, context)
        except Exception as e:
            errors.append(f"openrouter: {e}")
            # Continue to fallback

    # All providers failed, use local fallback
    error_summary = "; ".join(errors) if errors else "No API keys configured"
    return {
        "text": f"[All providers failed: {error_summary}] Using local fallback.",
        "meta": {"provider": "local-fallback", "errors": errors}
    }

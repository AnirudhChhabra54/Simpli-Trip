# backend/services/lmstudio_service.py
import os, time, requests
from typing import Any, Dict, Optional

LM_HOST = os.getenv("LMSTUDIO_HOST", "http://127.0.0.1:1234/v1").rstrip("/")
LM_MODEL = os.getenv("LMSTUDIO_MODEL", "openai/gpt-oss-20b")
LM_TIMEOUT = int(os.getenv("LMSTUDIO_TIMEOUT", "30"))
LM_RETRIES = int(os.getenv("LMSTUDIO_RETRIES", "2"))
LM_BACKOFF = float(os.getenv("LMSTUDIO_BACKOFF", "1.0"))
LM_API_KEY = os.getenv("LMSTUDIO_API_KEY", "") or None

HEADERS = {"Content-Type": "application/json"}
if LM_API_KEY:
    HEADERS["Authorization"] = f"Bearer {LM_API_KEY}"

def _post(path: str, payload: Dict[str, Any], timeout: int = LM_TIMEOUT):
    url = f"{LM_HOST}{path}"
    last_exc = None
    for attempt in range(LM_RETRIES + 1):
        try:
            r = requests.post(url, json=payload, headers=HEADERS, timeout=timeout)
            r.raise_for_status()
            try:
                return r.json()
            except Exception:
                return {"raw_text": r.text}
        except Exception as e:
            last_exc = e
            if attempt < LM_RETRIES:
                time.sleep(LM_BACKOFF * (1 + attempt))
                continue
            raise last_exc

def generate(prompt: str, max_tokens: int = 512, temperature: float = 0.7, top_p: Optional[float] = None, stop: Optional[list] = None) -> Dict[str, Any]:
    payload = {
        "model": LM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful travel assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    if top_p is not None:
        payload["top_p"] = top_p
    if stop is not None:
        payload["stop"] = stop

    # Try chat completions (OpenAI-style)
    try:
        res = _post("/chat/completions", payload)
        text = ""
        if isinstance(res, dict) and "choices" in res and res["choices"]:
            first = res["choices"][0]
            if isinstance(first, dict):
                text = (first.get("message") or {}).get("content") or first.get("text") or ""
            elif isinstance(first, str):
                text = first
        if text:
            return {"text": text, "raw": res}
    except Exception:
        pass

    # Fallback to completions
    try:
        res = _post("/completions", {"model": LM_MODEL, "prompt": prompt, "max_tokens": max_tokens, "temperature": temperature})
        text = ""
        if isinstance(res, dict) and "choices" in res and res["choices"]:
            first = res["choices"][0]
            text = first.get("text", "") if isinstance(first, dict) else str(first)
        if text:
            return {"text": text, "raw": res}
    except Exception:
        pass

    return {"text": "", "raw": {"error": "no-endpoint-responded"}}

def is_available() -> bool:
    try:
        r = requests.get(f"{LM_HOST}/models", headers=HEADERS, timeout=2)
        if r.status_code == 200:
            return True
        r2 = requests.get(LM_HOST, headers=HEADERS, timeout=2)
        return r2.status_code in (200,302,404)
    except Exception:
        return False

def health() -> Dict[str, Any]:
    return {"provider":"lmstudio","host":LM_HOST,"model":LM_MODEL,"available": is_available()}

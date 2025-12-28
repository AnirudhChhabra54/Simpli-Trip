# backend/services/lmstudio_service.py
"""
Upgraded LM Studio adapter for SimpliTrip.
- Uses the OpenAI-compatible /v1/chat/completions endpoint.
- Provides `generate` and a new `chat` method for multi-turn conversations.
"""

import os
import time
import requests
from typing import Any, Dict, List, Optional, Union

# Read settings from environment variables
LM_HOST = os.getenv("LMSTUDIO_HOST", "http://localhost:1234")  # ← Base URL without /v1
LM_MODEL = os.getenv("LMSTUDIO_MODEL", "openai/gpt-oss-20b")
LM_TIMEOUT = int(os.getenv("LMSTUDIO_TIMEOUT", "45"))
LM_RETRIES = int(os.getenv("LMSTUDIO_RETRIES", "1"))
LM_BACKOFF = float(os.getenv("LMSTUDIO_BACKOFF", "1.5"))
LM_API_KEY = os.getenv("LMSTUDIO_API_KEY", "lm-studio") # LM Studio default

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {LM_API_KEY}",
}

def _request_json(path: str, payload: Dict[str, Any], timeout: int = LM_TIMEOUT) -> Dict[str, Any]:
    """Reusable request handler with retries."""
    # Build URL: if LM_HOST already ends with /v1, use it; otherwise add /v1
    host = LM_HOST.rstrip('/')
    if not host.endswith('/v1'):
        host = f"{host}/v1"
    url = f"{host}{path}"
    
    last_exc = None
    for attempt in range(LM_RETRIES + 1):
        try:
            resp = requests.post(url, json=payload, headers=HEADERS, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            last_exc = e
            print(f"LM Studio request failed (attempt {attempt + 1}/{LM_RETRIES + 1}): {e}")
            if attempt < LM_RETRIES:
                time.sleep(LM_BACKOFF * (1 + attempt))
    raise last_exc

def chat(
    messages: List[Dict[str, str]],
    max_tokens: int = 1024,
    temperature: float = 0.7,
    top_p: Optional[float] = None,
    stop: Optional[Union[str, List[str]]] = None,
) -> Dict[str, Any]:
    """
    Send a list of messages to the /v1/chat/completions endpoint.

    Args:
        messages: A list of message dictionaries, e.g., [{"role": "system", "content": "You are a helpful assistant."}]

    Returns:
        A dictionary containing the response text and raw API output.
        e.g., {'text': '...', 'raw': {...}}
    """
    payload = {
        "model": LM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if top_p is not None:
        payload["top_p"] = top_p
    if stop is not None:
        payload["stop"] = stop

    # Make the request to the chat completions endpoint
    result = _request_json("/chat/completions", payload)

    # Extract the response text
    text = ""
    if result and "choices" in result and result["choices"]:
        choice = result["choices"][0]
        if "message" in choice and "content" in choice["message"]:
            text = choice["message"]["content"]
    
    return {"text": text.strip(), "raw": result}


def generate(
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
    top_p: Optional[float] = None,
    stop: Optional[Union[str, List[str]]] = None,
) -> str:
    """
    A simplified wrapper around `chat` for single-prompt generation.
    Returns only the generated text string.
    """
    messages = [{"role": "user", "content": prompt}]
    response = chat(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        stop=stop,
    )
    return response["text"]


def is_available() -> bool:
    """Check if the LM Studio server is reachable and has models."""
    try:
        # The /v1/models endpoint is standard for OpenAI-compatible servers
        url = f"{LM_HOST.rstrip('/')}/v1/models"
        resp = requests.get(url, headers=HEADERS, timeout=5)
        return resp.status_code == 200 and "data" in resp.json()
    except requests.exceptions.RequestException:
        return False


def health() -> Dict[str, Any]:
    """Return a health check dictionary."""
    avail = is_available()
    return {
        "provider": "lmstudio",
        "host": LM_HOST,
        "model": LM_MODEL,
        "available": avail,
    }

# Make the chat function easily importable
lmstudio_service = {
    "chat": chat,
    "generate": generate,
    "is_available": is_available,
    "health": health,
}

"""
Ollama adapter for SimpliTrip.

Keeps a stable import surface for modules (like data_enrichment_service) that
reference `services.ollama_service`. The backend primarily uses LM Studio, so
Ollama is treated as an optional, best-effort provider that degrades gracefully.
"""
import os
import json
import logging
from typing import Any, Dict, List

from utils.logger import logger

try:
    import requests
except Exception:  # pragma: no cover
    requests = None  # type: ignore

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "30"))


class _OllamaService:
    def __init__(self):
        self.host = OLLAMA_HOST
        self.model = OLLAMA_MODEL

    def is_available(self) -> bool:
        if requests is None:
            return False
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=2)
            return resp.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, system: str = "", max_tokens: int = 200, temperature: float = 0.7) -> str:
        """Return raw generated text (mirrors LM Studio `generate` interface)."""
        if requests is None or not self.is_available():
            return ""
        try:
            payload: Dict[str, Any] = {
                "model": self.model,
                "prompt": prompt,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            }
            if system:
                payload["system"] = system
            resp = requests.post(f"{self.host}/api/generate", json=payload, timeout=OLLAMA_TIMEOUT)
            resp.raise_for_status()
            parts = []
            for line in resp.text.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    parts.append(json.loads(line).get("response", ""))
                except Exception:
                    continue
            return "".join(parts).strip()
        except Exception as e:
            logger.error("Ollama generate error: %s", e)
            return ""

    def models(self) -> List[str]:
        if requests is None or not self.is_available():
            return []
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            return []

    def health(self) -> Dict[str, Any]:
        return {"provider": "ollama", "host": self.host, "model": self.model, "available": self.is_available()}


ollama_service = _OllamaService()
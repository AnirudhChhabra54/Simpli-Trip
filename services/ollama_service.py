# backend/services/ollama_service.py
# Minimal stub for Ollama adapter so imports don't crash when Ollama is not used.
# This file makes the rest of the codebase believe "Ollama" exists but is unavailable.
import logging
from typing import Any, Dict

logger = logging.getLogger("simplitrip")

class _StubOllamaService:
    def __init__(self):
        self.name = "ollama-stub"
        self.available = False

    def is_available(self) -> bool:
        """Return False — real Ollama not configured."""
        return False

    def generate(self, *args, **kwargs) -> Dict[str, Any]:
        """Return a safe empty response structure the rest of the code expects."""
        return {"text": "", "raw": {"error": "ollama-not-configured"}, "ok": False}

    def models(self):
        """Return empty list of models."""
        return []

    def health(self) -> Dict[str, Any]:
        return {"provider": "ollama", "available": False}

# single instance used elsewhere: from .ollama_service import ollama_service
ollama_service = _StubOllamaService()
logger.info("Ollama stub service loaded — Ollama not configured locally.")

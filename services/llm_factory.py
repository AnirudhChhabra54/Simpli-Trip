# backend/services/llm_factory.py
import os
provider = os.getenv("LLM_PROVIDER", "lmstudio").lower()
if provider == "lmstudio":
    from .lmstudio_service import generate, is_available, health
else:
    # keep ollama import commented for now
    # from .ollama_service import generate, is_available, health
    from .lmstudio_service import generate, is_available, health

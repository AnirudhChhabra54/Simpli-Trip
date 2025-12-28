# services/prompt_builder.py
"""
Prompt builder for RAG -> LLM pipeline.
Creates a compact prompt with constraints and retrieved facts (citations).
"""

from typing import List, Dict, Any

DEFAULT_MAX_CHARS = 4000


def build_prompt(user_constraints: Dict[str, Any], retrieved: List[Dict], max_chars: int = DEFAULT_MAX_CHARS) -> str:
    header = "You are SimpliTrip — an expert Indian travel planner. Use ONLY the facts from the 'RETRIEVED FACTS' section below.\n\n"
    constraints_lines = []
    for k in ("destination", "duration_days", "travelers", "budget", "meal_pref"):
        v = user_constraints.get(k)
        if v is not None:
            constraints_lines.append(f"- {k.replace('_',' ').capitalize()}: {v}")
    constraints = "USER CONSTRAINTS:\n" + ("\n".join(constraints_lines) if constraints_lines else " - none\n") + "\n\n"

    items = []
    total_chars = len(header) + len(constraints)
    for i, r in enumerate(retrieved, 1):
        meta = r.get("meta", {}) or {}
        id_ = meta.get("source_id") or meta.get("id") or f"doc_{i}"
        text = (r.get("text") or "").replace("\n", " ").strip()
        snippet = text[:400]
        item = f"[{i}] {id_} — {snippet}"
        if total_chars + len(item) > max_chars:
            break
        items.append(item)
        total_chars += len(item)
    retrieved_block = "RETRIEVED FACTS:\n" + ("\n\n".join(items) + "\n\n" if items else "")

    instr = (
        "INSTRUCTIONS:\n"
        "Generate a day-by-day itinerary respecting the constraints. For each day list morning/afternoon/evening activities, estimated travel times, and estimated costs (if available). Cite sources using the bracketed numbers from retrieved facts, e.g., [1], [2]. If information is missing, say 'information not available.'\n\n"
        "OUTPUT FORMAT:\n"
        "Return a JSON object with keys: daily_plan (array of days with activities and costs), total_estimated_cost (INR or 'unknown'), sources (list of used doc ids), and markdown (a readable markdown itinerary).\n\n"
    )
    prompt = header + constraints + retrieved_block + instr
    return prompt

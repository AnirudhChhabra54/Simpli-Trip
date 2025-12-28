# services/ranker.py
"""
Simple constraint-aware candidate ranking for RAG candidates.
"""

from typing import Dict, Any, List


def _semantic_from_distance(dist: float) -> float:
    """Convert Chroma distance (lower better) to similarity in [0,1]."""
    try:
        d = float(dist)
        return 1.0 / (1.0 + d)
    except Exception:
        return 0.0


def budget_score(avg_cost_per_person: float, user_budget_total: float, travelers: int) -> float:
    """Score budget fit: 1.0 = fits comfortably, 0 = way over budget."""
    if not user_budget_total or not travelers:
        return 0.5
    per_person_budget = user_budget_total / max(1, travelers)
    if avg_cost_per_person <= per_person_budget:
        return 1.0
    diff = (avg_cost_per_person - per_person_budget) / max(1, per_person_budget)
    return max(0.0, 1.0 - diff)


def travel_time_score(minutes: float) -> float:
    """Penalize very long travel times (minutes)."""
    try:
        if minutes is None:
            return 0.5
        minutes = float(minutes)
        if minutes <= 30:
            return 1.0
        if minutes >= 240:
            return 0.0
        return max(0.0, 1 - (minutes - 30) / (240 - 30))
    except Exception:
        return 0.5


def rank_candidates(candidates: List[Dict], user_constraints: Dict, top_k: int = 6) -> List[Dict]:
    """
    Score and select top_k candidates.

    candidates: list of dicts with keys 'text','meta','distance'
    user_constraints: {'budget','travelers','duration_days'}
    """
    scored = []
    for c in candidates:
        dist = c.get("distance")
        sim = _semantic_from_distance(dist) if dist is not None else 0.5
        meta = c.get("meta", {}) or {}
        pop = float(meta.get("popularity", 0)) / 5.0 if meta.get("popularity") else 0.5

        # avg cost per person
        avg_cost = 0.0
        acr = meta.get("avg_cost_range")
        if isinstance(acr, dict):
            avg_cost = (acr.get("min", 0) + acr.get("max", 0)) / 2.0
        else:
            try:
                avg_cost = float(meta.get("avg_cost_per_person", 0) or 0)
            except Exception:
                avg_cost = 0.0

        bscore = budget_score(avg_cost, user_constraints.get("budget") or 0, user_constraints.get("travelers") or 1)
        tt = meta.get("travel_time_from_city_center_mins") or meta.get("travel_time_mins") or 60
        tscore = travel_time_score(tt)

        score = 0.6 * sim + 0.2 * pop + 0.15 * bscore + 0.05 * tscore
        scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for (_, c) in scored[:top_k]]

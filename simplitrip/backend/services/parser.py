# services/parser.py
"""
Simple rule-based parser to extract structured trip constraints from free text.
Improved to distinguish between 'days' and 'travelers' and handle 'k' notation.
"""
import re
from typing import Optional, Dict, Any, List

def _norm_int(s: str) -> int:
    """Normalize number strings, handling 'k' (e.g. 50k -> 50000)"""
    if not s: 
        return 0
    s = s.lower().replace(",", "").replace(" ", "")
    
    # Handle 50k / 1.5k notation
    if 'k' in s:
        try:
            val = float(s.replace('k', ''))
            return int(val * 1000)
        except ValueError:
            return 0
            
    try:
        return int(float(s))
    except ValueError:
        return 0


def parse_user_input(text: str, known_cities: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Parse user free-text travel request into structured fields.
    """
    text = (text or "").strip()
    out: Dict[str, Any] = {
        "raw": text,
        "destination": None,
        "duration_days": None,
        "travelers": 1,  # Default to 1 (safe fallback)
        "budget": None,
        "meal_pref": None,
        "categories": [],
        "confidence": 0.0
    }

    if not text:
        return out

    # 1. Duration (Explicitly look for 'day', 'days', 'night', 'nights')
    # Matches: "3 days", "3-4 days", "a week" (mapped manually if needed, but keeping simple)
    dur_m = re.search(r"(\d+)(?:-\d+)?\s*(?:day|night)", text, re.I)
    if dur_m:
        out["duration_days"] = _norm_int(dur_m.group(1))
        out["confidence"] = max(out["confidence"], 0.6)

    # 2. Travelers (Keywords are MANDATORY to avoid mixing up with days)
    # Matches: "3 people", "2 travelers", "5 pax"
    trav_m = re.search(r"(\d+)\s*(?:people|person|pax|traveller|traveler|friend|guest)", text, re.I)
    if trav_m:
        out["travelers"] = _norm_int(trav_m.group(1))
        out["confidence"] = max(out["confidence"], 0.7)
    
    # Semantic matches for travelers
    elif re.search(r"\b(couple|two)\b", text, re.I):
        out["travelers"] = 2
        out["confidence"] = max(out["confidence"], 0.6)
    elif re.search(r"\b(solo|alone)\b", text, re.I):
        out["travelers"] = 1
        out["confidence"] = max(out["confidence"], 0.6)
    elif re.search(r"\b(family)\b", text, re.I):
        out["travelers"] = 4 # Reasonable default
        out["confidence"] = max(out["confidence"], 0.5)

    # 3. Budget (Handle 'rs', 'inr', 'rupees', '$', and 'k')
    # Matches: "50000", "50k", "50k rupees", "under 20000"
    bud_m = re.search(r"(?:rs\.?|inr|₹|rupees|\$)\s*([\d,.]+[kK]?)", text, re.I)
    if not bud_m:
        # Try finding number followed by currency
        bud_m = re.search(r"([\d,.]+[kK]?)\s*(?:rs\.?|inr|₹|rupees)", text, re.I)
    
    if bud_m:
        out["budget"] = _norm_int(bud_m.group(1))
        out["confidence"] = max(out["confidence"], 0.8)

    # 4. Destination (Remove common verbs)
    # Heuristic: Look for Proper Noun after 'to', 'in', 'visit'
    dest_m = re.search(r"(?:to|in|visit|at)\s+([A-Z][a-zA-Z]+(?:[\s-][A-Z][a-zA-Z]+)*)", text)
    if dest_m:
        cand = dest_m.group(1).strip()
        # Filter out common false positives
        if cand.lower() not in ['goa', 'india', 'bali', 'dubai', 'europe'] and len(cand) < 3:
            pass # Ignore very short garbage
        else:
            out["destination"] = cand
            out["confidence"] = max(out["confidence"], 0.7)

    # 5. Meal preference
    if re.search(r"\b(non-?veg|nonveg|non veg)\b", text, re.I):
        out["meal_pref"] = "non-veg"
    elif re.search(r"\b(veg|vegetarian)\b", text, re.I):
        out["meal_pref"] = "veg"
    elif re.search(r"\b(vegan)\b", text, re.I):
        out["meal_pref"] = "vegan"

    # 6. Category keywords
    cats = []
    # Extended keyword list
    keywords = ["beach", "mountain", "histor", "adventur", "wildlife", "culture", "relax", 
                "spiritual", "food", "shopping", "nature", "hill station", "snow"]
    
    for cat in keywords:
        if re.search(rf"\b{cat}\w*\b", text, re.I):
            clean_cat = cat
            if cat == "histor": clean_cat = "historical"
            if cat == "adventur": clean_cat = "adventure"
            cats.append(clean_cat)
    out["categories"] = list(dict.fromkeys(cats))

    return out
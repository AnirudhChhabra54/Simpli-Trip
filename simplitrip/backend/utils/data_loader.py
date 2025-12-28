# utils/data_loader.py
"""
Local-first dataset loader for SimpliTrip.
Priority: local files > fallback sample data (NO automatic Kaggle downloads)
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional
import pandas as pd

logger = logging.getLogger("data_loader")
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

# dataset mapping (keys used in code)
DATA_DIR = os.getenv("DATA_DIR", "./data")
DATASETS_DIR = os.getenv("DATASETS_DIR", "./datasets")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DATASETS_DIR, exist_ok=True)


def _load_docs_jsonl(path: str) -> pd.DataFrame:
    """Load docs.jsonl into a dataframe with columns: id, text, metadata (if available)."""
    rows = []
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"docs.jsonl not found at {path}")
    with p.open("r", encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                # unify fields
                doc_id = obj.get("id") or obj.get("doc_id") or f"doc_{i}"
                text = obj.get("text") or obj.get("content") or ""
                meta = obj.get("meta") or obj.get("metadata") or {}
                rows.append({"id": doc_id, "text": text, **meta})
            except Exception:
                # try fallback: treat line as plain text
                rows.append({"id": f"doc_{i}", "text": line})
    return pd.DataFrame(rows)


def load_explore_india_dataset() -> pd.DataFrame:
    """
    Local-first loader for the Explore India dataset.
    Priority:
      1) data/explore_india.csv (if exists)
      2) datasets/destinations/*.csv (any CSV in destinations folder)
      3) data/docs.jsonl (fallback)
      4) Built-in sample data (last resort)
    
    NO automatic Kaggle downloads.
    """
    # 1) Try data/explore_india.csv
    local_csv = Path(DATA_DIR) / "explore_india.csv"
    if local_csv.exists():
        try:
            df = pd.read_csv(local_csv)
            logger.info("Loaded local dataset: %s (%d rows)", local_csv, len(df))
            return df
        except Exception as e:
            logger.warning("Failed to load %s: %s", local_csv, e)

    # 2) Try datasets/destinations/*.csv
    dest_dir = Path(DATASETS_DIR) / "destinations"
    if dest_dir.exists():
        csv_files = list(dest_dir.glob("**/*.csv"))
        if csv_files:
            # Sort by size, pick largest
            csv_files.sort(key=lambda p: p.stat().st_size, reverse=True)
            try:
                df = pd.read_csv(csv_files[0])
                logger.info("Loaded dataset from: %s (%d rows)", csv_files[0], len(df))
                return df
            except Exception as e:
                logger.warning("Failed to load %s: %s", csv_files[0], e)

    # 3) Try data/docs.jsonl
    docs_path = Path(DATA_DIR) / "docs.jsonl"
    if docs_path.exists():
        try:
            df = _load_docs_jsonl(str(docs_path))
            logger.info("Loaded fallback docs.jsonl: %s (%d rows)", docs_path, len(df))
            return df
        except Exception as e:
            logger.warning("Failed to load docs.jsonl: %s", e)

    # 4) Built-in sample data (last resort)
    logger.warning("No local datasets found. Using built-in sample data (5 rows).")
    logger.info("To use real data:")
    logger.info("  1. Place CSV files in: %s/destinations/", DATASETS_DIR)
    logger.info("  2. Or place docs.jsonl in: %s/", DATA_DIR)
    logger.info("  3. Or run: python scripts/csv_to_jsonl.py --input datasets/destinations/*.csv --out data/docs.jsonl")
    
    sample = pd.DataFrame([
        {'Destination Name': 'Goa', 'State': 'Goa', 'Category': 'Beach', 'Rating': 4.5, 'Best Time to Visit': 'November to February', 'Description': 'Beautiful beaches and vibrant nightlife'},
        {'Destination Name': 'Jaipur', 'State': 'Rajasthan', 'Category': 'Historical', 'Rating': 4.7, 'Best Time to Visit': 'October to March', 'Description': 'The Pink City with magnificent forts and palaces'},
        {'Destination Name': 'Kerala', 'State': 'Kerala', 'Category': 'Nature', 'Rating': 4.8, 'Best Time to Visit': 'September to March', 'Description': "God's Own Country with backwaters and hill stations"},
        {'Destination Name': 'Udaipur', 'State': 'Rajasthan', 'Category': 'Historical', 'Rating': 4.6, 'Best Time to Visit': 'October to March', 'Description': 'City of Lakes with romantic palaces'},
        {'Destination Name': 'Manali', 'State': 'Himachal Pradesh', 'Category': 'Adventure', 'Rating': 4.4, 'Best Time to Visit': 'October to June', 'Description': 'Hill station perfect for adventure activities'}
    ])
    return sample


def load_tourist_places_dataset() -> pd.DataFrame:
    """
    Load tourist places dataset (local-first).
    Falls back to deriving from docs.jsonl or sample data.
    """
    # Try data/places.csv or data/tourist_places.csv
    for filename in ["places.csv", "tourist_places.csv", "places_processed.csv"]:
        path = Path(DATA_DIR) / filename
        if path.exists():
            try:
                df = pd.read_csv(path)
                logger.info("Loaded tourist places from: %s (%d rows)", path, len(df))
                return df
            except Exception as e:
                logger.warning("Failed to load %s: %s", path, e)
    
    # Try datasets/destinations/places*.csv
    dest_dir = Path(DATASETS_DIR) / "destinations"
    if dest_dir.exists():
        place_files = list(dest_dir.glob("**/places*.csv"))
        if place_files:
            try:
                df = pd.read_csv(place_files[0])
                logger.info("Loaded places from: %s (%d rows)", place_files[0], len(df))
                return df
            except Exception as e:
                logger.warning("Failed to load %s: %s", place_files[0], e)
    
    # Fallback: derive from docs.jsonl
    docs_path = Path(DATA_DIR) / "docs.jsonl"
    if docs_path.exists():
        try:
            df = _load_docs_jsonl(str(docs_path))
            # Try to extract place names
            places = []
            for _, r in df.iterrows():
                place_name = r.get("Destination") or r.get("Place Name") or r.get("text", "")[:80]
                category = r.get("Category") or r.get("Type") or "General"
                places.append({
                    "Place Name": place_name,
                    "Category": category,
                    "Visit Duration": r.get("Visit Duration", "2-3 hours")
                })
            logger.info("Derived %d places from docs.jsonl", len(places))
            return pd.DataFrame(places)
        except Exception as e:
            logger.warning("Could not derive places from docs.jsonl: %s", e)
    
    # Last resort: sample data
    logger.warning("No tourist places data found. Using sample data.")
    return pd.DataFrame([
        {"Place Name": "Baga Beach", "Category": "Beach", "Visit Duration": "3-4 hours"},
        {"Place Name": "Amber Fort", "Category": "Historical", "Visit Duration": "2-3 hours"},
        {"Place Name": "Lake Pichola", "Category": "Lake", "Visit Duration": "2 hours"},
    ])


# Convenience object if other modules expect `data_loader` object
class _DataLoaderShim:
    def load_explore_india_dataset(self):
        return load_explore_india_dataset()

    def load_tourist_places_dataset(self):
        return load_tourist_places_dataset()

    def load_processed_data(self, filename: str):
        """Load processed data from data/ directory"""
        path = Path(DATA_DIR) / filename
        if not path.exists():
            logger.error("Processed data file not found: %s", path)
            raise FileNotFoundError(f"File not found: {path}")
        return pd.read_csv(path)

    def save_processed_data(self, df: pd.DataFrame, filename: str):
        """Save processed data to data/ directory"""
        path = Path(DATA_DIR) / filename
        df.to_csv(path, index=False)
        logger.info("Saved processed data to: %s", path)
        return str(path)


# Export the shim as `data_loader` to be compatible with existing code
data_loader = _DataLoaderShim()

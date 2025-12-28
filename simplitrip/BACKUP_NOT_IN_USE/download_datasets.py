#!/usr/bin/env python3
"""
SimpliTrip - Dataset Download Script (LOCAL-FIRST MODE)

This script is now a NO-OP by default. SimpliTrip uses local datasets.

To use Kaggle datasets (optional):
  1. Set up Kaggle API credentials (~/.kaggle/kaggle.json)
  2. Run with flag: python scripts/download_datasets.py --kaggle-download

For normal usage, manually place your datasets:
  - CSV files: datasets/destinations/*.csv
  - JSONL file: data/docs.jsonl
  - Or run: python scripts/csv_to_jsonl.py to convert CSV to JSONL
"""

import sys
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("download_datasets")


def print_instructions():
    """Print instructions for manual dataset setup"""
    print("=" * 70)
    print("SimpliTrip - Local-First Dataset Setup")
    print("=" * 70)
    print()
    print("📁 This project now uses LOCAL datasets (no automatic Kaggle downloads).")
    print()
    print("To set up your datasets:")
    print()
    print("Option 1: Use CSV files")
    print("  1. Place your CSV files in: datasets/destinations/")
    print("     Example: datasets/destinations/india_destinations.csv")
    print()
    print("  2. Convert to JSONL format:")
    print("     python scripts/csv_to_jsonl.py --input datasets/destinations/*.csv --out data/docs.jsonl")
    print()
    print("  3. Build embeddings:")
    print("     python scripts/build_embeddings.py")
    print()
    print("Option 2: Use JSONL directly")
    print("  1. Place your docs.jsonl file in: data/docs.jsonl")
    print("     Format: one JSON object per line")
    print('     Example: {"id":"doc1","text":"Description...","meta":{}}')
    print()
    print("  2. Build embeddings:")
    print("     python scripts/build_embeddings.py")
    print()
    print("Option 3: Use Kaggle datasets (optional)")
    print("  1. Set up Kaggle API: ~/.kaggle/kaggle.json")
    print("  2. Run: python scripts/download_datasets.py --kaggle-download")
    print()
    print("=" * 70)
    print()
    print("Current directory structure:")
    print("  data/")
    print("    ├── docs.jsonl          (JSONL format for RAG)")
    print("    ├── explore_india.csv   (optional CSV)")
    print("    └── chroma_db/          (vector database)")
    print("  datasets/")
    print("    └── destinations/       (place CSV files here)")
    print()
    print("=" * 70)


def attempt_kaggle_download():
    """Attempt to download datasets from Kaggle (requires credentials)"""
    try:
        from kaggle import api as kaggle_api
    except ImportError:
        logger.error("Kaggle package not installed. Run: pip install kaggle")
        return False
    
    # Check credentials
    kaggle_json = Path.home() / '.kaggle' / 'kaggle.json'
    if not kaggle_json.exists():
        logger.error("Kaggle credentials not found at ~/.kaggle/kaggle.json")
        logger.info("Get your API token from: https://www.kaggle.com/settings")
        return False
    
    logger.info("Kaggle credentials found. Attempting download...")
    
    # Define datasets
    datasets = [
        "surajjha101/explore-india-a-tourist-destination-dataset",
    ]
    
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    success = False
    for dataset_id in datasets:
        try:
            logger.info("Downloading: %s", dataset_id)
            kaggle_api.dataset_download_files(dataset_id, path=str(data_dir), unzip=True, quiet=False)
            logger.info("✅ Downloaded: %s", dataset_id)
            success = True
        except Exception as e:
            logger.error("❌ Failed to download %s: %s", dataset_id, e)
    
    if success:
        logger.info("Download complete. Check data/ directory for CSV files.")
        logger.info("Next: Run python scripts/csv_to_jsonl.py to convert to JSONL format.")
    
    return success


def main():
    parser = argparse.ArgumentParser(description="SimpliTrip Dataset Setup (Local-First)")
    parser.add_argument(
        "--kaggle-download",
        action="store_true",
        help="Attempt to download datasets from Kaggle (requires API credentials)"
    )
    
    args = parser.parse_args()
    
    if args.kaggle_download:
        logger.info("Kaggle download mode enabled")
        success = attempt_kaggle_download()
        return 0 if success else 1
    else:
        # Default: print instructions
        print_instructions()
        return 0


if __name__ == "__main__":
    sys.exit(main())

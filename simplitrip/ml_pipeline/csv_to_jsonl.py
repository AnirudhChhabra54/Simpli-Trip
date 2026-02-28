#!/usr/bin/env python3
"""
CSV to JSONL Converter for SimpliTrip

Converts CSV files (destination data) to JSONL format for RAG indexing.

Usage:
    python scripts/csv_to_jsonl.py --input datasets/destinations/*.csv --out data/docs.jsonl
    python scripts/csv_to_jsonl.py --input data/explore_india.csv --out data/docs.jsonl
    python scripts/csv_to_jsonl.py --input datasets/destinations/raw/*.csv --out data/docs.jsonl --id-prefix dest
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import glob

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("csv_to_jsonl")


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names to handle variations"""
    # Create a mapping of common variations
    column_mapping = {}
    
    for col in df.columns:
        col_lower = col.lower().strip()
        
        # ID columns
        if col_lower in ['id', 'doc_id', 'destination_id', 'place_id']:
            column_mapping[col] = 'id'
        # Destination/Place name
        elif col_lower in ['destination', 'place', 'place name', 'place_name', 'name', 'title']:
            column_mapping[col] = 'destination'
        # Description
        elif col_lower in ['description', 'desc', 'about', 'overview']:
            column_mapping[col] = 'description'
        # Category/Type
        elif col_lower in ['category', 'type', 'place_type', 'destination_type']:
            column_mapping[col] = 'category'
        # Attractions
        elif col_lower in ['attractions', 'places_to_visit', 'top_attractions']:
            column_mapping[col] = 'attractions'
        # Activities
        elif col_lower in ['activities', 'things_to_do', 'what_to_do']:
            column_mapping[col] = 'activities'
        # Best time
        elif col_lower in ['best_time', 'best_time_to_visit', 'season', 'best_season']:
            column_mapping[col] = 'best_time'
        # Duration
        elif col_lower in ['duration', 'visit_duration', 'recommended_duration']:
            column_mapping[col] = 'duration'
        # Budget
        elif col_lower in ['budget', 'cost', 'estimated_cost', 'price']:
            column_mapping[col] = 'budget'
    
    if column_mapping:
        df = df.rename(columns=column_mapping)
        logger.info("Normalized %d column names", len(column_mapping))
    
    return df


def csv_row_to_jsonl_doc(row: pd.Series, row_idx: int, id_prefix: str = "") -> Dict[str, Any]:
    """
    Convert a CSV row to a JSONL document.
    
    Returns dict with: id, text, meta
    """
    # Generate ID
    doc_id = None
    if 'id' in row and pd.notna(row['id']):
        doc_id = str(row['id'])
    elif 'destination' in row and pd.notna(row['destination']):
        # Create ID from destination name
        dest_name = str(row['destination']).lower().replace(' ', '_').replace(',', '')
        doc_id = f"{id_prefix}{dest_name}_{row_idx}" if id_prefix else f"{dest_name}_{row_idx}"
    else:
        doc_id = f"{id_prefix}doc_{row_idx}" if id_prefix else f"doc_{row_idx}"
    
    # Build text content (combine relevant fields)
    text_parts = []
    
    # Add destination/place name
    if 'destination' in row and pd.notna(row['destination']):
        text_parts.append(f"Destination: {row['destination']}")
    
    # Add description
    if 'description' in row and pd.notna(row['description']):
        text_parts.append(str(row['description']))
    
    # Add attractions
    if 'attractions' in row and pd.notna(row['attractions']):
        text_parts.append(f"Attractions: {row['attractions']}")
    
    # Add activities
    if 'activities' in row and pd.notna(row['activities']):
        text_parts.append(f"Activities: {row['activities']}")
    
    # Add best time
    if 'best_time' in row and pd.notna(row['best_time']):
        text_parts.append(f"Best time to visit: {row['best_time']}")
    
    # Add duration
    if 'duration' in row and pd.notna(row['duration']):
        text_parts.append(f"Recommended duration: {row['duration']}")
    
    # Add budget
    if 'budget' in row and pd.notna(row['budget']):
        text_parts.append(f"Budget: {row['budget']}")
    
    # Combine text
    text = ". ".join(text_parts)
    
    # If no text was built, use all non-null values
    if not text.strip():
        text = ". ".join([f"{k}: {v}" for k, v in row.items() if pd.notna(v)])
    
    # Build metadata
    meta = {}
    for col in row.index:
        if col not in ['id', 'description'] and pd.notna(row[col]):
            # Store as metadata
            meta[col] = str(row[col])
    
    return {
        "id": doc_id,
        "text": text,
        "meta": meta
    }


def convert_csv_to_jsonl(input_files: List[str], output_file: str, id_prefix: str = "") -> int:
    """
    Convert CSV files to JSONL format.
    
    Returns: number of documents written
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    total_docs = 0
    
    with output_path.open('w', encoding='utf-8') as out_fh:
        for input_file in input_files:
            input_path = Path(input_file)
            
            if not input_path.exists():
                logger.warning("Input file not found: %s", input_file)
                continue
            
            logger.info("Processing: %s", input_file)
            
            try:
                # Read CSV
                df = pd.read_csv(input_path)
                logger.info("  Loaded %d rows", len(df))
                
                # Normalize column names
                df = normalize_column_names(df)
                
                # Convert each row
                for idx, row in df.iterrows():
                    doc = csv_row_to_jsonl_doc(row, idx, id_prefix)
                    
                    # Write as JSON line
                    json_line = json.dumps(doc, ensure_ascii=False)
                    out_fh.write(json_line + '\n')
                    total_docs += 1
                
                logger.info("  Converted %d documents", len(df))
                
            except Exception as e:
                logger.error("Failed to process %s: %s", input_file, e)
                continue
    
    logger.info("✅ Total documents written: %d", total_docs)
    logger.info("Output file: %s", output_path.absolute())
    
    return total_docs


def main():
    parser = argparse.ArgumentParser(
        description="Convert CSV files to JSONL format for RAG indexing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all CSVs in destinations folder
  python scripts/csv_to_jsonl.py --input datasets/destinations/*.csv --out data/docs.jsonl
  
  # Convert single CSV
  python scripts/csv_to_jsonl.py --input data/explore_india.csv --out data/docs.jsonl
  
  # With ID prefix
  python scripts/csv_to_jsonl.py --input datasets/destinations/*.csv --out data/docs.jsonl --id-prefix dest_
        """
    )
    
    parser.add_argument(
        '--input',
        nargs='+',
        required=True,
        help='Input CSV file(s). Supports wildcards: datasets/destinations/*.csv'
    )
    
    parser.add_argument(
        '--out',
        '--output',
        required=True,
        help='Output JSONL file path (e.g., data/docs.jsonl)'
    )
    
    parser.add_argument(
        '--id-prefix',
        default='',
        help='Prefix for document IDs (e.g., "dest_" -> dest_goa_0)'
    )
    
    args = parser.parse_args()
    
    # Expand wildcards
    input_files = []
    for pattern in args.input:
        expanded = glob.glob(pattern)
        if expanded:
            input_files.extend(expanded)
        else:
            # Not a wildcard, add as-is
            input_files.append(pattern)
    
    if not input_files:
        logger.error("No input files found matching patterns: %s", args.input)
        return 1
    
    logger.info("Found %d input file(s)", len(input_files))
    
    # Convert
    num_docs = convert_csv_to_jsonl(input_files, args.out, args.id_prefix)
    
    if num_docs > 0:
        print()
        print("=" * 70)
        print("✅ Conversion complete!")
        print("=" * 70)
        print(f"Documents created: {num_docs}")
        print(f"Output file: {Path(args.out).absolute()}")
        print()
        print("Next steps:")
        print("  1. Build embeddings:")
        print("     python scripts/build_embeddings.py")
        print()
        print("  2. Start the backend:")
        print("     python main.py")
        print("=" * 70)
        return 0
    else:
        logger.error("No documents were created")
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""
⚡ QUICK START: One-command script to feed North India data
Run this for a quick setup without verification
"""

import json
import sys
from pathlib import Path

# Add backend to path for imports
backend_path = str(Path(__file__).parent.parent)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from services.rag_service import rag_service
from utils.logger import logger

def quick_feed():
    """Quick feed function - minimal setup"""
    print("\n" + "=" * 50)
    print("⚡ QUICK FEED: NORTH INDIA DATA")
    print("=" * 50)
    
    # Read data
    data_file = Path(__file__).parent.parent / "data" / "north_india_destinations.json"
    
    if not data_file.exists():
        print(f"❌ File not found: {data_file}")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        destinations = json.load(f)
    
    print(f"Found {len(destinations)} destinations")
    
    # Add to ChromaDB
    for dest in destinations:
        try:
            # Simple format
            text = f"{dest['destination']} {dest['state']} {dest.get('best_season', '')} {dest.get('climate', '')}"
            
            rag_service.collection.add(
                documents=[text],
                metadatas=[{
                    "type": "destination",
                    "destination": dest['destination'],
                    "state": dest['state'],
                    "region": "North",
                    "custom": True,
                    "data_json": json.dumps(dest, ensure_ascii=False)
                }],
                ids=[f"north_{dest['destination'].lower().replace(' ', '_')}"]
            )
            
            print(f"✅ {dest['destination']}")
            
        except Exception as e:
            print(f"❌ Error: {dest.get('destination', 'Unknown')} - {e}")
    
    print("\n" + "=" * 50)
    print("✨ DONE! Data added to ChromaDB")
    print("=" * 50)

if __name__ == "__main__":
    quick_feed()

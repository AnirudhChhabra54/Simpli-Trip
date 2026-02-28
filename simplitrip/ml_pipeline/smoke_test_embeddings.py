"""
Quick smoke test: run build_embeddings, then check Chroma collection size.
"""
import os
from pathlib import Path
import time
import subprocess
import sys

from dotenv import load_dotenv

load_dotenv()
DATA_DIR = Path(os.environ.get("DATA_DIR", "./data"))
PERSIST_DIR = DATA_DIR / "chroma_db"
COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION", "simplitrip_knowledge")


def check_collection():
    """Check if the collection exists and print stats."""
    try:
        import chromadb
        from chromadb.config import Settings
    except Exception as e:
        print("❌ chromadb not installed:", e)
        print("Install it with: pip install chromadb")
        return

    print("\n" + "=" * 60)
    print("Checking ChromaDB Collection")
    print("=" * 60)
    
    try:
        client = chromadb.PersistentClient(path=str(PERSIST_DIR))
        
        collections = [c.name for c in client.list_collections()]
        print(f"\nCollections available: {collections}")
        
        if COLLECTION_NAME in collections:
            print(f"✅ Collection '{COLLECTION_NAME}' exists")
            col = client.get_collection(COLLECTION_NAME)
            
            # Try to get count
            try:
                count = col.count()
                print(f"   Document count: {count}")
            except Exception as e:
                print(f"   Count not available: {e}")
            
            # Try to get sample metadata
            try:
                results = col.peek(limit=3)
                if results and 'metadatas' in results and results['metadatas']:
                    print(f"   Sample metadata (first 3):")
                    for i, meta in enumerate(results['metadatas'][:3], 1):
                        print(f"     {i}. {meta}")
            except Exception as e:
                print(f"   Could not peek at documents: {e}")
        else:
            print(f"❌ Collection '{COLLECTION_NAME}' not found.")
            print("   Did build_embeddings run successfully?")
    
    except Exception as e:
        print(f"❌ Error checking collection: {e}")


def main():
    print("\n" + "=" * 60)
    print("Smoke Test: Build Embeddings & Verify")
    print("=" * 60)
    
    # Run build_embeddings
    print("\n[1/2] Running build_embeddings...")
    build_script = Path(__file__).resolve().parents[0] / "build_embeddings.py"
    rc = subprocess.call([sys.executable, str(build_script)])
    print(f"\nbuild_embeddings exit code: {rc}")
    
    if rc != 0:
        print("❌ build_embeddings failed!")
        return
    
    # Wait a moment for persistence
    time.sleep(1)
    
    # Check collection
    print("\n[2/2] Checking collection...")
    check_collection()
    
    print("\n" + "=" * 60)
    print("Smoke test complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

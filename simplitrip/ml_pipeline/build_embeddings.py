"""
Build embeddings and upsert to Chroma collection.

Expect:
  - data/docs.jsonl  (one JSON object per line with fields: id, title, text, meta)
  - environment variables (see README below)
"""
import json
import os
import logging
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

try:
    import chromadb
except Exception as e:
    chromadb = None

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("build_embeddings")

# Config (can be set via env)
DATA_DIR = Path(os.environ.get("DATA_DIR", "./data"))
INPUT_FILE = Path(os.environ.get("DOCS_FILE", DATA_DIR / "docs.jsonl"))
CHROMA_COLLECTION = os.environ.get("CHROMA_COLLECTION", "simplitrip_knowledge")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
PERSIST_DIR = Path(os.environ.get("CHROMA_PERSIST", DATA_DIR / "chroma_db"))
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 300))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", 50))
BATCH_SIZE = int(os.environ.get("EMBED_BATCH_SIZE", 64))


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks based on word tokens."""
    tokens = text.split()
    if len(tokens) <= chunk_size:
        return [" ".join(tokens)]
    chunks = []
    i = 0
    while i < len(tokens):
        chunk = tokens[i : i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks


def load_documents(path: Path) -> List[Dict]:
    """Load documents from JSONL file (one JSON object per line)."""
    docs = []
    if not path.exists():
        logger.error("Input docs file not found: %s", path)
        return docs
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                docs.append(obj)
            except Exception:
                logger.exception("Skipping invalid JSON line.")
    logger.info("Loaded %d documents from %s", len(docs), path)
    return docs


def main():
    if chromadb is None:
        logger.error("chromadb is not installed. Run: pip install chromadb")
        print("\n❌ ChromaDB not found!")
        print("Install it with: pip install chromadb")
        return

    INPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    PERSIST_DIR.mkdir(parents=True, exist_ok=True)

    docs = load_documents(INPUT_FILE)
    if not docs:
        logger.error("No documents to index. Input file: %s", INPUT_FILE)
        print(f"\n❌ No documents found in {INPUT_FILE}")
        print()
        print("To create docs.jsonl:")
        print()
        print("Option 1: Convert CSV files to JSONL")
        print("  python scripts/csv_to_jsonl.py --input datasets/destinations/*.csv --out data/docs.jsonl")
        print()
        print("Option 2: Manually create JSONL file")
        print("  Create data/docs.jsonl with one JSON object per line:")
        print('  {"id":"doc1","text":"Description of destination...","meta":{"category":"beach"}}')
        print()
        print("Option 3: Copy sample data")
        print("  cp data/docs.jsonl.sample data/docs.jsonl")
        print()
        return

    # Setup chroma client (using PersistentClient for newer ChromaDB versions)
    logger.info("Initializing ChromaDB at %s", PERSIST_DIR)
    client = chromadb.PersistentClient(path=str(PERSIST_DIR))
    
    # create/get collection
    try:
        collection = client.get_collection(CHROMA_COLLECTION)
        logger.info("Found existing collection '%s'", CHROMA_COLLECTION)
    except Exception:
        collection = client.create_collection(CHROMA_COLLECTION)
        logger.info("Created collection '%s'", CHROMA_COLLECTION)

    # Setup embedder
    logger.info("Loading embedding model: %s", EMBEDDING_MODEL)
    embedder = SentenceTransformer(EMBEDDING_MODEL)
    logger.info("Embedding model loaded successfully")

    # Process documents and create chunks
    all_ids, all_docs, all_meta = [], [], []
    for doc in docs:
        doc_id = doc.get("id") or doc.get("title") or f"doc_{len(all_ids)+1}"
        text = doc.get("text", "")
        meta = doc.get("meta", {})
        chunks = chunk_text(text)
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}__{idx}"
            all_ids.append(chunk_id)
            all_docs.append(chunk)
            # include source reference
            entry_meta = dict(meta)
            entry_meta.update({"source_id": doc_id, "chunk_index": idx})
            all_meta.append(entry_meta)

    logger.info("Total chunks to embed: %d", len(all_docs))

    # Compute embeddings in batches
    embeddings = []
    for i in tqdm(range(0, len(all_docs), BATCH_SIZE), desc="Embedding batches"):
        batch_texts = all_docs[i : i + BATCH_SIZE]
        emb_batch = embedder.encode(
            batch_texts, 
            batch_size=len(batch_texts), 
            convert_to_numpy=True, 
            show_progress_bar=False
        )
        embeddings.extend(emb_batch.tolist())

    logger.info("Adding to Chroma collection...")
    # Try to add, fallback to upsert if needed
    try:
        collection.add(ids=all_ids, documents=all_docs, metadatas=all_meta, embeddings=embeddings)
        logger.info("Successfully added documents to collection")
    except Exception as e:
        logger.warning("Add failed (%s); attempting upsert fallback.", str(e))
        try:
            collection.upsert(ids=all_ids, documents=all_docs, metadatas=all_meta, embeddings=embeddings)
            logger.info("Successfully upserted documents to collection")
        except Exception:
            logger.exception("Upsert also failed.")
            return

    # Note: PersistentClient auto-persists, no need to call persist()
    logger.info("✅ Upsert complete. Data persisted to %s", PERSIST_DIR)
    print(f"\n✅ Successfully indexed {len(all_docs)} chunks from {len(docs)} documents")
    print(f"Collection: {CHROMA_COLLECTION}")
    print(f"Persist directory: {PERSIST_DIR}")


if __name__ == "__main__":
    main()

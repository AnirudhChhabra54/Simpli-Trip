"""
RAG Service - Local Retrieval-Augmented Generation using ChromaDB.

Privacy-first vector storage with zero cloud cost:
- ChromaDB: local vector database with persistence
- Sentence-Transformers: local embeddings (all-MiniLM-L6-v2)

Gracefully degrades: if ChromaDB/embeddings are unavailable the service
reports `is_available() == False` so callers (trip storage, health check,
knowledge search) fall back to safe behaviour instead of crashing.
"""
import os
import string
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.api.types import EmbeddingFunction

from utils.logger import logger
from config.settings import settings

# Default persistent location (kept alongside the rest of the data).
try:
    DEFAULT_PERSIST_DIR = str(Path(settings.DATA_DIR) / "chromadb")
except Exception:
    DEFAULT_PERSIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "chromadb")


class _HashEmbeddingFunction(EmbeddingFunction):
    """
    Deterministic, dependency-free fallback embedding function.

    Produces a fixed-size vector from text via a hashing trick, so ChromaDB
    can operate even when Sentence-Transformers and its model are unavailable
    or unavailable offline. Retrieval quality is lower than a real transformer
    but add/get/update/delete remain fully functional.
    """

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def __call__(self, input: List[str]) -> List[List[float]]:
        return [self._hash_text(text) for text in input]

    def _hash_text(self, text: str) -> List[float]:
        cleaned = text.lower().translate(str.maketrans("", "", string.punctuation))
        tokens = cleaned.split()
        vector = [0.0] * self.dimensions
        for token in tokens:
            # Simple hashing trick: deterministic index + sign.
            h = 0
            for ch in token:
                h = (h * 31 + ord(ch)) & 0xFFFFFFFF
            idx = h % self.dimensions
            try:
                sign = (h >> 4) % 2 if h else 1
                vector[idx] += 1.0 if sign else -1.0
            except Exception:
                vector[h % self.dimensions] += 1.0
        norm = sum(v * v for v in vector) ** 0.5
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector


class RAGService:
    """Local ChromaDB-backed knowledge base and trip store."""

    COLLECTION_NAME = "travel_knowledge"

    def __init__(self, persist_directory: Optional[str] = None):
        self.persist_directory = persist_directory or DEFAULT_PERSIST_DIR
        self.client = None
        self.collection = None
        self.embedding_function = None
        self._initialize()

    def _initialize(self):
        """Set up the embedding function, client and collection. Never raises."""
        try:
            # Prefer real transformers for high-quality retrieval; fall back to hashing.
            try:
                from sentence_transformers import SentenceTransformer

                class _STEmbeddingFunction(EmbeddingFunction):
                    _model = None

                    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
                        self._model_name = model_name
                        if _STEmbeddingFunction._model is None:
                            _STEmbeddingFunction._model = SentenceTransformer(model_name)

                    def __call__(self, input: List[str]) -> List[List[float]]:
                        return self._model.encode(input).tolist()

                self.embedding_function = _STEmbeddingFunction()
            except Exception:
                logger.warning("Sentence-Transformers unavailable; using hashing embeddings.")
                self.embedding_function = _HashEmbeddingFunction()

            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=ChromaSettings(anonymized_telemetry=False),
            )

            try:
                self.collection = self.client.get_collection(
                    name=self.COLLECTION_NAME,
                    embedding_function=self.embedding_function,
                )
            except Exception:
                self.collection = self.client.create_collection(
                    name=self.COLLECTION_NAME,
                    metadata={"description": "Travel knowledge base for SimpliTrip"},
                    embedding_function=self.embedding_function,
                )
            logger.info("RAG service ready at %s", self.persist_directory)
        except Exception as e:
            logger.error("RAG service unavailable: %s", e)
            self.client = None
            self.collection = None

    def is_available(self) -> bool:
        return self.collection is not None

    def retrieve(self, query: str, top_k: int = 5, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Return up to `top_k` matching documents as [{id, text, meta, distance}]."""
        if not self.is_available() or not query:
            return []
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where or None,
            )
            if not results or not results.get("ids"):
                return []
            formatted: List[Dict[str, Any]] = []
            for i in range(len(results["ids"][0])):
                formatted.append({
                    "id": results["ids"][0][i],
                    "text": (results.get("documents") or [[]])[0][i],
                    "meta": (results.get("metadatas") or [[]])[0][i] or {},
                    "distance": (results.get("distances") or [[]])[0][i]
                    if results.get("distances") else 0.0,
                })
            return formatted
        except Exception as e:
            logger.error("RAG retrieve error: %s", e)
            return []

    def search(self, query: str, n_results: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Alias of retrieve() keeping the same shape for older callers."""
        return self.retrieve(query, top_k=n_results, where=filter_metadata)

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> Optional[List[str]]:
        if not self.is_available() or not documents:
            return None
        try:
            existing_count = self.collection.count()
            if ids is None:
                ids = [f"doc_{existing_count + i}" for i in range(len(documents))]
            self.collection.add(
                documents=documents,
                metadatas=metadatas or [{} for _ in documents],
                ids=ids,
            )
            return ids
        except Exception as e:
            logger.error("RAG add_documents error: %s", e)
            return None

    def get_collection_stats(self) -> Dict[str, Any]:
        if not self.is_available():
            return {"available": False, "count": 0}
        try:
            return {"available": True, "count": self.collection.count(), "name": self.COLLECTION_NAME}
        except Exception as e:
            logger.error("RAG stats error: %s", e)
            return {"available": False, "count": 0}

    def seed_knowledge_base(self) -> bool:
        """
        Populate the ChromaDB knowledge base from the local destination/place
        datasets on first use (no-op if already populated). This is what makes
        semantic destination search and RAG-driven itinerary generation work.
        """
        if not self.is_available():
            return False
        try:
            # Seed if no dataset documents are present yet (the collection may
            # already hold user trips, which we must not remove).
            if self.collection.count() > 0:
                existing = self.collection.get(where={"source": "dataset"}, limit=1)
                if existing and existing.get("ids"):
                    return True

            from utils.data_loader import load_explore_india_dataset, load_tourist_places_dataset

            documents: List[str] = []
            metadatas: List[Dict[str, Any]] = []
            ids: List[str] = []

            try:
                df = load_explore_india_dataset()
                for i, row in df.iterrows():
                    name = (row.get("Destination Name")
                            or row.get("destination_name")
                            or row.get("Destination")
                            or row.get("name"))
                    if not name:
                        continue
                    state = (row.get("State")
                             or row.get("state")
                             or "India")
                    category = row.get("Category") or row.get("category") or "General"
                    desc = (row.get("Description")
                            or row.get("description")
                            or row.get("text")
                            or f"{name} is a popular travel destination.")
                    documents.append(f"{name} ({state}) | {category}. {desc}")
                    metadatas.append({
                        "destination": str(name),
                        "state": str(state),
                        "category": str(category),
                        "best_season": str(row.get("Best Time to Visit") or row.get("best_time_visit") or ""),
                        "source": "dataset",
                    })
                    ids.append(f"dest_{i}")
            except Exception as e:
                logger.warning("RAG seed destinations skipped: %s", e)

            try:
                pdf = load_tourist_places_dataset()
                for i, row in pdf.iterrows():
                    pname = row.get("Place Name") or row.get("name")
                    if not pname:
                        continue
                    category = row.get("Category") or row.get("category") or "General"
                    documents.append(f"{pname} - {category}. Visit duration: {row.get('Visit Duration') or 'N/A'}")
                    metadatas.append({
                        "destination": str(pname),
                        "state": "",
                        "category": str(category),
                        "source": "dataset",
                    })
                    ids.append(f"place_{i}")
            except Exception as e:
                logger.warning("RAG seed places skipped: %s", e)

            if documents:
                self.add_documents(documents=documents, metadatas=metadatas, ids=ids)
                logger.info("Knowledge base seeded with %d documents", len(documents))
            return True
        except Exception as e:
            logger.error("RAG seed_knowledge_base error: %s", e)
            return False


rag_service = RAGService()
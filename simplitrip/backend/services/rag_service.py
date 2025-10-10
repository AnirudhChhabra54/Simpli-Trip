"""
RAG Service - FREE Retrieval-Augmented Generation
Uses ChromaDB (local vector database) and Sentence-Transformers (local embeddings)
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from services.ollama_service import ollama_service
from utils.logger import logger
from config.settings import settings


class RAGService:
    """
    FREE RAG implementation using:
    - ChromaDB: Local vector database
    - Sentence-Transformers: Local embeddings
    - Ollama: Local LLM
    """
    
    def __init__(
        self,
        collection_name: str = "travel_knowledge",
        embedding_model: str = "all-MiniLM-L6-v2",
        persist_directory: Optional[str] = None
    ):
        """
        Initialize RAG service
        
        Args:
            collection_name: Name of the ChromaDB collection
            embedding_model: Sentence-Transformers model name
            persist_directory: Directory to persist ChromaDB data
        """
        self.collection_name = collection_name
        
        # Set persist directory
        if persist_directory is None:
            persist_directory = str(Path(settings.DATA_DIR) / "chromadb")
        
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model (runs locally, FREE)
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedder = SentenceTransformer(embedding_model)
        logger.info("Embedding model loaded successfully")
        
        # Initialize ChromaDB client (runs locally, FREE)
        logger.info(f"Initializing ChromaDB at: {persist_directory}")
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Travel knowledge base for SimpliTrip"}
            )
            logger.info(f"Created new collection: {collection_name}")
            self._initialize_with_sample_data()
    
    def _initialize_with_sample_data(self):
        """Initialize collection with sample travel data"""
        logger.info("Initializing with sample travel data...")
        
        sample_docs = [
            {
                "content": "Goa is best visited between November and February when the weather is pleasant. The monsoon season (June-September) brings heavy rains. Summer (March-May) can be very hot and humid.",
                "metadata": {"destination": "Goa", "category": "weather", "type": "best_time"}
            },
            {
                "content": "Goa offers beautiful beaches like Baga, Calangute, and Anjuna. Popular activities include water sports, beach parties, and exploring Portuguese architecture. Budget: ₹30,000-50,000 for 5 days.",
                "metadata": {"destination": "Goa", "category": "activities", "type": "overview"}
            },
            {
                "content": "Jaipur, the Pink City, is famous for Amber Fort, City Palace, and Hawa Mahal. Best time to visit is October to March. Rich in Rajasthani culture and cuisine. Budget: ₹25,000-45,000 for 4 days.",
                "metadata": {"destination": "Jaipur", "category": "historical", "type": "overview"}
            },
            {
                "content": "Kerala backwaters are best explored by houseboat. Alleppey and Kumarakom are popular starting points. A 2-day houseboat cruise costs ₹8,000-15,000. Best season: September to March.",
                "metadata": {"destination": "Kerala", "category": "nature", "type": "activities"}
            },
            {
                "content": "Ladakh is ideal for adventure seekers. Visit between June and September when roads are open. Key attractions: Pangong Lake, Nubra Valley, Leh Palace. Budget: ₹40,000-70,000 for 7 days.",
                "metadata": {"destination": "Ladakh", "category": "adventure", "type": "overview"}
            },
            {
                "content": "Manali offers skiing, paragliding, and trekking. Solang Valley and Rohtang Pass are must-visits. Best time: October to June. Avoid monsoon season. Budget: ₹20,000-35,000 for 5 days.",
                "metadata": {"destination": "Manali", "category": "adventure", "type": "activities"}
            },
            {
                "content": "Udaipur, the City of Lakes, is known for Lake Pichola, City Palace, and romantic ambiance. Best for couples and honeymooners. Visit October to March. Budget: ₹30,000-50,000 for 4 days.",
                "metadata": {"destination": "Udaipur", "category": "romantic", "type": "overview"}
            },
            {
                "content": "Budget travel tips: Book flights 2-3 months in advance, stay in hostels or budget hotels, use public transport, eat at local restaurants, travel during off-season for better deals.",
                "metadata": {"category": "budget", "type": "tips"}
            },
            {
                "content": "Indian Railways offers affordable travel. Book Tatkal tickets for last-minute plans. AC 3-tier is comfortable and economical. Use IRCTC app for bookings.",
                "metadata": {"category": "transport", "type": "tips"}
            },
            {
                "content": "Street food safety: Eat at busy stalls with high turnover, avoid raw salads, drink bottled water, carry hand sanitizer. Popular safe options: samosas, pakoras, dosas.",
                "metadata": {"category": "food", "type": "safety"}
            }
        ]
        
        self.add_documents(
            documents=[doc["content"] for doc in sample_docs],
            metadatas=[doc["metadata"] for doc in sample_docs]
        )
        
        logger.info(f"Added {len(sample_docs)} sample documents to knowledge base")
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ):
        """
        Add documents to the knowledge base
        
        Args:
            documents: List of text documents
            metadatas: Optional metadata for each document
            ids: Optional IDs for documents (auto-generated if not provided)
        """
        if not documents:
            return
        
        # Generate embeddings (FREE, runs locally)
        logger.info(f"Generating embeddings for {len(documents)} documents...")
        embeddings = self.embedder.encode(documents, show_progress_bar=True)
        
        # Generate IDs if not provided
        if ids is None:
            existing_count = self.collection.count()
            ids = [f"doc_{existing_count + i}" for i in range(len(documents))]
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas or [{} for _ in documents],
            ids=ids
        )
        
        logger.info(f"Added {len(documents)} documents to collection")
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of relevant documents with metadata and scores
        """
        # Generate query embedding (FREE, runs locally)
        query_embedding = self.embedder.encode([query])[0]
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted_results
    
    def query_with_rag(
        self,
        question: str,
        n_context: int = 3,
        filter_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Answer question using RAG (Retrieval-Augmented Generation)
        
        Args:
            question: User's question
            n_context: Number of context documents to retrieve
            filter_metadata: Optional metadata filters
            
        Returns:
            Dict with answer, sources, and context
        """
        # Step 1: Retrieve relevant documents
        logger.info(f"Searching for context: {question}")
        search_results = self.search(question, n_results=n_context, filter_metadata=filter_metadata)
        
        if not search_results:
            return {
                'answer': "I don't have enough information to answer that question.",
                'sources': [],
                'context': []
            }
        
        # Step 2: Build context from retrieved documents
        context_parts = []
        sources = []
        
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"[{i}] {result['document']}")
            sources.append({
                'id': result['id'],
                'content': result['document'],
                'metadata': result['metadata']
            })
        
        context = "\n\n".join(context_parts)
        
        # Step 3: Generate answer using Ollama (FREE, local LLM)
        system_prompt = """You are a helpful travel assistant. Answer questions based on the provided context.
If the context doesn't contain enough information, say so. Be concise and helpful."""
        
        prompt = f"""Context information:
{context}

Question: {question}

Answer the question based on the context above. If the context doesn't have enough information, say so clearly."""
        
        logger.info("Generating answer with Ollama...")
        answer = ollama_service.generate(prompt, system=system_prompt, temperature=0.7)
        
        return {
            'answer': answer,
            'sources': sources,
            'context': context_parts
        }
    
    def get_destination_info(self, destination: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a destination
        
        Args:
            destination: Destination name
            
        Returns:
            Dict with destination information
        """
        # Search for destination-specific information
        results = self.search(
            query=f"Information about {destination}",
            n_results=5,
            filter_metadata={"destination": destination}
        )
        
        if not results:
            return {
                'destination': destination,
                'info': f"Limited information available for {destination}",
                'sources': []
            }
        
        # Compile information
        info_parts = [result['document'] for result in results]
        combined_info = "\n\n".join(info_parts)
        
        # Generate summary using LLM
        prompt = f"""Summarize this information about {destination} in 2-3 paragraphs:

{combined_info}

Make it engaging and informative for travelers."""
        
        summary = ollama_service.generate(prompt, temperature=0.7)
        
        return {
            'destination': destination,
            'summary': summary,
            'details': info_parts,
            'sources': [r['metadata'] for r in results]
        }
    
    def get_travel_tips(self, category: str = "general") -> List[str]:
        """
        Get travel tips for a specific category
        
        Args:
            category: Category of tips (budget, safety, food, transport, etc.)
            
        Returns:
            List of travel tips
        """
        results = self.search(
            query=f"{category} travel tips",
            n_results=3,
            filter_metadata={"category": category}
        )
        
        if not results:
            # Get general tips
            results = self.search(query="travel tips", n_results=3)
        
        tips = []
        for result in results:
            # Extract tips from document
            doc = result['document']
            # Split by common delimiters
            if ':' in doc:
                tip = doc.split(':', 1)[1].strip()
                tips.append(tip)
            else:
                tips.append(doc)
        
        return tips[:5]  # Return max 5 tips
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(name=self.collection_name)
        logger.info(f"Cleared collection: {self.collection_name}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        count = self.collection.count()
        
        return {
            'total_documents': count,
            'collection_name': self.collection_name,
            'embedding_model': self.embedder.get_sentence_embedding_dimension(),
            'status': 'active' if count > 0 else 'empty'
        }
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Alias for get_stats() - for compatibility with add_data_to_rag.py"""
        return self.get_stats()
    
    def add_document(self, text: str, metadata: Dict = None) -> str:
        """
        Add a single document to the knowledge base
        
        Args:
            text: Document text
            metadata: Optional metadata
            
        Returns:
            Document ID
        """
        if metadata is None:
            metadata = {}
        
        # Generate ID
        existing_count = self.collection.count()
        doc_id = f"doc_{existing_count}"
        
        # Add using add_documents
        self.add_documents(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        return doc_id


# Create global instance
rag_service = RAGService()

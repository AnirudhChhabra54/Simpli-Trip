"""
Trip Storage Service - ChromaDB based trip management
Replaces Firestore for local, privacy-first trip storage
"""
import uuid
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from services.rag_service import rag_service

logger = logging.getLogger("TripStorageService")

class TripStorageService:
    """
    Stores user trips in ChromaDB as JSON documents with embeddings
    Enables semantic search and efficient retrieval
    """
    
    COLLECTION_NAME = "user_trips"
    
    def __init__(self):
        self.rag_service = rag_service
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Ensure trips collection exists in ChromaDB"""
        try:
            if not self.rag_service.is_available():
                logger.warning("RAG service not available, trip storage may be limited")
                return
            
            # Get or create trips collection
            if hasattr(self.rag_service, 'collection') and self.rag_service.collection:
                logger.info("✅ Trip storage collection ready in ChromaDB")
            else:
                logger.warning("⚠️ ChromaDB collection not ready")
        except Exception as e:
            logger.error(f"Error ensuring collection: {e}")
    
    def add_trip(self, user_id: str, trip_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new trip to ChromaDB
        
        Args:
            user_id: Unique user identifier
            trip_data: Trip information (name, destination, budget, dates, etc.)
            
        Returns:
            Created trip with ID
        """
        try:
            # Generate unique trip ID
            trip_id = str(uuid.uuid4())
            
            # Prepare trip document
            trip_doc = {
                "id": trip_id,
                "userId": user_id,
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                **trip_data  # Merge all trip data
            }
            
            # Create searchable text representation
            search_text = self._create_search_text(trip_doc)
            
            # Store in ChromaDB
            if self.rag_service.is_available():
                doc_id = self.rag_service.collection.add(
                    documents=[search_text],
                    metadatas=[{
                        "type": "trip",
                        "user_id": user_id,
                        "trip_id": trip_id,
                        "destination": trip_data.get("destination", ""),
                        "full_data": json.dumps(trip_doc)
                    }],
                    ids=[trip_id]
                )
                logger.info(f"✅ Trip saved: {trip_id} for user: {user_id}")
            
            return trip_doc
            
        except Exception as e:
            logger.error(f"Error adding trip: {e}")
            raise
    
    def get_user_trips(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all trips for a user
        
        Args:
            user_id: User ID to filter by
            
        Returns:
            List of user's trips
        """
        try:
            if not self.rag_service.is_available():
                logger.warning("RAG service not available")
                return []
            
            # Query for user's trips
            results = self.rag_service.collection.get(
                where={"user_id": user_id}
            ) if hasattr(self.rag_service.collection, 'get') else None
            
            if not results or not results.get('metadatas'):
                return []
            
            trips = []
            for metadata in results['metadatas']:
                if 'full_data' in metadata:
                    trip = json.loads(metadata['full_data'])
                    trips.append(trip)
            
            logger.info(f"✅ Retrieved {len(trips)} trips for user: {user_id}")
            return trips
            
        except Exception as e:
            logger.error(f"Error retrieving trips: {e}")
            return []
    
    def get_trip_by_id(self, trip_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific trip by ID
        
        Args:
            trip_id: Trip ID to retrieve
            
        Returns:
            Trip data or None
        """
        try:
            if not self.rag_service.is_available():
                return None
            
            # Retrieve by ID
            result = self.rag_service.collection.get(ids=[trip_id])
            
            if result and result['metadatas']:
                metadata = result['metadatas'][0]
                if 'full_data' in metadata:
                    return json.loads(metadata['full_data'])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting trip {trip_id}: {e}")
            return None
    
    def update_trip(self, trip_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing trip
        
        Args:
            trip_id: Trip ID to update
            updates: Fields to update
            
        Returns:
            Updated trip
        """
        try:
            # Get current trip
            trip = self.get_trip_by_id(trip_id)
            if not trip:
                raise ValueError(f"Trip {trip_id} not found")
            
            # Merge updates
            trip.update(updates)
            trip['updatedAt'] = datetime.now().isoformat()
            
            # Update search text
            search_text = self._create_search_text(trip)
            
            # Update in ChromaDB
            if self.rag_service.is_available():
                self.rag_service.collection.update(
                    ids=[trip_id],
                    documents=[search_text],
                    metadatas=[{
                        "type": "trip",
                        "user_id": trip['userId'],
                        "trip_id": trip_id,
                        "destination": trip.get("destination", ""),
                        "full_data": json.dumps(trip)
                    }]
                )
                logger.info(f"✅ Trip updated: {trip_id}")
            
            return trip
            
        except Exception as e:
            logger.error(f"Error updating trip: {e}")
            raise
    
    def delete_trip(self, trip_id: str) -> bool:
        """
        Delete a trip
        
        Args:
            trip_id: Trip ID to delete
            
        Returns:
            True if successful
        """
        try:
            if self.rag_service.is_available():
                self.rag_service.collection.delete(ids=[trip_id])
                logger.info(f"✅ Trip deleted: {trip_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting trip: {e}")
            return False
    
    def search_trips(self, user_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Semantic search for trips by destination, preferences, etc.
        
        Args:
            user_id: Filter by user
            query: Search query (e.g., "beach destinations")
            top_k: Number of results
            
        Returns:
            List of matching trips
        """
        try:
            if not self.rag_service.is_available():
                return []
            
            # Semantic search
            results = self.rag_service.retrieve(
                query=f"user: {user_id} - {query}",
                top_k=top_k
            )
            
            trips = []
            for result in results:
                if isinstance(result, dict) and 'meta' in result:
                    meta = result['meta']
                    if meta.get('user_id') == user_id and 'full_data' in meta:
                        trip = json.loads(meta['full_data'])
                        trips.append(trip)
            
            return trips
            
        except Exception as e:
            logger.error(f"Error searching trips: {e}")
            return []
    
    @staticmethod
    def _create_search_text(trip_doc: Dict[str, Any]) -> str:
        """Create searchable text representation of trip"""
        parts = [
            f"Trip: {trip_doc.get('name', 'Unnamed')}",
            f"Destination: {trip_doc.get('destination', '')}",
            f"Budget: {trip_doc.get('budget', 'N/A')}",
            f"Dates: {trip_doc.get('startDate', '')} to {trip_doc.get('endDate', '')}",
            f"Travelers: {trip_doc.get('travelers', 1)}",
            f"Preferences: {', '.join(trip_doc.get('preferences', []))}",
            f"Status: {trip_doc.get('status', 'planned')}"
        ]
        return " | ".join(parts)


# Singleton instance
trip_storage = TripStorageService()

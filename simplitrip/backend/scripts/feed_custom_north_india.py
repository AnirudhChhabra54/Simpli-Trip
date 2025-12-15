"""
🚀 COMPLETE SCRIPT: Feed Custom North India Data to RAG/ChromaDB
Run this script to add all North India destinations to your vector database
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path for imports
backend_path = str(Path(__file__).parent.parent)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from services.rag_service import rag_service
from utils.logger import logger

# ============================================================================
# 📊 MAIN FEED FUNCTION
# ============================================================================

def feed_custom_north_india_data():
    """
    Feed custom North India destinations from JSON file to ChromaDB
    Returns: True if successful, False otherwise
    """
    try:
        logger.info("=" * 70)
        logger.info("🌏 FEEDING CUSTOM NORTH INDIA DATA TO CHROMADB")
        logger.info("=" * 70)
        
        # Check if RAG service is available
        if not hasattr(rag_service, 'collection'):
            logger.error("❌ RAG service or collection not initialized")
            return False
        
        # Path to data file
        data_file = Path(__file__).parent.parent / "data" / "north_india_destinations.json"
        
        if not data_file.exists():
            logger.error(f"❌ Data file not found: {data_file}")
            logger.info(f"💡 Please create the file at: {data_file}")
            return False
        
        # Read and validate JSON data
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                destinations = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse error in {data_file}: {e}")
            return False
        
        if not isinstance(destinations, list):
            logger.error("❌ Data should be a JSON array of destinations")
            return False
        
        logger.info(f"📥 Loading {len(destinations)} destinations from file...")
        
        added_count = 0
        errors = []
        
        # Process each destination
        for dest in destinations:
            try:
                # Validate required fields
                if not validate_destination(dest):
                    errors.append(f"Invalid destination: {dest.get('destination', 'Unknown')}")
                    continue
                
                # 1. Convert to searchable text for embeddings
                knowledge_text = format_for_search(dest)
                
                # 2. Create metadata with all data
                metadata = create_metadata(dest)
                
                # 3. Create unique document ID
                doc_id = f"custom_north_{dest['destination'].lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"
                
                # 4. Add to ChromaDB collection
                rag_service.collection.add(
                    documents=[knowledge_text],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
                
                added_count += 1
                logger.info(f"✅ Added: {dest['destination']} (ID: {doc_id})")
                
            except Exception as e:
                error_msg = f"Error adding {dest.get('destination', 'Unknown')}: {str(e)}"
                logger.error(f"❌ {error_msg}")
                errors.append(error_msg)
                continue
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info(f"✨ SUCCESSFULLY ADDED {added_count} DESTINATIONS TO CHROMADB")
        
        if errors:
            logger.info(f"⚠️  {len(errors)} errors occurred:")
            for error in errors[:5]:  # Show first 5 errors
                logger.info(f"   - {error}")
            if len(errors) > 5:
                logger.info(f"   ... and {len(errors) - 5} more errors")
        
        logger.info("=" * 70)
        
        return added_count > 0
        
    except Exception as e:
        logger.error(f"❌ Fatal error in feed function: {e}")
        return False


# ============================================================================
# 🛠️ HELPER FUNCTIONS
# ============================================================================

def validate_destination(dest):
    """Validate required fields in destination data"""
    required_fields = ['destination', 'state', 'best_season', 'attractions', 'activities', 'budget']
    
    for field in required_fields:
        if field not in dest:
            logger.warning(f"⚠️  Missing required field '{field}' in destination")
            return False
    
    # Check that attractions and activities are lists with at least one item
    if not isinstance(dest.get('attractions', []), list) or len(dest['attractions']) < 1:
        logger.warning(f"⚠️  'attractions' must be a non-empty list")
        return False
    
    if not isinstance(dest.get('activities', []), list) or len(dest['activities']) < 1:
        logger.warning(f"⚠️  'activities' must be a non-empty list")
        return False
    
    return True


def format_for_search(dest):
    """
    Format destination data into searchable text for vector embeddings
    Optimized for semantic search
    """
    parts = [
        f"DESTINATION: {dest['destination']}",
        f"STATE: {dest.get('state', 'N/A')}",
        f"REGION: {dest.get('region', 'North India')}",
        f"BEST TIME TO VISIT: {dest.get('best_season', 'N/A')}",
        f"CLIMATE: {dest.get('climate', 'N/A')}",
        "",
        "TOP ATTRACTIONS:",
        *[f"• {attraction}" for attraction in dest.get('attractions', [])],
        "",
        "POPULAR ACTIVITIES:",
        *[f"• {activity}" for activity in dest.get('activities', [])],
        "",
        f"AVERAGE BUDGET: {dest.get('budget', 'N/A')}",
        "",
        "LOCAL FOOD SPECIALTIES:",
        *[f"• {food}" for food in dest.get('food_specialties', [])],
        "",
        "RECOMMENDED PACKING LIST:",
        *[f"• {item}" for item in dest.get('packing_list', [])],
        "",
        "TRAVEL TIPS:",
        *[f"• {tip}" for tip in dest.get('travel_tips', [])],
        "",
        f"TRANSPORTATION: {dest.get('transportation', 'N/A')}",
        "",
        "ACCOMMODATION OPTIONS:",
        *[f"• {hotel}" for hotel in dest.get('hotels', [])],
    ]
    
    return "\n".join(parts)


def create_metadata(dest):
    """Create metadata dictionary for ChromaDB storage"""
    return {
        "type": "destination",
        "category": "custom_north_india",
        "destination": dest['destination'],
        "state": dest.get('state', ''),
        "region": dest.get('region', 'North'),
        "best_season": dest.get('best_season', ''),
        "climate": dest.get('climate', ''),
        "budget": dest.get('budget', ''),
        "attraction_count": len(dest.get('attractions', [])),
        "activity_count": len(dest.get('activities', [])),
        "data_json": json.dumps(dest, ensure_ascii=False),  # Full data
        "custom": True,
        "source": "north_india_custom_data",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# 🔍 VERIFICATION FUNCTIONS
# ============================================================================

def verify_data_in_chromadb():
    """
    Verify that data was successfully added to ChromaDB
    """
    try:
        logger.info("\n" + "=" * 70)
        logger.info("🔍 VERIFYING DATA IN CHROMADB")
        logger.info("=" * 70)
        
        # Get collection statistics
        try:
            stats = rag_service.get_collection_stats()
            total_docs = stats.get('num_documents', 0)
            logger.info(f"📊 Total documents in ChromaDB: {total_docs}")
        except Exception as e:
            logger.warning(f"⚠️  Could not get stats: {e}")
            total_docs = "Unknown"
        
        # Test search queries
        test_queries = [
            "Ladakh high altitude trekking",
            "Jaipur forts and palaces",
            "Rishikesh yoga meditation",
            "Manali adventure sports"
        ]
        
        found_count = 0
        for query in test_queries:
            try:
                results = rag_service.retrieve(query, top_k=2)
                if results and len(results) > 0:
                    dest = results[0]['meta']['destination']
                    logger.info(f"✅ Query '{query}' → Found: {dest}")
                    found_count += 1
                else:
                    logger.warning(f"⚠️  No results for query: {query}")
            except Exception as e:
                logger.error(f"❌ Error searching for '{query}': {e}")
        
        logger.info(f"📈 Search success rate: {found_count}/{len(test_queries)}")
        
        # List all custom North India destinations
        try:
            logger.info("\n📋 CUSTOM NORTH INDIA DESTINATIONS:")
            logger.info("-" * 40)
            
            # Get all documents with custom tag
            all_docs = rag_service.collection.get(include=['metadatas'])
            custom_destinations = []
            
            for metadata in all_docs.get('metadatas', []):
                if metadata.get('custom') == True and metadata.get('category') == 'custom_north_india':
                    custom_destinations.append(metadata['destination'])
            
            for dest in sorted(set(custom_destinations)):
                logger.info(f"• {dest}")
            
            logger.info(f"Total custom destinations: {len(set(custom_destinations))}")
            
        except Exception as e:
            logger.error(f"❌ Error listing destinations: {e}")
        
        logger.info("=" * 70)
        
        return found_count > 0
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        return False


def search_custom_data(query, top_k=5):
    """
    Search custom data with detailed results
    
    Args:
        query: Search query string
        top_k: Number of results to return
    
    Returns:
        List of search results
    """
    try:
        results = rag_service.retrieve(query, top_k=top_k)
        
        logger.info(f"\n🔍 SEARCH RESULTS FOR: '{query}'")
        logger.info("-" * 70)
        
        if not results:
            logger.info("No results found")
            return []
        
        for i, result in enumerate(results, 1):
            metadata = result['meta']
            distance = result.get('distance', 0)
            similarity_score = f"{100 - (distance * 100):.1f}%" if distance and distance > 0 else "N/A"
            
            logger.info(f"{i}. {metadata['destination']}, {metadata['state']}")
            logger.info(f"   Best Season: {metadata.get('best_season', 'N/A')}")
            logger.info(f"   Budget: {metadata.get('budget', 'N/A')}")
            logger.info(f"   Similarity: {similarity_score}")
            logger.info("")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        return []


def get_destination_details(destination_name):
    """
    Get full details of a specific destination
    
    Args:
        destination_name: Name of destination to retrieve
    
    Returns:
        Dictionary with destination details or None if not found
    """
    try:
        # Search for the destination
        results = rag_service.retrieve(destination_name, top_k=3)
        
        if not results:
            logger.warning(f"❌ Destination '{destination_name}' not found")
            return None
        
        # Find exact match
        exact_match = None
        for result in results:
            if result['meta']['destination'].lower() == destination_name.lower():
                exact_match = result
                break
        
        if not exact_match:
            logger.warning(f"❌ Destination '{destination_name}' not found exactly")
            logger.info(f"Did you mean: {results[0]['meta']['destination']}?")
            exact_match = results[0]  # Return closest match
        
        metadata = exact_match['meta']
        
        # Parse the full data from JSON string
        if 'data_json' in metadata:
            data = json.loads(metadata['data_json'])
            
            logger.info(f"\n📍 {data['destination'].upper()} - COMPLETE DETAILS")
            logger.info("=" * 70)
            
            # Display formatted details
            display_fields = [
                ("State", data.get('state')),
                ("Region", data.get('region')),
                ("Best Season", data.get('best_season')),
                ("Climate", data.get('climate')),
                ("Budget", data.get('budget')),
                ("Transportation", data.get('transportation')),
            ]
            
            for label, value in display_fields:
                if value:
                    logger.info(f"• {label}: {value}")
            
            logger.info("\n🏞️  ATTRACTIONS:")
            for attraction in data.get('attractions', []):
                logger.info(f"  • {attraction}")
            
            logger.info("\n🎯 ACTIVITIES:")
            for activity in data.get('activities', []):
                logger.info(f"  • {activity}")
            
            logger.info("\n🍽️  FOOD SPECIALTIES:")
            for food in data.get('food_specialties', []):
                logger.info(f"  • {food}")
            
            logger.info("\n🎒 PACKING LIST:")
            for item in data.get('packing_list', []):
                logger.info(f"  • {item}")
            
            logger.info("\n💡 TRAVEL TIPS:")
            for tip in data.get('travel_tips', []):
                logger.info(f"  • {tip}")
            
            logger.info("\n🏨 HOTELS:")
            for hotel in data.get('hotels', []):
                logger.info(f"  • {hotel}")
            
            logger.info("=" * 70)
            
            return data
        
        logger.error("❌ No full data found in metadata")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error getting destination details: {e}")
        return None


# ============================================================================
# 🎬 MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🚀 NORTH INDIA CUSTOM DATA FEED SCRIPT")
    logger.info("=" * 70)
    
    # Step 1: Check RAG service availability
    try:
        logger.info("Checking RAG service...")
        # Simple test to verify service is available
        test_query = "test"
        _ = rag_service.retrieve(test_query, top_k=1)
        logger.info("✅ RAG service is available")
    except Exception as e:
        logger.error(f"❌ RAG service not available: {e}")
        logger.info("Please ensure RAG service is properly initialized")
        exit(1)
    
    # Step 2: Feed data to ChromaDB
    logger.info("\n" + "=" * 70)
    logger.info("STEP 1: FEEDING DATA TO CHROMADB")
    logger.info("=" * 70)
    
    success = feed_custom_north_india_data()
    
    # Step 3: Verify data was added
    if success:
        logger.info("\n" + "=" * 70)
        logger.info("STEP 2: VERIFYING DATA")
        logger.info("=" * 70)
        
        verify_data_in_chromadb()
        
        # Step 4: Test functionality
        logger.info("\n" + "=" * 70)
        logger.info("STEP 3: TESTING FUNCTIONALITY")
        logger.info("=" * 70)
        
        # Test search with various queries
        test_queries = [
            "mountain trekking adventure",
            "yoga meditation retreat",
            "desert forts palaces",
            "winter snow skiing",
            "budget travel north india"
        ]
        
        for query in test_queries:
            search_custom_data(query, top_k=2)
        
        # Get details for sample destinations
        logger.info("\n" + "=" * 70)
        logger.info("STEP 4: GETTING DESTINATION DETAILS")
        logger.info("=" * 70)
        
        sample_destinations = ["Ladakh", "Jaipur", "Rishikesh", "Manali"]
        for dest in sample_destinations:
            get_destination_details(dest)
            logger.info("")  # Empty line for spacing
    
    logger.info("\n" + "=" * 70)
    logger.info("✨ SCRIPT EXECUTION COMPLETE")
    logger.info("=" * 70)

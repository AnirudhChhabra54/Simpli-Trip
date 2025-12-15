"""
TEMPLATE: Custom North India Data Feed Script
Copy and modify this for your own data
"""

from services.rag_service import rag_service
from utils.logger import logger
import json

# ============================================================================
# 📝 MODIFY THIS: Your Custom North India Destinations
# ============================================================================

NORTH_INDIA_DESTINATIONS = [
    {
        "destination": "Ladakh",
        "state": "Ladakh",
        "region": "North",
        "best_season": "June to September",
        "climate": "High altitude, cold, dry",
        "attractions": [
            "Pangong Lake - high altitude blue lake",
            "Khardung La - motorable mountain pass",
            "Lamayuru Monastery - ancient Buddhist site",
            "Magnetic Hill - optical illusion"
        ],
        "activities": [
            "Trekking and hiking",
            "Mountain biking",
            "Monastery tours",
            "Stargazing"
        ],
        "budget": "₹2000-3500/day",
        "food_specialties": [
            "Tibetan momos",
            "Thukpa (noodle soup)",
            "Yak meat dishes",
            "Local breads"
        ],
        "packing_list": [
            "Warm clothing layers",
            "High SPF sunscreen",
            "Altitude medicine",
            "Sturdy hiking boots"
        ],
        "travel_tips": [
            "Acclimatize for 2-3 days",
            "Travel only June to September",
            "Book guides in advance",
            "Carry cash for remote areas"
        ],
        "transportation": "Flights via LEH airport or road from Delhi",
        "hotels": ["Budget homestays", "3-4 star hotels in Leh"]
    },
    
    {
        "destination": "Jaipur",
        "state": "Rajasthan",
        "region": "North",
        "best_season": "October to February",
        "climate": "Desert - hot summers, cool winters",
        "attractions": [
            "Hawa Mahal - iconic pink structure",
            "City Palace - royal residence and museum",
            "Amber Fort - hilltop fort with architecture",
            "Jantar Mantar - astronomical observation site",
            "Nahargarh Fort - panoramic views"
        ],
        "activities": [
            "Fort and palace exploration",
            "Elephant rides at Amber Fort",
            "Photography in Pink City",
            "Shopping in local bazaars",
            "Ayurvedic massage"
        ],
        "budget": "₹1200-2500/day",
        "food_specialties": [
            "Jaipur biryani",
            "Dal-baati-churma",
            "Pyaaz ki kachori",
            "Mirchi bada"
        ],
        "packing_list": [
            "Light, breathable clothes",
            "Hat and sunglasses",
            "Walking shoes",
            "High SPF sunscreen"
        ],
        "travel_tips": [
            "Visit forts early morning to avoid crowds",
            "Stay in Pink City area for convenience",
            "Book guides for better tours",
            "Try local eateries for authentic food"
        ],
        "transportation": "Airport: JAI, Train station available, Auto-rickshaws abundant",
        "hotels": ["Budget hotels in Pink City", "Luxury palace hotels"]
    },

    {
        "destination": "Rishikesh",
        "state": "Uttarakhand",
        "region": "North",
        "best_season": "September to March",
        "climate": "Temperate, holy city on Ganges river",
        "attractions": [
            "Laxman Jhula - suspension bridge",
            "Ram Jhula - iconic bridge",
            "Ganges Aarti - evening ritual",
            "Yoga ashrams and meditation centers",
            "Triveni Ghat - sacred bathing spot"
        ],
        "activities": [
            "Yoga and meditation classes",
            "River rafting on Ganges",
            "Temple visits and spiritual tours",
            "Ayurveda treatment and massage",
            "Riverside walks"
        ],
        "budget": "₹1000-2000/day",
        "food_specialties": [
            "South Indian vegetarian cuisine",
            "Ayurvedic food",
            "Street food specialties",
            "Spiritual food at ashrams"
        ],
        "packing_list": [
            "Light, modest clothing",
            "Yoga mat and spiritual wear",
            "Comfortable walking shoes",
            "Sun protection"
        ],
        "travel_tips": [
            "Book yoga classes in advance",
            "Respect local customs and traditions",
            "Visit temples in early morning",
            "Learn basic Sanskrit phrases"
        ],
        "transportation": "Train from Delhi (about 5 hours), Buses available, Taxi from Delhi airport",
        "hotels": ["Budget ashram stays", "Mid-range yoga resorts", "Luxury riverside hotels"]
    }
]

# ============================================================================
# 🚀 RUN THIS: Feed data to ChromaDB
# ============================================================================

def feed_custom_north_india_data():
    """
    Feed your custom North India destinations to ChromaDB
    """
    try:
        logger.info("=" * 70)
        logger.info("🌏 FEEDING CUSTOM NORTH INDIA DATA TO CHROMADB")
        logger.info("=" * 70)
        
        if not rag_service.is_available():
            logger.error("❌ RAG service not available")
            return False
        
        added_count = 0
        
        for dest in NORTH_INDIA_DESTINATIONS:
            try:
                # 1. Convert to searchable text
                knowledge_text = format_for_search(dest)
                
                # 2. Create metadata (preserve all data)
                metadata = {
                    "type": "destination",
                    "destination": dest['destination'],
                    "state": dest.get('state', ''),
                    "region": dest.get('region', 'North'),
                    "best_season": dest.get('best_season', ''),
                    "custom": True,
                    "source": "custom_north_india",
                    "data_json": json.dumps(dest)  # Full data as JSON string
                }
                
                # 3. Create unique ID
                doc_id = f"custom_north_{dest['destination'].lower().replace(' ', '_')}"
                
                # 4. Add to ChromaDB
                rag_service.collection.add(
                    documents=[knowledge_text],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
                
                added_count += 1
                logger.info(f"✅ Added: {dest['destination']} (ID: {doc_id})")
                
            except Exception as e:
                logger.error(f"❌ Error adding {dest.get('destination', 'Unknown')}: {e}")
                continue
        
        logger.info("\n" + "=" * 70)
        logger.info(f"✨ Successfully added {added_count} destinations to ChromaDB!")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return False


def format_for_search(dest):
    """
    Format destination data for vector embeddings and search
    Makes text searchable and semantically meaningful
    """
    parts = [
        f"Destination: {dest['destination']}",
        f"Location: {dest.get('state', '')}",
        f"Region: {dest.get('region', 'North India')}",
        f"Best Time to Visit: {dest.get('best_season', '')}",
        f"Climate: {dest.get('climate', '')}",
        f"\nTop Attractions:\n{format_list(dest.get('attractions', []))}",
        f"\nActivities:\n{format_list(dest.get('activities', []))}",
        f"\nBudget: {dest.get('budget', '')}",
        f"\nLocal Food:\n{format_list(dest.get('food_specialties', []))}",
        f"\nWhat to Pack:\n{format_list(dest.get('packing_list', []))}",
        f"\nTravel Tips:\n{format_list(dest.get('travel_tips', []))}",
        f"\nTransportation: {dest.get('transportation', '')}",
        f"\nHotels: {', '.join(dest.get('hotels', []))}",
    ]
    return "\n".join(parts)


def format_list(items):
    """Convert list to formatted bullet points"""
    return "\n".join([f"• {item}" for item in items])


def verify_data_in_chromadb():
    """
    Verify that your custom data was successfully added
    """
    try:
        logger.info("\n" + "=" * 70)
        logger.info("🔍 VERIFYING DATA IN CHROMADB")
        logger.info("=" * 70)
        
        # Get stats
        stats = rag_service.get_collection_stats()
        logger.info(f"📊 Total documents in ChromaDB: {stats.get('num_documents', 0)}")
        
        # Test search
        test_queries = [
            "north india mountains trekking",
            "beach relax vacation",
            "yoga meditation spiritual"
        ]
        
        for query in test_queries:
            results = rag_service.retrieve(query, top_k=1)
            if results:
                dest = results[0]['metadata']['destination']
                logger.info(f"✅ Query '{query}' → Found: {dest}")
            else:
                logger.warning(f"⚠️ No results for query: {query}")
        
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")


def search_custom_data(query, top_k=5):
    """
    Search your custom data by query
    
    Example:
        results = search_custom_data("mountain trekking adventure")
    """
    try:
        results = rag_service.retrieve(query, top_k=top_k)
        
        logger.info(f"\n🔍 Search Results for: '{query}'")
        logger.info("-" * 70)
        
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            dest = metadata['destination']
            state = metadata['state']
            logger.info(f"{i}. {dest}, {state}")
            logger.info(f"   Best Season: {metadata.get('best_season', 'N/A')}")
            logger.info(f"   Similarity Score: {result.get('distance', 'N/A')}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        return []


def get_destination_details(destination_name):
    """
    Get full details of a destination from ChromaDB
    
    Example:
        details = get_destination_details("Ladakh")
    """
    try:
        results = rag_service.retrieve(destination_name, top_k=1)
        
        if results:
            metadata = results[0]['metadata']
            if 'data_json' in metadata:
                data = json.loads(metadata['data_json'])
                logger.info(f"\n📍 {destination_name} - Full Details:")
                logger.info(json.dumps(data, indent=2, ensure_ascii=False))
                return data
        
        logger.warning(f"❌ Destination not found: {destination_name}")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error getting details: {e}")
        return None


# ============================================================================
# 🎬 MAIN: Run when you execute this script
# ============================================================================

if __name__ == "__main__":
    # Step 1: Feed data to ChromaDB
    success = feed_custom_north_india_data()
    
    # Step 2: Verify data was added
    if success:
        verify_data_in_chromadb()
        
        # Step 3: Test search (optional)
        logger.info("\n" + "=" * 70)
        logger.info("🧪 TESTING SEARCH FUNCTIONALITY")
        logger.info("=" * 70)
        
        search_custom_data("north india adventure trekking")
        get_destination_details("Ladakh")
    
    logger.info("\n✨ SCRIPT COMPLETE!")

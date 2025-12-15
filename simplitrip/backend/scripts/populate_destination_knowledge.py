"""
Populate ChromaDB with destination knowledge for RAG system
This enables semantic search for travel recommendations and destination context
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.rag_service import rag_service
from utils.logger import logger

# Comprehensive Indian destination knowledge base
DESTINATION_KNOWLEDGE = {
    "Goa": {
        "state": "Goa",
        "best_season": "November to February",
        "climate": "Tropical, hot and humid. Monsoon June-September",
        "attractions": [
            "Baga Beach - water sports, nightlife",
            "Palolem Beach - peaceful, palm-fringed",
            "Fort Aguada - historic lighthouse",
            "Basilica of Bom Jesus - religious landmark",
            "Dudhsagar Falls - spectacular waterfalls",
            "Casino - night entertainment"
        ],
        "activities": [
            "Beach relaxation and swimming",
            "Water sports - parasailing, jet skiing",
            "Spice plantation tours",
            "Dolphin cruises",
            "Bar and club hopping",
            "Portuguese cuisine tasting"
        ],
        "budget": "Budget: ₹1500-3000/day, Mid: ₹3000-6000/day, Luxury: ₹6000+/day",
        "transportation": "Flights via GOI airport, Auto-rickshaws and taxis available",
        "packing": "Light clothes, swimwear, sunscreen, rain gear during monsoon",
        "food": "Fresh seafood, Goan curries, Portuguese influence, pizza and pasta",
        "tips": "Avoid peak season for crowds, Book accommodations in advance, Try local shacks for authentic food"
    },
    
    "Udaipur": {
        "state": "Rajasthan",
        "best_season": "October to March",
        "climate": "Arid with hot summers. Pleasant in winter",
        "attractions": [
            "Lake Pichola - boat rides and sunset views",
            "City Palace - stunning architecture",
            "Jagmandir Island Palace - romantic destination",
            "Saheliyon ki Bari - ornamental garden",
            "Shilpgram - traditional crafts",
            "Monsoon Palace - panoramic views"
        ],
        "activities": [
            "Boat rides on Lake Pichola",
            "Visit historical palaces",
            "Shopping for jewelry and textiles",
            "Photography and sunset viewing",
            "Yoga and meditation",
            "Folk dance performances"
        ],
        "budget": "Budget: ₹1500-2500/day, Mid: ₹2500-5000/day, Luxury: ₹5000+/day",
        "transportation": "Nearest airport: Jaipur (250km), Bus services, Taxi available",
        "packing": "Light clothing for day, warm layers for evening, comfortable shoes",
        "food": "Rajasthani cuisine, Dal-baati-churma, Gatte ki sabzi, local sweets",
        "tips": "Stay near lake for best views, Early morning walks are peaceful, Book palace hotels for luxury experience"
    },
    
    "Jaipur": {
        "state": "Rajasthan",
        "best_season": "October to February",
        "climate": "Desert climate, hot summers, cool winters",
        "attractions": [
            "Hawa Mahal - Pink City's iconic structure",
            "City Palace - royal residence",
            "Jantar Mantar - astronomical observation site",
            "Amber Fort - hilltop fort with architecture",
            "Nahargarh Fort - panoramic views",
            "Central Museum - art and history"
        ],
        "activities": [
            "Fort and palace exploration",
            "Elephant rides at Amber Fort",
            "Photography of Pink City",
            "Shopping in local bazaars",
            "Ayurvedic massage",
            "Classical music concerts"
        ],
        "budget": "Budget: ₹1200-2500/day, Mid: ₹2500-5000/day, Luxury: ₹5000+/day",
        "transportation": "Airport: JAI, Train station, Auto-rickshaws and taxis abundant",
        "packing": "Light, breathable clothes, hat and sunglasses, walking shoes",
        "food": "Jaipur biryani, Dal-baati, Mirchi bada, Pyaaz ki kachori",
        "tips": "Visit Amber Fort early morning to avoid crowds, Stay in Pink City area, Book guides for fort visits"
    },
    
    "Kerala": {
        "state": "Kerala",
        "best_season": "November to January (cool and dry)",
        "climate": "Tropical with monsoon. Monsoon June-August refreshing",
        "attractions": [
            "Backwaters - serene houseboat cruises",
            "Munnar - tea plantations and hills",
            "Alleppey Beach - scenic and peaceful",
            "Thekkady - wildlife sanctuary",
            "Kochi Fort - historic area",
            "Athirapally Falls - powerful waterfalls"
        ],
        "activities": [
            "Houseboat cruises through backwaters",
            "Tea plantation tours",
            "Beach walks and swimming",
            "Ayurveda massage and wellness",
            "Wildlife spotting",
            "Spice garden tours"
        ],
        "budget": "Budget: ₹2000-3500/day, Mid: ₹3500-6000/day, Luxury: ₹6000+/day",
        "transportation": "Flights via COK airport, Backwaters transportation, Taxis and auto available",
        "packing": "Light clothes for heat, rain jacket for monsoon, comfortable shoes",
        "food": "Appam, sambar, fish curries, coconut-based dishes, fresh seafood",
        "tips": "Visit during green monsoon for beauty, Book houseboats in advance, Try Ayurveda treatments"
    },
    
    "Delhi": {
        "state": "Delhi",
        "best_season": "October to March",
        "climate": "Temperate with hot summers, cool winters, moderate rainfall",
        "attractions": [
            "Red Fort - Mughal era fort",
            "Jama Masjid - historic mosque",
            "India Gate - colonial monument",
            "Raj Ghat - Gandhi memorial",
            "Qutub Minar - tallest minaret",
            "National Museum - art and history"
        ],
        "activities": [
            "Historical monument tours",
            "Museum exploration",
            "Shopping in Chandni Chowk",
            "Market street food",
            "Yoga and meditation at ashrams",
            "Night sightseeing tours"
        ],
        "budget": "Budget: ₹1500-3000/day, Mid: ₹3000-6000/day, Luxury: ₹6000+/day",
        "transportation": "Major hub - flights, trains, Metro system, Taxis and auto-rickshaws",
        "packing": "Layers for winter, sunscreen for summer, umbrella for rain",
        "food": "Chaat, samosa, butter chicken, biryani, street food varieties",
        "tips": "Use Metro for easy commute, Avoid peak summer season, Start Old Delhi tour early"
    },
    
    "Mumbai": {
        "state": "Maharashtra",
        "best_season": "November to February",
        "climate": "Tropical monsoon climate. Monsoon July-September",
        "attractions": [
            "Gateway of India - iconic monument",
            "Marine Drive - scenic boulevard",
            "Taj Mahal Palace Hotel - historic luxury",
            "Bandra-Worli Sea Link - architectural marvel",
            "Haji Ali - mosque in sea",
            "Chhatrapati Shivaji Terminal - UNESCO site"
        ],
        "activities": [
            "Beach promenades at Marine Drive",
            "Film city tours",
            "Island hopping - Elephanta Caves",
            "Shopping in malls and markets",
            "Nightlife - bars and clubs",
            "Street food tours"
        ],
        "budget": "Budget: ₹2000-3500/day, Mid: ₹3500-7000/day, Luxury: ₹7000+/day",
        "transportation": "Major airport: BOM, Local trains, Metro system, Taxis and Uber",
        "packing": "Light clothes for humidity, rain jacket for monsoon, comfortable shoes",
        "food": "Street food - vada pav, pav bhaji, Mumbai biryani, fresh seafood",
        "tips": "Use local trains for authentic experience, Visit early morning for freshness, Book hotels near Metro"
    },
    
    "Bangalore": {
        "state": "Karnataka",
        "best_season": "October to March",
        "climate": "Pleasant year-round, rain during monsoon",
        "attractions": [
            "Vidhana Soudha - legislative building",
            "Lalbagh Botanical Garden - flower displays",
            "Ulsoor Lake - recreational area",
            "Tipu Sultan's Palace - historic monument",
            "St. Mary's Basilica - religious site",
            "Tech parks - modern malls and eateries"
        ],
        "activities": [
            "Garden tours and photography",
            "Café hopping in MG Road",
            "IT park visits",
            "Nightlife - bars and clubs",
            "Outdoor activities - trekking",
            "Shopping malls and markets"
        ],
        "budget": "Budget: ₹1500-3000/day, Mid: ₹3000-6000/day, Luxury: ₹6000+/day",
        "transportation": "Airport: BLR, Metro system, Taxis, Auto-rickshaws",
        "packing": "Light clothes, jacket for cool evenings, umbrella for rain",
        "food": "South Indian - dosa, sambar, idli, ragi, biryanis, cosmopolitan cuisines",
        "tips": "Visit gardens during flower season, Use Metro for commute, Try local eateries for authentic food"
    },
    
    "Ladakh": {
        "state": "Ladakh",
        "best_season": "June to September",
        "climate": "High altitude, cold winters, dry climate",
        "attractions": [
            "Pangong Lake - high altitude blue lake",
            "Magnetic Hill - optical illusion site",
            "Khardung La - highest motorable pass",
            "Lamayuru Monastery - ancient Buddhist site",
            "Nubra Valley - sand dunes and glaciers",
            "Thiksey Monastery - scenic monastery"
        ],
        "activities": [
            "Mountain biking and trekking",
            "High altitude exploration",
            "Buddhist monastery tours",
            "Photography of landscapes",
            "Stargazing - very clear skies",
            "Cultural tours and homestays"
        ],
        "budget": "Budget: ₹2000-3500/day, Mid: ₹3500-6000/day, Luxury: ₹6000+/day",
        "transportation": "Flights via LEH airport, Road travel, Bike rentals available",
        "packing": "Warm clothes, layers, sunscreen, high SPF, altitude medicine, sturdy shoes",
        "food": "Tibetan momos, thukpa soup, tsampa, local breads, yak meat dishes",
        "tips": "Acclimatize properly before activity, Carry cash for remote areas, Travel during summer season only"
    },
    
    "Manali": {
        "state": "Himachal Pradesh",
        "best_season": "March to October",
        "climate": "Temperate mountain climate, snow in winter",
        "attractions": [
            "Solang Valley - adventure activities",
            "Rohtang Pass - panoramic mountain pass",
            "Hadimba Temple - ancient wooden temple",
            "Old Manali - bohemian atmosphere",
            "Bhrigu Lake - high altitude meadow",
            "Manu Temple - spiritual site"
        ],
        "activities": [
            "Trekking and hiking",
            "Paragliding and adventure sports",
            "Mountain biking",
            "Monastery tours",
            "Hot spring visits",
            "Photography of landscape"
        ],
        "budget": "Budget: ₹1200-2500/day, Mid: ₹2500-5000/day, Luxury: ₹5000+/day",
        "transportation": "Nearest airport: Bhuntar (50km), Bus services, Taxis, Car rentals",
        "packing": "Warm layers, waterproof jacket, hiking boots, hat and gloves",
        "food": "Himachali cuisine, trout fish, momos, rajma, local breads",
        "tips": "Visit during summer for best weather, Book hotels in advance, Hire local guides for treks"
    }
}

def populate_destination_knowledge():
    """
    Populate ChromaDB with destination knowledge
    This enables RAG system to provide context for destination recommendations
    """
    try:
        logger.info("🚀 Starting destination knowledge population...")
        
        if not rag_service.is_available():
            logger.error("❌ RAG service not available")
            return False
        
        added_count = 0
        
        for destination, knowledge in DESTINATION_KNOWLEDGE.items():
            try:
                # Create comprehensive knowledge text for embeddings
                knowledge_text = f"""
Destination: {destination}
State: {knowledge.get('state', 'N/A')}
Best Season: {knowledge.get('best_season', 'N/A')}
Climate: {knowledge.get('climate', 'N/A')}

Attractions: {', '.join(knowledge.get('attractions', []))}

Activities: {', '.join(knowledge.get('activities', []))}

Budget: {knowledge.get('budget', 'N/A')}

Transportation: {knowledge.get('transportation', 'N/A')}

Food: {knowledge.get('food', 'N/A')}

Packing: {knowledge.get('packing', 'N/A')}

Tips: {knowledge.get('tips', 'N/A')}
                """
                
                # Prepare metadata as JSON string for ChromaDB
                metadata = {
                    "type": "destination",
                    "destination": destination,
                    "state": knowledge.get("state", ""),
                    "best_season": knowledge.get("best_season", ""),
                    "popularity": "high",
                    "data_json": json.dumps(knowledge),  # Full knowledge as JSON
                    "timestamp": datetime.now().isoformat()
                }
                
                # Create unique ID for destination
                doc_id = f"dest_{destination.lower().replace(' ', '_')}"
                
                # Add to ChromaDB
                rag_service.collection.add(
                    documents=[knowledge_text],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
                
                added_count += 1
                logger.info(f"✅ Added knowledge for {destination}")
                
            except Exception as e:
                logger.error(f"❌ Error adding {destination}: {e}")
                continue
        
        logger.info(f"✨ Successfully populated {added_count} destinations in ChromaDB")
        return added_count > 0
        
    except Exception as e:
        logger.error(f"❌ Error populating destination knowledge: {e}")
        return False


def verify_population():
    """Verify that destination knowledge was added to ChromaDB"""
    try:
        if not rag_service.is_available():
            logger.error("❌ RAG service not available")
            return False
        
        stats = rag_service.get_collection_stats()
        logger.info(f"📊 ChromaDB Collection Stats: {stats}")
        
        if stats and stats.get("num_documents", 0) > 0:
            logger.info(f"✅ ChromaDB has {stats['num_documents']} documents")
            return True
        else:
            logger.warning("⚠️ ChromaDB appears empty")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error verifying population: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Destination Knowledge Population Script")
    logger.info("=" * 60)
    
    # Populate destination knowledge
    success = populate_destination_knowledge()
    
    if success:
        logger.info("\n" + "=" * 60)
        logger.info("Verifying population...")
        logger.info("=" * 60)
        verify_population()
    
    logger.info("\n" + "=" * 60)
    logger.info("Population script completed!")
    logger.info("=" * 60)

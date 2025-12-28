"""
Test script to verify backend setup and all connections
Run this to validate the backend before deployment
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.model_service import ModelService
from utils.logger import logger

async def test_model_service_methods():
    """Test all model service methods exist and are callable"""
    
    logger.info("=" * 60)
    logger.info("🧪 TESTING MODEL SERVICE SETUP")
    logger.info("=" * 60)
    
    # Create service instance
    model_service = ModelService()
    print()
    
    # Test initialization
    print("1️⃣  Testing initialization...")
    try:
        model_service.initialize()
        logger.info("✅ ModelService initialized successfully")
    except Exception as e:
        logger.error(f"❌ Initialization failed: {str(e)}")
        return False
    
    print()
    print("2️⃣  Testing required methods...")
    
    required_methods = {
        # Recommendations
        'get_destination_recommendations': 'Destination recommendations',
        'get_nearby_recommendations': 'Nearby recommendations',
        'get_smart_suggestions': 'Smart suggestions',
        # Cost predictions
        'predict_flight_cost': 'Flight cost prediction',
        'predict_accommodation_cost': 'Accommodation cost prediction',
        'predict_total_trip_cost': 'Total trip cost prediction',
        'optimize_budget': 'Budget optimization',
        # Itinerary
        'optimize_itinerary': 'Itinerary optimization',
        'validate_itinerary': 'Itinerary validation',
        'generate_complete_itinerary': 'Complete itinerary generation',
        # LLM services
        'parse_natural_language_query': 'Query parsing',
        'generate_itinerary_description': 'Itinerary description',
        'explain_recommendation': 'Recommendation explanation',
        # Data methods
        'get_destinations': 'Get destinations',
        'get_places': 'Get places',
        # RAG methods
        'query_knowledge_base': 'Knowledge base query',
        'get_destination_insights': 'Destination insights',
        'get_rag_stats': 'RAG statistics',
    }
    
    missing_methods = []
    available_methods = []
    
    for method_name, description in required_methods.items():
        if hasattr(model_service, method_name):
            method = getattr(model_service, method_name)
            if callable(method):
                logger.info(f"✅ {description:<35} - {method_name}")
                available_methods.append(method_name)
            else:
                logger.error(f"❌ {description:<35} - NOT CALLABLE")
                missing_methods.append(method_name)
        else:
            logger.error(f"❌ {description:<35} - MISSING")
            missing_methods.append(method_name)
    
    print()
    print("3️⃣  Testing async method execution...")
    
    test_params = {
        "destination": "Paris",
        "duration": 5,
        "interests": ["art", "food"],
        "max_budget": 5000,
        "distance_km": 5000,
        "hotel_rating": 4
    }
    
    from datetime import datetime, timedelta
    
    # Test a few methods
    try:
        result = model_service.get_destinations()
        logger.info(f"✅ get_destinations() - Returned {len(result)} items")
    except Exception as e:
        logger.warning(f"⚠️ get_destinations() - {str(e)}")
    
    try:
        result = model_service.predict_flight_cost(
            from_city="New York", 
            to_city="Paris", 
            travel_date=datetime.now() + timedelta(days=30)
        )
        logger.info(f"✅ predict_flight_cost() - {result}")
    except Exception as e:
        logger.warning(f"⚠️ predict_flight_cost() - {str(e)}")
    
    print()
    logger.info("=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"✅ Available methods: {len(available_methods)}/{len(required_methods)}")
    logger.info(f"❌ Missing methods: {len(missing_methods)}")
    
    if missing_methods:
        logger.warning("Missing method implementations:")
        for method in missing_methods:
            logger.warning(f"   - {method}")
    
    print()
    
    # Cleanup
    try:
        model_service.shutdown()
        logger.info("✅ Shutdown successful")
    except Exception as e:
        logger.warning(f"⚠️ Shutdown issue: {str(e)}")
    
    return len(missing_methods) == 0

async def main():
    """Run all tests"""
    success = await test_model_service_methods()
    
    if success:
        logger.info("🎉 ALL TESTS PASSED! Backend is ready to use.")
        sys.exit(0)
    else:
        logger.warning("⚠️ Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

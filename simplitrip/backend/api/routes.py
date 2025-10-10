"""
API Routes for SimpliTrip Backend
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import Dict, Any
import uuid

from api.schemas import (
    RecommendationRequest, RecommendationResponse, DestinationRecommendation,
    FlightCostRequest, FlightCostResponse,
    AccommodationCostRequest, AccommodationCostResponse,
    TripCostRequest, TripCostResponse,
    BudgetOptimizationRequest, BudgetOptimizationResponse,
    ItineraryOptimizationRequest, ItineraryOptimizationResponse,
    ItineraryValidationResponse,
    NaturalLanguageQueryRequest, ParsedQuery,
    DescriptionGenerationRequest, DescriptionGenerationResponse,
    RecommendationExplanationRequest, RecommendationExplanationResponse,
    HealthCheckResponse, ErrorResponse
)
from services.model_service import ModelService
from services.web_scraper import destination_scraper
from utils.logger import logger

# Create router
router = APIRouter()

# Initialize model service (will be injected)
model_service = ModelService()


# Health Check
@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now()
    )


# Recommendation Endpoints
@router.post("/recommendations/destinations", response_model=RecommendationResponse)
async def get_destination_recommendations(request: RecommendationRequest):
    """
    Get destination recommendations based on user preferences
    """
    try:
        logger.info(f"Recommendation request: {request.dict()}")
        
        # Get recommendations from model service
        recommendations = model_service.get_recommendations(
            preferences={
                'category': request.category,
                'state': request.state,
                'best_time': request.best_time,
                'budget': request.budget
            },
            user_id=request.user_id,
            top_n=request.top_n,
            exclude_destinations=request.exclude_destinations
        )
        
        # Convert to response format
        recommendation_objects = [
            DestinationRecommendation(**rec) for rec in recommendations
        ]
        
        return RecommendationResponse(
            recommendations=recommendation_objects,
            total_count=len(recommendation_objects),
            request_id=str(uuid.uuid4())
        )
        
    except Exception as e:
        logger.error(f"Error in get_destination_recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/nearby")
async def get_nearby_recommendations(
    destination: str,
    category: str = None,
    top_n: int = 5
):
    """
    Get nearby attraction recommendations for a destination
    """
    try:
        logger.info(f"Nearby recommendations request for: {destination}")
        
        # Get nearby recommendations
        recommendations = model_service.get_nearby_recommendations(
            destination=destination,
            category=category,
            top_n=top_n
        )
        
        return {
            "destination": destination,
            "recommendations": recommendations,
            "total_count": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Error in get_nearby_recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Cost Prediction Endpoints
@router.post("/predictions/flight-cost", response_model=FlightCostResponse)
async def predict_flight_cost(request: FlightCostRequest):
    """
    Predict flight cost for given route and date
    """
    try:
        logger.info(f"Flight cost prediction: {request.from_city} -> {request.to_city}")
        
        result = model_service.predict_flight_cost(
            from_city=request.from_city,
            to_city=request.to_city,
            travel_date=request.travel_date,
            booking_date=request.booking_date,
            num_travelers=request.num_travelers
        )
        
        return FlightCostResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in predict_flight_cost: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predictions/accommodation-cost", response_model=AccommodationCostResponse)
async def predict_accommodation_cost(request: AccommodationCostRequest):
    """
    Predict accommodation cost
    """
    try:
        logger.info(f"Accommodation cost prediction for: {request.destination}")
        
        result = model_service.predict_accommodation_cost(
            destination=request.destination,
            accommodation_type=request.accommodation_type,
            star_rating=request.star_rating,
            duration_nights=request.duration_nights,
            travel_date=request.travel_date,
            budget_category=request.budget_category
        )
        
        return AccommodationCostResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in predict_accommodation_cost: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predictions/total-cost", response_model=TripCostResponse)
async def predict_total_trip_cost(request: TripCostRequest):
    """
    Predict total trip cost with breakdown
    """
    try:
        logger.info(f"Total trip cost prediction: {request.from_city} -> {request.to_city}")
        
        result = model_service.predict_total_trip_cost(
            from_city=request.from_city,
            to_city=request.to_city,
            travel_date=request.travel_date,
            return_date=request.return_date,
            num_travelers=request.num_travelers,
            accommodation_type=request.accommodation_type,
            star_rating=request.star_rating,
            budget_category=request.budget_category,
            meal_preference=request.meal_preference,
            include_activities=request.include_activities
        )
        
        return TripCostResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in predict_total_trip_cost: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predictions/optimize-budget", response_model=BudgetOptimizationResponse)
async def optimize_budget(request: BudgetOptimizationRequest):
    """
    Get budget optimization suggestions
    """
    try:
        logger.info(f"Budget optimization request for target: {request.target_budget}")
        
        result = model_service.optimize_budget(
            current_cost=request.current_cost,
            target_budget=request.target_budget,
            flexibility=request.flexibility
        )
        
        return BudgetOptimizationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in optimize_budget: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Itinerary Endpoints
@router.post("/itinerary/optimize", response_model=ItineraryOptimizationResponse)
async def optimize_itinerary(request: ItineraryOptimizationRequest):
    """
    Optimize itinerary using TSP algorithm
    """
    try:
        logger.info(f"Itinerary optimization for {len(request.places)} places")
        
        # Convert Pydantic models to dicts
        places = [place.dict() for place in request.places]
        start_location = request.start_location.dict() if request.start_location else None
        
        result = model_service.optimize_itinerary(
            places=places,
            start_location=start_location,
            num_days=request.num_days,
            daily_time_budget=request.daily_time_budget
        )
        
        return ItineraryOptimizationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in optimize_itinerary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/itinerary/validate", response_model=ItineraryValidationResponse)
async def validate_itinerary(itinerary: Dict[str, Any]):
    """
    Validate itinerary feasibility
    """
    try:
        logger.info("Itinerary validation request")
        
        result = model_service.validate_itinerary(itinerary)
        
        return ItineraryValidationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in validate_itinerary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# LLM Endpoints
@router.post("/llm/parse-query", response_model=ParsedQuery)
async def parse_natural_language_query(request: NaturalLanguageQueryRequest):
    """
    Parse natural language travel query
    """
    try:
        logger.info(f"Parsing query: {request.query}")
        
        result = model_service.parse_natural_language_query(request.query)
        
        return ParsedQuery(**result)
        
    except Exception as e:
        logger.error(f"Error in parse_natural_language_query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/llm/generate-description", response_model=DescriptionGenerationResponse)
async def generate_itinerary_description(request: DescriptionGenerationRequest):
    """
    Generate engaging description for itinerary
    """
    try:
        logger.info("Generating itinerary description")
        
        result = model_service.generate_itinerary_description(
            itinerary=request.itinerary,
            style=request.style
        )
        
        return DescriptionGenerationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in generate_itinerary_description: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/llm/explain-recommendation", response_model=RecommendationExplanationResponse)
async def explain_recommendation(request: RecommendationExplanationRequest):
    """
    Explain why a destination is recommended
    """
    try:
        logger.info(f"Explaining recommendation for: {request.destination}")
        
        result = model_service.explain_recommendation(
            destination=request.destination,
            user_profile=request.user_profile
        )
        
        return RecommendationExplanationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in explain_recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Data Endpoints
@router.get("/data/destinations")
async def get_destinations(
    state: str = None,
    category: str = None,
    limit: int = 100
):
    """
    Get destination data
    """
    try:
        destinations = model_service.get_destinations(
            state=state,
            category=category,
            limit=limit
        )
        
        return {
            "destinations": destinations,
            "total_count": len(destinations)
        }
        
    except Exception as e:
        logger.error(f"Error in get_destinations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/places")
async def get_places(
    destination: str = None,
    category: str = None,
    limit: int = 100
):
    """
    Get places/attractions data
    """
    try:
        places = model_service.get_places(
            destination=destination,
            category=category,
            limit=limit
        )
        
        return {
            "places": places,
            "total_count": len(places)
        }
        
    except Exception as e:
        logger.error(f"Error in get_places: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# RAG / Knowledge Base Endpoints
@router.post("/rag/query")
async def query_knowledge_base(request: Dict[str, Any]):
    """
    Query the RAG knowledge base with a question
    """
    try:
        question = request.get('question', '')
        destination = request.get('destination')
        
        logger.info(f"RAG query: {question}")
        
        result = model_service.query_knowledge_base(
            question=question,
            destination=destination
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in query_knowledge_base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rag/destination-info/{destination}")
async def get_destination_info(destination: str):
    """
    Get comprehensive destination information from RAG
    """
    try:
        logger.info(f"Getting destination info for: {destination}")
        
        result = model_service.get_destination_insights(destination)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_destination_info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rag/stats")
async def get_rag_stats():
    """
    Get RAG knowledge base statistics
    """
    try:
        from services.rag_service import rag_service
        stats = rag_service.get_collection_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error in get_rag_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Smart Workflow Endpoints
@router.post("/recommendations/smart-suggest")
async def smart_destination_suggestions(request: Dict[str, Any]):
    """
    Smart destination suggestions based on parsed intent
    Uses RAG + recommendation model
    """
    try:
        budget = request.get('budget')
        duration = request.get('duration')
        preferences = request.get('preferences', [])
        season = request.get('season')
        travelers = request.get('travelers', 1)
        
        logger.info(f"Smart suggestions for: budget={budget}, preferences={preferences}")
        
        # Get recommendations from model service
        suggestions = model_service.get_smart_suggestions(
            budget=budget,
            duration=duration,
            preferences=preferences,
            season=season,
            travelers=travelers,
            top_n=5
        )
        
        return {
            "suggestions": suggestions,
            "total_count": len(suggestions)
        }
        
    except Exception as e:
        logger.error(f"Error in smart_destination_suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/itinerary/generate-complete")
async def generate_complete_itinerary(request: Dict[str, Any]):
    """
    Generate complete itinerary with day-by-day plans and cost breakdown
    Uses RAG for destination info + LLM for generation
    """
    try:
        destination = request.get('destination')
        duration = request.get('duration')
        budget = request.get('budget')
        travelers = request.get('travelers', 1)
        preferences = request.get('preferences', [])
        accommodation_type = request.get('accommodation_type', 'hotel')
        meal_preference = request.get('meal_preference', 'veg')
        
        logger.info(f"Generating itinerary for {destination}, {duration} days")
        
        # Generate using model service
        itinerary = model_service.generate_complete_itinerary(
            destination=destination,
            duration=duration,
            budget=budget,
            travelers=travelers,
            preferences=preferences,
            accommodation_type=accommodation_type,
            meal_preference=meal_preference
        )
        
        return {
            "itinerary": itinerary,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error in generate_complete_itinerary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Web Scraping Endpoints
@router.post("/scraper/search-destinations")
async def search_destinations_by_query(request: Dict[str, Any]):
    """
    Search and scrape destinations based on parsed query
    Returns real-time destination data with costs, attractions, etc.
    """
    try:
        query_params = request.get('query_params', {})
        
        logger.info(f"Scraping destinations for query: {query_params}")
        
        # Search destinations using web scraper
        results = destination_scraper.search_destinations_by_query(query_params)
        
        return {
            "destinations": results,
            "total_count": len(results),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error in search_destinations_by_query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scraper/destination-details")
async def get_scraped_destination_details(request: Dict[str, Any]):
    """
    Get detailed scraped information for a specific destination
    """
    try:
        destination_name = request.get('destination')
        query_params = request.get('query_params', {})
        
        logger.info(f"Scraping details for: {destination_name}")
        
        # Scrape destination info
        details = destination_scraper.scrape_destination_info(destination_name, query_params)
        
        return {
            "destination": destination_name,
            "details": details,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error in get_scraped_destination_details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

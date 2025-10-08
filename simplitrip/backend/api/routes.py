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

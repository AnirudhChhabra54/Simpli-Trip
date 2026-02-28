"""
API Routes for SimpliTrip Backend
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid
import os
from pydantic import BaseModel

# Schema imports (assuming api/schemas.py exists, if not we define fallbacks below)
try:
    from api.schemas import *
except ImportError:
    # Fallback schemas if file is missing/incomplete during refactor
    from pydantic import BaseModel
    class NaturalLanguageQueryRequest(BaseModel): query: str
    class ParsedQuery(BaseModel): pass 
    class HealthCheckResponse(BaseModel): 
        status: str
        version: str
        timestamp: datetime
    # (Add others as needed or rely on dynamic dicts for now)

from services.model_service import model_service
from services.dialog_manager import dialog_manager  # Added for Chat
from services.rag_service import rag_service
from services.lmstudio_service import lmstudio_service # Added for Health Check
from utils.logger import logger

# Create router
router = APIRouter()

# --- 1. System Health ---

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint - Verifies RAG and LM Studio"""
    rag_ok = False
    llm_ok = False
    
    # Check RAG
    try:
        rag_ok = rag_service.is_available()
    except Exception:
        rag_ok = False
        
    # Check LM Studio (Replaces Ollama)
    try:
        llm_ok = lmstudio_service.is_available() if lmstudio_service is not None else False
    except Exception:
        llm_ok = False

    status = "healthy" if rag_ok and llm_ok else "degraded"
    
    return HealthCheckResponse(
        status=status,
        version="1.0.0",
        timestamp=datetime.now()
    )


# --- 2. AI Chat Assistant (New) ---

class ChatMessage(BaseModel):
    """Chat message request body"""
    session_id: str
    message: str


@router.post("/chat/start")
async def start_chat(body: ChatMessage):
    """Start a conversational planning session"""
    try:
        if dialog_manager is None:
            raise HTTPException(status_code=501, detail="Dialog manager not available")
        return dialog_manager.start_session(body.session_id, body.message)
    except Exception as e:
        logger.error(f"Chat start error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/continue")
async def continue_chat(body: ChatMessage):
    """Continue an existing conversation.
    
    Sends the user's message directly to LM Studio and returns the LLM's plain text reply.
    """
    try:
        if dialog_manager is None:
            raise HTTPException(status_code=501, detail="Dialog manager not available")
        reply = dialog_manager.continue_session(body.session_id, body.message)
        # Return both the text reply and the session id for frontend continuity
        return {
            "session_id": body.session_id,
            "reply": reply,
            "message": reply  # Also include as 'message' for flexibility
        }
    except Exception as e:
        logger.error(f"Chat continue error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- 3. LLM Services (Parsing & Generation) ---

class ModelSelectRequest(BaseModel):
    model: str

@router.get("/llm/models")
async def list_llm_models():
    """List every model the connected LM Studio server has loaded, with connection status."""
    try:
        result = lmstudio_service["list_models"]()
        return {
            "connected": result.get("available", False),
            "host": os.environ.get("LMSTUDIO_HOST", "http://localhost:1234") + "/v1",
            "current_model": result.get("current"),
            "models": result.get("models", []),
        }
    except Exception as e:
        logger.error(f"Error listing LLM models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/llm/models/select")
async def select_llm_model(request: ModelSelectRequest):
    """Switch the active model used for chat and generation."""
    try:
        current = lmstudio_service["set_current_model"](request.model)
        return {
            "current_model": current,
            "host": os.environ.get("LMSTUDIO_HOST", "http://localhost:1234") + "/v1",
        }
    except Exception as e:
        logger.error(f"Error selecting LLM model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/llm/parse-query") # Matches your frontend
async def parse_natural_language_query(request: NaturalLanguageQueryRequest):
    """
    Parse natural language travel query using LM Studio
    Input: "Goa for 3 days under 20k"
    """
    try:
        logger.info(f"Parsing query: {request.query}")
        result = model_service.parse_natural_language_query(request.query)
        # Ensure result matches ParsedQuery schema or return dict
        return result
    except Exception as e:
        logger.error(f"Error in parse_natural_language_query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/llm/generate-description")
async def generate_itinerary_description(request: DescriptionGenerationRequest):
    """Generate engaging description for itinerary"""
    try:
        result = model_service.generate_itinerary_description(
            itinerary=request.itinerary,
            style=request.style
        )
        return result
    except Exception as e:
        logger.error(f"Error in generate_itinerary_description: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/llm/explain-recommendation")
async def explain_recommendation(request: RecommendationExplanationRequest):
    """Explain why a destination is recommended"""
    try:
        result = model_service.explain_recommendation(
            destination=request.destination,
            user_profile=request.user_profile
        )
        return result
    except Exception as e:
        logger.error(f"Error in explain_recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- 4. Core Travel Logic (Recommendations & Cost) ---

@router.post("/recommendations/destinations")
async def get_destination_recommendations(request: RecommendationRequest):
    try:
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
        return {
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "request_id": str(uuid.uuid4())
        }
    except Exception as e:
        logger.error(f"Error in get_destination_recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommendations/nearby")
async def get_nearby_recommendations(destination: str = None, category: str = None, top_n: int = 5, body: Dict[str, Any] = {}):
    try:
        # Accept either query params or a JSON body (frontend sends a body).
        if not destination:
            destination = body.get("destination")
        if category is None:
            category = body.get("category")
        if "top_n" in body:
            top_n = body.get("top_n", 5)
        if not destination:
            raise HTTPException(status_code=400, detail="destination is required")

        recommendations = model_service.get_nearby_recommendations(
            destination=destination,
            category=category,
            top_n=top_n
        )
        return {"destination": destination, "recommendations": recommendations}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_nearby_recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predictions/flight-cost")
async def predict_flight_cost(request: FlightCostRequest):
    try:
        result = model_service.predict_flight_cost(
            from_city=request.from_city,
            to_city=request.to_city,
            travel_date=request.travel_date,
            booking_date=request.booking_date,
            num_travelers=request.num_travelers
        )
        return result
    except Exception as e:
        logger.error(f"Error in predict_flight_cost: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predictions/accommodation-cost")
async def predict_accommodation_cost(request: AccommodationCostRequest):
    try:
        result = model_service.predict_accommodation_cost(
            destination=request.destination,
            accommodation_type=request.accommodation_type,
            star_rating=request.star_rating,
            duration_nights=request.duration_nights,
            travel_date=request.travel_date,
            budget_category=request.budget_category
        )
        return result
    except Exception as e:
        logger.error(f"Error in predict_accommodation_cost: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predictions/total-cost")
async def predict_total_trip_cost(request: TripCostRequest):
    try:
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
        return result
    except Exception as e:
        logger.error(f"Error in predict_total_trip_cost: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predictions/optimize-budget")
async def optimize_budget(request: BudgetOptimizationRequest):
    try:
        result = model_service.optimize_budget(
            current_cost=request.current_cost,
            target_budget=request.target_budget,
            flexibility=request.flexibility
        )
        return result
    except Exception as e:
        logger.error(f"Error in optimize_budget: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- 5. Itinerary Logic (TSP & Validation) ---

@router.post("/itinerary/optimize")
async def optimize_itinerary(request: ItineraryOptimizationRequest):
    try:
        # Pydantic v2 .model_dump() or v1 .dict()
        places = [p.dict() for p in request.places] 
        start_location = request.start_location.dict() if request.start_location else None

        result = model_service.optimize_itinerary(
            places=places,
            start_location=start_location,
            num_days=request.num_days,
            daily_time_budget=request.daily_time_budget
        )
        return result
    except Exception as e:
        logger.error(f"Error in optimize_itinerary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/itinerary/validate")
async def validate_itinerary(itinerary: Dict[str, Any]):
    try:
        result = model_service.validate_itinerary(itinerary)
        return result
    except Exception as e:
        logger.error(f"Error in validate_itinerary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/itinerary/generate-complete")
async def generate_complete_itinerary(request: Dict[str, Any]):
    """
    Generate complete itinerary with day-by-day plans.
    Uses RAG for facts + LM Studio for writing.
    """
    try:
        # Extract fields safely
        destination = request.get('destination')
        duration = request.get('duration', 3)
        budget = request.get('budget', 50000)
        travelers = request.get('travelers', 1)
        preferences = request.get('preferences', [])
        
        logger.info(f"Generating itinerary for {destination}, {duration} days")

        itinerary = model_service.generate_complete_itinerary(
            destination=destination,
            duration=duration,
            budget=budget,
            travelers=travelers,
            preferences=preferences
        )
        return {"itinerary": itinerary, "status": "success"}
    except Exception as e:
        logger.error(f"Error in generate_complete_itinerary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- 8. LOCATION SERVICE (Nominatim / OpenStreetMap) ---

@router.post("/locations/search")
async def search_locations(request: LocationSearchRequest):
    """
    Search for locations using Nominatim OSM API
    
    Example:
        POST /api/v1/locations/search
        {"query": "Goa India", "limit": 10}
    """
    try:
        from services.location_service import LocationService
        
        results = await LocationService.search_locations(
            query=request.query,
            limit=request.limit
        )
        
        if not results:
            return {"results": [], "total_count": 0, "status": "success"}
        
        # Convert Pydantic models to dicts
        results_dicts = [r.dict() if hasattr(r, 'dict') else r for r in results]
        
        return {
            "results": results_dicts,
            "total_count": len(results),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error in search_locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/locations/autocomplete")
async def autocomplete_locations(query: str, limit: int = 5):
    """
    Get location suggestions (autocomplete)
    
    Example:
        GET /api/v1/locations/autocomplete?query=Goa&limit=5
    """
    try:
        from services.location_service import LocationService
        
        results = await LocationService.autocomplete_locations(
            query=query,
            limit=limit
        )
        
        return {
            "suggestions": results,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error in autocomplete_locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/locations/reverse")
async def reverse_geocode(lat: float, lon: float):
    """
    Reverse geocoding: coordinates → location name
    
    Example:
        GET /api/v1/locations/reverse?lat=15.5&lon=73.8
    """
    try:
        from services.location_service import LocationService
        
        location = await LocationService.reverse_geocode(lat=lat, lon=lon)
        
        if not location:
            return {
                "error": "Location not found",
                "status": "not_found"
            }
        
        return {
            "location": location.dict(),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error in reverse_geocode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/locations/bounds")
async def get_location_bounds(city_name: str):
    """
    Get bounding box for a city (useful for map zoom)
    
    Example:
        GET /api/v1/locations/bounds?city_name=Goa
    """
    try:
        from services.location_service import LocationService
        
        bounds = await LocationService.get_city_bounds(city_name)
        
        if not bounds:
            return {
                "error": "Bounds not found",
                "status": "not_found"
            }
        
        return {
            "bounds": bounds.dict(),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error in get_location_bounds: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- 9. WEATHER SERVICE (Open-Meteo) ---

@router.post("/weather/current")
async def get_current_weather(request: WeatherRequestParams):
    """
    Get current weather for a location
    
    Example:
        POST /api/v1/weather/current
        {"lat": 15.5, "lon": 73.8, "location_name": "Goa"}
    """
    try:
        from services.weather_service import WeatherService
        
        weather = await WeatherService.get_current_weather(
            lat=request.lat,
            lon=request.lon,
            location_name=request.location_name
        )
        
        if not weather:
            raise HTTPException(status_code=500, detail="Failed to fetch weather")
        
        return {
            "weather": weather.dict(),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error in get_current_weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weather/forecast")
async def get_weather_forecast(request: WeatherRequestParams):
    """
    Get weather forecast (7-16 days)
    
    Example:
        POST /api/v1/weather/forecast
        {"lat": 15.5, "lon": 73.8, "location_name": "Goa", "days": 7}
    """
    try:
        from services.weather_service import WeatherService
        
        forecast = await WeatherService.get_forecast(
            lat=request.lat,
            lon=request.lon,
            location_name=request.location_name,
            days=request.days
        )
        
        if not forecast:
            raise HTTPException(status_code=500, detail="Failed to fetch forecast")
        
        return forecast.dict()
    except Exception as e:
        logger.error(f"Error in get_weather_forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weather/best-season")
async def get_best_season(destination: str):
    """
    Get best time to visit a destination
    
    Example:
        GET /api/v1/weather/best-season?destination=Goa
    """
    try:
        from services.weather_service import WeatherService
        
        season = WeatherService.get_best_season(destination)
        
        if not season:
            raise HTTPException(status_code=500, detail="Failed to get season info")
        
        return season.dict()
    except Exception as e:
        logger.error(f"Error in get_best_season: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weather/advisory")
async def get_weather_advisory(lat: float, lon: float, trip_date: str):
    """
    Get weather advisory for a specific trip date
    
    Example:
        GET /api/v1/weather/advisory?lat=15.5&lon=73.8&trip_date=2025-01-15
    """
    try:
        from services.weather_service import WeatherService
        
        advisory = await WeatherService.get_weather_advisory(
            lat=lat,
            lon=lon,
            trip_date=trip_date
        )
        
        return {
            "advisory": advisory,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error in get_weather_advisory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- 10. CONTEXT ENRICHMENT (Combine Location + Weather + RAG for LLM) ---

@router.post("/enrichment/destination-context")
async def get_enriched_destination_context(request: TripContextRequest):
    """
    Get complete enriched context for a destination
    
    Combines:
    - Location data (coordinates, bounds)
    - Weather (current + forecast)
    - Travel tips & packing suggestions
    - Activity recommendations
    
    Perfect for providing LLM with rich context for better output
    
    Example:
        POST /api/v1/enrichment/destination-context
        {
            "destination": "Goa",
            "travel_dates": ["2025-01-15", "2025-01-16"],
            "budget": 50000,
            "preferences": ["beach", "relaxation"]
        }
    """
    try:
        from services.context_enrichment_service import context_enrichment_service
        
        llm_context = await context_enrichment_service.enrich_trip_context(
            destination=request.destination,
            start_date=request.travel_dates[0] if request.travel_dates else None,
            end_date=request.travel_dates[-1] if request.travel_dates else None,
            budget=request.budget,
            preferences=request.preferences
        )
        
        return TripContextResponse(
            destination_context=llm_context.get("destination", {}),
            travel_advisories=llm_context.get("weather", {}).get("current", {}),
            packing_suggestions=llm_context.get("packing", ""),
            activity_recommendations=llm_context.get("activities", "")
        )
    except Exception as e:
        logger.error(f"Error in get_enriched_destination_context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enrichment/llm-context")
async def get_llm_context(request: TripContextRequest):
    """
    Get LLM-optimized context for trip planning
    
    This endpoint returns a JSON object optimized for passing to LLM
    with all necessary information for generating itineraries
    
    Example:
        POST /api/v1/enrichment/llm-context
        {
            "destination": "Goa",
            "travel_dates": ["2025-01-15"],
            "budget": 50000
        }
    
    Response format (ready for LLM prompt):
    {
        "destination": {...},
        "weather": {...},
        "packing": "...",
        "activities": "...",
        "trip_details": {...}
    }
    """
    try:
        from services.context_enrichment_service import context_enrichment_service
        
        llm_context = await context_enrichment_service.enrich_trip_context(
            destination=request.destination,
            start_date=request.travel_dates[0] if request.travel_dates else None,
            end_date=request.travel_dates[-1] if request.travel_dates else None,
            budget=request.budget,
            preferences=request.preferences
        )
        
        return {
            "llm_context": llm_context,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error in get_llm_context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- 11. FLIGHT SEARCH (Amadeus Integration) ---

@router.post("/flights/search")
async def search_flights(request: Dict[str, Any]):
    """
    Search for flights using Amadeus API
    
    The flights are shown based on the chosen destination
    
    Request body:
    {
        "origin": "DEL",              # IATA code (3 letters)
        "destination": "GOI",          # IATA code (3 letters)
        "departure_date": "2025-01-15",# YYYY-MM-DD format
        "return_date": "2025-01-20",   # Optional, for round-trip
        "adults": 1,                   # Number of passengers (default 1)
        "currency": "INR"              # Currency for pricing
    }
    
    Example:
        POST /api/v1/flights/search
        {
            "origin": "DEL",
            "destination": "GOI",
            "departure_date": "2025-01-15",
            "adults": 2
        }
    """
    try:
        from services.amadeus_service import AmadeusService
        
        logger.info(f"Flight search: {request['origin']} → {request['destination']}")
        
        amadeus_service = AmadeusService()
        
        # Check if API is available
        if not amadeus_service._check_availability():
            raise HTTPException(
                status_code=503,
                detail="Amadeus API not available - check credentials"
            )
        
        # Prepare search parameters
        search_params = {
            "origin": request.get("origin", "").upper(),
            "destination": request.get("destination", "").upper(),
            "departure_date": request.get("departure_date"),
            "adults": request.get("adults", 1),
            "return_date": request.get("return_date")
        }
        
        # Validate required fields
        if not all([search_params["origin"], search_params["destination"], search_params["departure_date"]]):
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: origin, destination, departure_date"
            )
        
        # Search for flights
        flights = amadeus_service.search_flights(**search_params)
        
        if not flights or "error" in flights:
            error_msg = flights.get("error", "No flights found") if flights else "No flights found"
            raise HTTPException(status_code=404, detail=error_msg)
        
        return {
            "origin": search_params["origin"],
            "destination": search_params["destination"],
            "departure_date": search_params["departure_date"],
            "flights": flights,
            "count": len(flights),
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in search_flights: {e}")
        raise HTTPException(status_code=500, detail=f"Flight search failed: {str(e)}")


@router.post("/flights/by-destination")
async def get_flights_for_destination(request: Dict[str, Any]):
    """
    Get flight options for a specific destination
    
    This endpoint integrates destination selection with flight search.
    Perfect for the trip planning workflow.
    
    Request body:
    {
        "destination": "Goa",         # Destination name
        "origin": "DEL",              # IATA code (default: DEL for India)
        "departure_date": "2025-01-15",
        "return_date": "2025-01-20",  # Optional
        "adults": 2,
        "budget": 50000               # Optional budget in INR
    }
    
    Example:
        POST /api/v1/flights/by-destination
        {
            "destination": "Goa",
            "departure_date": "2025-01-15",
            "adults": 2
        }
    """
    try:
        from services.amadeus_service import AmadeusService
        from services.location_service import LocationService
        
        destination = request.get("destination", "").title()
        origin = request.get("origin", "DEL").upper()
        departure_date = request.get("departure_date")
        
        logger.info(f"Getting flights to {destination}")
        
        # Get IATA code for destination
        location_service = LocationService()
        destination_iata = location_service.get_iata_code(destination)
        
        if not destination_iata:
            raise HTTPException(
                status_code=404,
                detail=f"Could not find IATA code for destination: {destination}"
            )
        
        # Search flights
        amadeus_service = AmadeusService()
        flights = amadeus_service.search_flights(
            origin=origin,
            destination=destination_iata,
            departure_date=departure_date,
            adults=request.get("adults", 1),
            return_date=request.get("return_date")
        )
        
        if not flights or "error" in flights:
            raise HTTPException(status_code=404, detail="No flights available for this destination")
        
        # Filter by budget if provided
        budget = request.get("budget")
        if budget:
            flights = [f for f in flights if f.get("price", float('inf')) <= budget]
        
        return {
            "destination": destination,
            "destination_iata": destination_iata,
            "origin": origin,
            "departure_date": departure_date,
            "flights": flights,
            "count": len(flights),
            "budget_filter": budget,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in get_flights_for_destination: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- 12. TRIP STORAGE (ChromaDB) ---

@router.post("/trips")
async def create_trip(request: Dict[str, Any]):
    """
    Create and store a new trip in ChromaDB
    
    Replaces Firestore storage with ChromaDB for semantic search and RAG integration
    
    Request body:
    {
        "user_id": "user123",
        "destination": "Goa",
        "start_date": "2025-01-15",
        "end_date": "2025-01-20",
        "budget": 50000,
        "preferences": ["beach", "relaxation"],
        "flights": [...],              # Optional: flight selection
        "itinerary": [...],            # Optional: planned activities
        "accommodation": {...}         # Optional: hotel details
    }
    
    Example:
        POST /api/v1/trips
        {
            "user_id": "user123",
            "destination": "Goa",
            "start_date": "2025-01-15",
            "end_date": "2025-01-20",
            "budget": 50000
        }
    """
    try:
        from services.trip_storage_service import TripStorageService
        
        user_id = request.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        destination = request.get("destination")
        if not destination:
            raise HTTPException(status_code=400, detail="destination is required")
        
        trip_id = str(uuid.uuid4())
        
        trip_data = {
            "trip_id": trip_id,
            "user_id": user_id,
            "destination": destination,
            "start_date": request.get("start_date"),
            "end_date": request.get("end_date"),
            "budget": request.get("budget"),
            "preferences": request.get("preferences", []),
            "flights": request.get("flights", []),
            "itinerary": request.get("itinerary", []),
            "accommodation": request.get("accommodation", {}),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        trip_storage = TripStorageService()
        stored_trip_id = trip_storage.add_trip(user_id, trip_data)
        
        logger.info(f"✅ Trip created: {stored_trip_id} for user {user_id}")
        
        return {
            "trip_id": stored_trip_id,
            "destination": destination,
            "status": "success",
            "message": f"Trip to {destination} created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trips/{user_id}")
async def get_user_trips(user_id: str):
    """
    Get all trips for a user from ChromaDB
    
    Retrieves trips stored in ChromaDB with semantic search capabilities
    
    Example:
        GET /api/v1/trips/user123
    """
    try:
        from services.trip_storage_service import TripStorageService
        
        trip_storage = TripStorageService()
        trips = trip_storage.get_user_trips(user_id)
        
        logger.info(f"Retrieved {len(trips)} trips for user {user_id}")
        
        return {
            "user_id": user_id,
            "trips": trips,
            "count": len(trips),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Error retrieving trips: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trips/{user_id}/{trip_id}")
async def get_trip_by_id(user_id: str, trip_id: str):
    """
    Get a specific trip from ChromaDB
    
    Example:
        GET /api/v1/trips/user123/trip-abc-123
    """
    try:
        from services.trip_storage_service import TripStorageService
        
        trip_storage = TripStorageService()
        trip = trip_storage.get_trip_by_id(trip_id)
        
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        # Verify ownership
        if trip.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        return {
            "trip": trip,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/trips/{trip_id}")
async def update_trip(trip_id: str, request: Dict[str, Any]):
    """
    Update an existing trip in ChromaDB
    
    Request body (only fields to update):
    {
        "destination": "Goa",
        "budget": 60000,
        "flights": [...],
        "itinerary": [...]
    }
    
    Example:
        PUT /api/v1/trips/trip-abc-123
        {
            "budget": 60000,
            "preferences": ["beach", "adventure"]
        }
    """
    try:
        from services.trip_storage_service import TripStorageService
        
        trip_storage = TripStorageService()
        
        # Add updated_at timestamp
        updates = {**request, "updated_at": datetime.now().isoformat()}
        
        trip_storage.update_trip(trip_id, updates)
        
        logger.info(f"✅ Trip {trip_id} updated")
        
        return {
            "trip_id": trip_id,
            "status": "success",
            "message": "Trip updated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error updating trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/trips/{trip_id}")
async def delete_trip(trip_id: str):
    """
    Delete a trip from ChromaDB
    
    Example:
        DELETE /api/v1/trips/trip-abc-123
    """
    try:
        from services.trip_storage_service import TripStorageService
        
        trip_storage = TripStorageService()
        trip_storage.delete_trip(trip_id)
        
        logger.info(f"✅ Trip {trip_id} deleted")
        
        return {
            "trip_id": trip_id,
            "status": "success",
            "message": "Trip deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error deleting trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trips/search")
async def search_trips(request: Dict[str, Any]):
    """
    Semantically search trips across all users
    
    Uses ChromaDB vector search for finding trips similar to query
    
    Request body:
    {
        "user_id": "user123",           # To filter by user
        "query": "beach relaxation",    # Search query
        "top_k": 5                      # Number of results
    }
    
    Example:
        POST /api/v1/trips/search
        {
            "user_id": "user123",
            "query": "adventure mountain trekking",
            "top_k": 3
        }
    """
    try:
        from services.trip_storage_service import TripStorageService
        
        user_id = request.get("user_id")
        query = request.get("query", "")
        top_k = request.get("top_k", 5)
        
        if not query:
            raise HTTPException(status_code=400, detail="query is required")
        
        trip_storage = TripStorageService()
        results = trip_storage.search_trips(user_id, query, top_k)
        
        logger.info(f"Found {len(results)} matching trips for query: {query}")
        
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error searching trips: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 📚 CHROMADB KNOWLEDGE BASE ENDPOINTS (NEW)
# ============================================================================

@router.post("/destinations/search-knowledge")
async def search_destination_knowledge(request: Dict[str, Any]):
    """
    🔍 Search destination knowledge from ChromaDB
    Returns semantic search results from RAG/ChromaDB system
    
    Request:
        {
            "query": "mountain trekking adventure in north india",
            "top_k": 3
        }
    
    Response includes destination data from ChromaDB with semantic relevance scores
    """
    try:
        query = request.get("query", "").strip()
        top_k = request.get("top_k", 5)
        
        if not query:
            raise HTTPException(status_code=400, detail="query parameter is required")
        
        # Import RAG service
                
        logger.info(f"🔍 Searching ChromaDB for: '{query}'")
        
        # Retrieve from ChromaDB
        results = rag_service.retrieve(query, top_k=top_k)
        
        if not results:
            logger.warning(f"⚠️  No results found in ChromaDB for query: '{query}'")
            return {
                "query": query,
                "results": [],
                "count": 0,
                "source": "chromadb",
                "status": "no_results"
            }
        
        # Format results for frontend
        formatted_results = []
        for result in results:
            meta = result.get('meta', {})
            text = result.get('text', '')
            distance = result.get('distance', 0)
            
            # Calculate similarity score (0-100)
            similarity = max(0, 100 - (distance * 100)) if distance else 100
            
            formatted_results.append({
                "destination": meta.get('destination', 'Unknown'),
                "state": meta.get('state', 'N/A'),
                "region": meta.get('region', 'N/A'),
                "best_season": meta.get('best_season', 'N/A'),
                "climate": meta.get('climate', 'N/A'),
                "budget": meta.get('budget', 'N/A'),
                "attraction_count": meta.get('attraction_count', 0),
                "activity_count": meta.get('activity_count', 0),
                "similarity_score": round(similarity, 2),
                "source": meta.get('source', 'unknown'),
                "is_custom": meta.get('custom', False),
                "preview": text[:300] + "..." if len(text) > 300 else text
            })
        
        logger.info(f"✅ Found {len(formatted_results)} destination(s) in ChromaDB")
        
        return {
            "query": query,
            "results": formatted_results,
            "count": len(formatted_results),
            "source": "chromadb",
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error searching ChromaDB knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 📦 DATA ENDPOINTS (destinations & places lists)
# Consumed by the frontend aiService (getAllDestinations / getAllPlaces).
# ============================================================================

def _shape_destination(record: Dict[str, Any]) -> Dict[str, Any]:
    """Map a raw dataset row into the DestinationCard shape used by the UI."""
    name = (record.get("Destination Name")
            or record.get("destination_name")
            or record.get("Destination")
            or record.get("name")
            or "Unknown")
    text = record.get("Description") or record.get("description") or record.get("text") or ""
    state = record.get("State") or record.get("state") or "India"
    return {
        "destination_name": name,
        "state": state,
        "match_score": round(float(record.get("Rating") or _hash_score(name)), 1),
        "image": record.get("image"),
        "description": str(text)[:280],
        "flight_estimate": record.get("flight_estimate"),
        "hotel_estimate": record.get("hotel_estimate"),
    }


def _hash_score(name: str) -> float:
    """Deterministic pseudo score in the 75-98 range so cards never look empty."""
    try:
        h = sum(ord(c) for c in name or "x")
        return 75 + (h % 24)
    except Exception:
        return 90.0


@router.get("/data/destinations")
async def get_data_destinations():
    """Return the list of destinations from the local dataset."""
    try:
        records = model_service.get_destinations()
        destinations = [_shape_destination(r) for r in records]
        return {"status": "success", "count": len(destinations), "destinations": destinations}
    except Exception as e:
        logger.error(f"Error in get_data_destinations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/places")
async def get_data_places():
    """Return the list of tourist places from the local dataset."""
    try:
        records = model_service.get_places()
        places = []
        for r in records:
            name = r.get("Place Name") or r.get("name") or r.get("text") or "Unknown"
            places.append({
                "name": name,
                "category": r.get("Category") or r.get("category") or "General",
                "visit_duration": r.get("Visit Duration") or r.get("visit_duration") or "N/A",
            })
        return {"status": "success", "count": len(places), "places": places}
    except Exception as e:
        logger.error(f"Error in get_data_places: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 🕷️ SCRAPER ENDPOINTS
# No external web scraper is used (YAGNI / privacy-first). These endpoints
# serve curated data backed by the local destination knowledge base so the
# frontend honest "realtime" endpoints resolve to working responses.
# ============================================================================

@router.post("/scraper/search-destinations")
async def scraper_search_destinations(request: Dict[str, Any]):
    """Search destinations. Returns locally-curated matching destinations."""
    try:
        query_params = request.get("query_params") or {}
        query = str(query_params.get("destination") or query_params.get("query") or "").lower()
        records = model_service.get_destinations()

        results = []
        for r in records:
            shaped = _shape_destination(r)
            if query and query not in shaped["destination_name"].lower():
                continue
            results.append(shaped)

        if not results and records:
            results = [_shape_destination(r) for r in records[:10]]

        return {"status": "success", "count": len(results), "results": results}
    except Exception as e:
        logger.error(f"Error in scraper_search_destinations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scraper/destination-details")
async def scraper_destination_details(request: Dict[str, Any]):
    """Return detailed (locally curated) information for a destination."""
    try:
        destination = str(request.get("destination") or "").strip()
        record = next(
            (r for r in model_service.get_destinations()
             if destination.lower() in (_shape_destination(r)["destination_name"].lower())),
            None,
        )

        if not record:
            return {
                "status": "not_found",
                "destination": destination,
                "data": {"overview": f"Limited information available for {destination}."},
            }

        shaped = _shape_destination(record)
        return {
            "status": "success",
            "destination": shaped["destination_name"],
            "data": {
                "overview": shaped["description"] or f"{shaped['destination_name']} is a popular travel destination.",
                "state": shaped["state"],
                "best_time": record.get("Best Time to Visit") or record.get("best_time_visit") or "Year-round",
                "category": record.get("Category") or record.get("category") or "General",
            },
        }
    except Exception as e:
        logger.error(f"Error in scraper_destination_details: {e}")
        raise HTTPException(status_code=500, detail=str(e))



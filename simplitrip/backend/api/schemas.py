"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# Recommendation Schemas
class RecommendationRequest(BaseModel):
    """Request schema for destination recommendations"""
    category: Optional[str] = Field(None, description="Destination category (e.g., Beach, Historical)")
    state: Optional[str] = Field(None, description="State in India")
    best_time: Optional[str] = Field(None, description="Best time to visit")
    budget: Optional[float] = Field(None, description="Budget in INR")
    user_id: Optional[str] = Field(None, description="User ID for personalized recommendations")
    top_n: int = Field(10, description="Number of recommendations to return")
    exclude_destinations: Optional[List[str]] = Field(None, description="Destinations to exclude")


class DestinationRecommendation(BaseModel):
    """Response schema for a single destination recommendation"""
    destination_name: str
    state: str
    category: str
    rating: float
    best_time: str
    score: float
    description: Optional[str] = None


class RecommendationResponse(BaseModel):
    """Response schema for recommendations"""
    recommendations: List[DestinationRecommendation]
    total_count: int
    request_id: Optional[str] = None


# Cost Prediction Schemas
class FlightCostRequest(BaseModel):
    """Request schema for flight cost prediction"""
    from_city: str = Field(..., description="Origin city")
    to_city: str = Field(..., description="Destination city")
    travel_date: datetime = Field(..., description="Date of travel")
    booking_date: Optional[datetime] = Field(None, description="Date of booking")
    num_travelers: int = Field(1, description="Number of travelers")


class FlightCostResponse(BaseModel):
    """Response schema for flight cost prediction"""
    predicted_cost: float
    confidence: float
    currency: str = "INR"
    breakdown: Optional[Dict[str, float]] = None


class AccommodationCostRequest(BaseModel):
    """Request schema for accommodation cost prediction"""
    destination: str
    accommodation_type: str = Field(..., description="Type: hotel, resort, hostel, etc.")
    star_rating: int = Field(..., ge=1, le=5, description="Star rating (1-5)")
    duration_nights: int = Field(..., ge=1, description="Number of nights")
    travel_date: datetime
    budget_category: str = Field("mid-range", description="Budget category: budget, mid-range, luxury")


class AccommodationCostResponse(BaseModel):
    """Response schema for accommodation cost prediction"""
    predicted_cost: float
    cost_per_night: float
    duration_nights: int
    confidence: float
    currency: str = "INR"


class TripCostRequest(BaseModel):
    """Request schema for total trip cost prediction"""
    from_city: str
    to_city: str
    travel_date: datetime
    return_date: datetime
    num_travelers: int = Field(..., ge=1)
    accommodation_type: str
    star_rating: int = Field(..., ge=1, le=5)
    budget_category: str = Field("mid-range", description="Budget category")
    meal_preference: str = Field("veg", description="Meal preference: veg, non-veg")
    include_activities: bool = Field(True, description="Include activity costs")


class TripCostResponse(BaseModel):
    """Response schema for total trip cost prediction"""
    breakdown: Dict[str, float]
    total_cost: float
    cost_per_person: float
    duration_days: int
    num_travelers: int
    currency: str = "INR"
    confidence: float


class BudgetOptimizationRequest(BaseModel):
    """Request schema for budget optimization"""
    current_cost: Dict[str, Any]
    target_budget: float
    flexibility: Dict[str, bool] = Field(
        default_factory=lambda: {
            "accommodation": True,
            "meals": True,
            "activities": True,
            "transport": True
        }
    )


class BudgetOptimizationResponse(BaseModel):
    """Response schema for budget optimization"""
    within_budget: bool
    over_budget_by: Optional[float] = None
    suggestions: List[Dict[str, Any]]
    potential_savings: float
    optimized_total: float


# Itinerary Schemas
class Place(BaseModel):
    """Schema for a place/attraction"""
    name: str
    category: Optional[str] = None
    visit_duration: Optional[int] = Field(None, description="Visit duration in minutes")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None


class StartLocation(BaseModel):
    """Schema for starting location (hotel/accommodation)"""
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ItineraryOptimizationRequest(BaseModel):
    """Request schema for itinerary optimization"""
    places: List[Place]
    start_location: Optional[StartLocation] = None
    num_days: int = Field(..., ge=1, description="Number of days")
    daily_time_budget: int = Field(480, description="Available time per day in minutes (default: 8 hours)")


class PlaceSchedule(BaseModel):
    """Schema for a place in the schedule"""
    place: Place
    travel_time: float
    visit_duration: float
    start_time: str


class DailySchedule(BaseModel):
    """Schema for a day's schedule"""
    day: int
    places: List[PlaceSchedule]
    total_time: float


class ItineraryOptimizationResponse(BaseModel):
    """Response schema for itinerary optimization"""
    daily_schedules: List[DailySchedule]
    num_days: int
    total_places: int
    total_travel_time: float
    total_visit_time: float
    optimization_score: float


class ItineraryValidationResponse(BaseModel):
    """Response schema for itinerary validation"""
    is_valid: bool
    issues: List[str]
    warnings: List[str]


# LLM Schemas
class NaturalLanguageQueryRequest(BaseModel):
    """Request schema for parsing natural language query"""
    query: str = Field(..., description="Natural language travel query")


class ParsedQuery(BaseModel):
    """Response schema for parsed query"""
    destination: Optional[str] = None
    duration: Optional[int] = None
    travelers: Optional[int] = None
    preferences: List[str] = []
    budget: Optional[float] = None
    travel_date: Optional[str] = None


class DescriptionGenerationRequest(BaseModel):
    """Request schema for generating itinerary description"""
    itinerary: Dict[str, Any]
    style: str = Field("engaging", description="Description style: engaging, formal, casual")


class DescriptionGenerationResponse(BaseModel):
    """Response schema for generated description"""
    description: str
    highlights: List[str]


class RecommendationExplanationRequest(BaseModel):
    """Request schema for explaining recommendation"""
    destination: str
    user_profile: Dict[str, Any]


class RecommendationExplanationResponse(BaseModel):
    """Response schema for recommendation explanation"""
    explanation: str
    key_factors: List[str]


# ============================================================================
# LOCATION SCHEMAS (for Nominatim OSM API)
# ============================================================================

class LocationCoords(BaseModel):
    """Location with coordinates"""
    name: str = Field(..., description="Location name")
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    display_name: Optional[str] = None
    place_type: Optional[str] = None


class LocationSearchResult(BaseModel):
    """Result from location search"""
    name: str
    lat: float
    lon: float
    state: Optional[str] = None
    country: Optional[str] = None
    importance: float = Field(0.0, description="Relevance score 0-1")


class BoundingBox(BaseModel):
    """Bounding box for map display"""
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float


class LocationSearchRequest(BaseModel):
    """Request to search for locations"""
    query: str = Field(..., description="Search query (city name, landmark, etc)")
    limit: int = Field(10, description="Max results to return")
    country: str = Field("India", description="Country to search in")


class LocationSearchResponse(BaseModel):
    """Response from location search"""
    results: List[LocationSearchResult]
    total_count: int
    status: str = "success"


class LocationAutocompleteRequest(BaseModel):
    """Request for location autocomplete"""
    query: str = Field(..., description="Partial location name")
    limit: int = Field(5, description="Max suggestions")


class LocationAutocompleteResponse(BaseModel):
    """Autocomplete suggestions"""
    suggestions: List[str]
    status: str = "success"


# ============================================================================
# WEATHER SCHEMAS (for Open-Meteo API)
# ============================================================================

class CurrentWeatherResponse(BaseModel):
    """Current weather data"""
    temperature: float = Field(..., description="Temperature in Celsius")
    feels_like: float
    humidity: int
    condition: str = Field(..., description="Weather condition description")
    condition_code: int
    precipitation: float = Field(..., description="Precipitation in mm")
    cloudiness: int
    wind_speed: float
    visibility: int
    uv_index: float
    timestamp: str


class DailyForecastResponse(BaseModel):
    """Daily weather forecast"""
    date: str = Field(..., description="YYYY-MM-DD")
    max_temp: float
    min_temp: float
    avg_temp: float
    precipitation: float
    precipitation_prob: int
    condition: str
    wind_speed_max: float
    uv_index_max: float
    sunrise: str = Field(..., description="HH:MM format")
    sunset: str = Field(..., description="HH:MM format")


class WeatherForecastResponse(BaseModel):
    """Complete weather forecast"""
    location: str
    lat: float
    lon: float
    current: CurrentWeatherResponse
    daily: List[DailyForecastResponse]
    status: str = "success"


class WeatherRequestParams(BaseModel):
    """Request parameters for weather"""
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    location_name: str = Field(..., description="Display name")
    days: int = Field(7, description="Forecast days (1-16)")


class BestSeasonResponse(BaseModel):
    """Best time to visit a destination"""
    destination: str
    months: List[str]
    reason: str
    avg_temp: float
    rainfall_season: str
    dry_season: str
    status: str = "success"


# ============================================================================
# ENRICHED CONTEXT SCHEMAS (combining Location + Weather + RAG for LLM)
# ============================================================================

class DestinationContext(BaseModel):
    """Complete context about a destination for LLM"""
    destination: str
    state: str
    location: LocationCoords
    current_weather: Optional[CurrentWeatherResponse] = None
    forecast: Optional[List[DailyForecastResponse]] = None
    best_season: Optional[BestSeasonResponse] = None
    description: Optional[str] = None
    category: Optional[str] = None
    rating: Optional[float] = None


class TripContextRequest(BaseModel):
    """Request to get enriched context for trip planning"""
    destination: str = Field(..., description="Destination name")
    travel_dates: Optional[List[str]] = Field(None, description="List of dates YYYY-MM-DD")
    budget: Optional[float] = None
    preferences: Optional[List[str]] = None


class TripContextResponse(BaseModel):
    """Enriched context response for LLM"""
    destination_context: DestinationContext
    travel_advisories: Optional[str] = None
    packing_suggestions: Optional[str] = None
    activity_recommendations: Optional[str] = None
    status: str = "success"


# ============================================================================
# GENERAL SCHEMAS
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime

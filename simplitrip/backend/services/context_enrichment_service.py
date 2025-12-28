"""
Context Enrichment Service

Combines Location + Weather + RAG data to provide rich context to LLM for better trip planning outputs.
This service ensures the LLM has all necessary information to generate high-quality recommendations.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from services.location_service import LocationService
from services.weather_service import WeatherService
from utils.logger import logger
from datetime import datetime, timedelta


class EnrichedDestinationContext(BaseModel):
    """Complete context about a destination"""
    destination: str
    coordinates: Dict[str, float]  # lat, lon
    current_weather: Optional[Dict[str, Any]] = None
    forecast: Optional[List[Dict[str, Any]]] = None
    best_season: Optional[Dict[str, Any]] = None
    rag_description: Optional[str] = None
    travel_tips: Optional[str] = None
    packing_suggestions: Optional[str] = None
    activity_recommendations: Optional[str] = None


class ContextEnrichmentService:
    """
    Service to enrich trip planning context with real data
    
    Flow:
    1. Search for destination location (Nominatim)
    2. Get coordinates and bounds
    3. Fetch current weather + forecast (Open-Meteo)
    4. Get best season info
    5. Query RAG for destination description
    6. Generate packing suggestions based on weather
    7. Return enriched context to LLM
    """
    
    @staticmethod
    async def enrich_destination_context(
        destination: str,
        travel_dates: Optional[List[str]] = None,
        context_type: str = "full"  # "full", "weather_only", "location_only"
    ) -> Optional[EnrichedDestinationContext]:
        """
        Get enriched context for a destination
        
        Args:
            destination: Destination name
            travel_dates: List of travel dates (YYYY-MM-DD format)
            context_type: What context to include
            
        Returns:
            Enriched context object or None on failure
            
        Example:
            context = await ContextEnrichmentService.enrich_destination_context(
                "Goa",
                travel_dates=["2025-01-15", "2025-01-16"],
                context_type="full"
            )
        """
        try:
            logger.info(f"Enriching context for {destination}")
            
            # Step 1: Find location coordinates
            locations = await LocationService.search_locations(
                query=destination,
                limit=1
            )
            
            if not locations:
                logger.warning(f"Location not found: {destination}")
                return None
            
            location = locations[0]
            coordinates = {
                "lat": location.lat,
                "lon": location.lon,
                "name": location.name
            }
            
            context = EnrichedDestinationContext(
                destination=destination,
                coordinates=coordinates
            )
            
            # Step 2: Get weather data if requested
            if context_type in ["full", "weather_only"]:
                weather = await WeatherService.get_current_weather(
                    lat=location.lat,
                    lon=location.lon,
                    location_name=location.name
                )
                
                if weather:
                    context.current_weather = weather.dict()
                
                # Get forecast
                forecast = await WeatherService.get_forecast(
                    lat=location.lat,
                    lon=location.lon,
                    location_name=location.name,
                    days=7
                )
                
                if forecast:
                    context.forecast = [
                        day.dict() for day in forecast.daily
                    ]
                
                # Get best season
                season = WeatherService.get_best_season(destination)
                if season:
                    context.best_season = season.dict()
            
            # Step 3: Get location bounds for reference
            bounds = await LocationService.get_city_bounds(destination)
            
            # Step 4: Generate travel tips based on location
            if context_type == "full":
                context.travel_tips = ContextEnrichmentService._generate_travel_tips(
                    destination,
                    location.state if hasattr(location, 'state') else None,
                    context.current_weather,
                    context.best_season
                )
                
                # Step 5: Generate packing suggestions
                context.packing_suggestions = ContextEnrichmentService._generate_packing_suggestions(
                    context.current_weather,
                    context.forecast
                )
                
                # Step 6: Generate activity recommendations
                context.activity_recommendations = ContextEnrichmentService._generate_activity_recommendations(
                    destination,
                    context.current_weather
                )
            
            logger.info(f"Successfully enriched context for {destination}")
            return context
            
        except Exception as e:
            logger.error(f"Error enriching context for {destination}: {e}")
            return None
    
    @staticmethod
    async def enrich_trip_context(
        destination: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        budget: Optional[float] = None,
        preferences: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get complete enriched context for trip planning
        
        Returns a comprehensive dictionary with all context needed by LLM
        
        Args:
            destination: Destination name
            start_date: Trip start date (YYYY-MM-DD)
            end_date: Trip end date (YYYY-MM-DD)
            budget: Budget in INR
            preferences: User preferences (e.g., ["adventure", "beach", "culture"])
            
        Returns:
            Dict with all context for LLM
        """
        try:
            # Get enriched destination context
            travel_dates = []
            if start_date and end_date:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                current = start
                while current <= end:
                    travel_dates.append(current.strftime("%Y-%m-%d"))
                    current += timedelta(days=1)
            
            context = await ContextEnrichmentService.enrich_destination_context(
                destination,
                travel_dates=travel_dates,
                context_type="full"
            )
            
            if not context:
                return {"error": "Failed to enrich context", "destination": destination}
            
            # Build LLM context dictionary
            llm_context = {
                "destination": {
                    "name": context.destination,
                    "coordinates": context.coordinates,
                    "travel_tips": context.travel_tips,
                    "description": context.rag_description or "Popular travel destination in India"
                },
                "weather": {
                    "current": context.current_weather,
                    "forecast": context.forecast,
                    "best_season": context.best_season
                },
                "packing": context.packing_suggestions,
                "activities": context.activity_recommendations,
                "trip_details": {
                    "duration_days": len(travel_dates) if travel_dates else "Not specified",
                    "budget": budget,
                    "preferences": preferences or [],
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
            
            return llm_context
            
        except Exception as e:
            logger.error(f"Error in enrich_trip_context: {e}")
            return {"error": str(e), "destination": destination}
    
    @staticmethod
    def _generate_travel_tips(
        destination: str,
        state: Optional[str] = None,
        weather: Optional[Dict] = None,
        season: Optional[Dict] = None
    ) -> str:
        """Generate travel tips based on destination and weather"""
        tips = []
        
        # Add destination-specific tips
        if destination.lower() in ["goa", "kerala", "maldives"]:
            tips.append("✈️ Beach destination - bring sunscreen and light clothing")
            tips.append("🏊 Swimwear and beach towels recommended")
        
        elif destination.lower() in ["delhi", "agra"]:
            tips.append("🏛️ Historical sites - comfortable walking shoes needed")
            tips.append("📸 Photography allowed at most attractions")
        
        elif destination.lower() in ["kashmir", "himachal"]:
            tips.append("⛰️ Mountain destination - layers and warm clothing needed")
            tips.append("🥾 Trekking shoes recommended")
        
        # Add weather-specific tips
        if weather and weather.get("temperature", 0) > 35:
            tips.append("☀️ Very hot weather - stay hydrated, avoid midday sun")
        elif weather and weather.get("temperature", 0) < 10:
            tips.append("❄️ Cold weather - bring warm jacket and layers")
        
        if weather and weather.get("precipitation", 0) > 5:
            tips.append("☔ Rainy weather - carry umbrella and waterproof bag")
        
        # Add season tips
        if season and "monsoon" in season.get("rainfall_season", "").lower():
            tips.append("🌧️ During monsoon season - landslides possible in hilly areas")
        
        return "\n".join(tips) if tips else "Have a great trip!"
    
    @staticmethod
    def _generate_packing_suggestions(
        weather: Optional[Dict] = None,
        forecast: Optional[List[Dict]] = None
    ) -> str:
        """Generate packing suggestions based on weather"""
        suggestions = {
            "essentials": ["Passport", "Travel documents", "Medications"],
            "clothing": [],
            "accessories": [],
            "weather_specific": []
        }
        
        # Determine temperature range
        temps = []
        if weather and "temperature" in weather:
            temps.append(weather["temperature"])
        if forecast:
            temps.extend([day.get("max_temp", 25) for day in forecast[:3]])
        
        avg_temp = sum(temps) / len(temps) if temps else 25
        
        # Temperature-based suggestions
        if avg_temp > 30:
            suggestions["clothing"].extend(["Light T-shirts", "Shorts", "Summer dresses"])
            suggestions["weather_specific"].extend(["Sunscreen (SPF 50+)", "Sunglasses", "Hat/Cap"])
        elif avg_temp < 15:
            suggestions["clothing"].extend(["Warm jacket", "Thermals", "Sweaters"])
            suggestions["accessories"].extend(["Scarf", "Winter gloves", "Beanie"])
        else:
            suggestions["clothing"].extend(["Light jacket", "Jeans", "T-shirts"])
        
        # Rain preparation
        if weather and weather.get("precipitation", 0) > 5:
            suggestions["accessories"].extend(["Umbrella", "Waterproof bag", "Rain cover"])
        
        # Always add common items
        suggestions["accessories"].extend(["Phone charger", "Universal adapter", "Power bank"])
        
        # Format output
        output = "PACKING SUGGESTIONS:\n"
        for category, items in suggestions.items():
            if items:
                output += f"\n{category.upper()}:\n"
                output += "\n".join([f"  • {item}" for item in items])
        
        return output
    
    @staticmethod
    def _generate_activity_recommendations(
        destination: str,
        weather: Optional[Dict] = None
    ) -> str:
        """Generate activity recommendations based on destination and weather"""
        activities = {
            "goa": [
                "🏖️ Beach relaxation at Baga, Calangute beaches",
                "🏄 Water sports - jet skiing, parasailing",
                "🌅 Sunset at Palolem Beach",
                "🏛️ Basilica of Bom Jesus - UNESCO site",
                "🎭 Nightlife in Panaji and Baga"
            ],
            "kashmir": [
                "⛰️ Trekking in Himalayas",
                "🛥️ Shikara rides in Dal Lake",
                "🌲 Pine forests and meadows",
                "🏔️ Gulmarg skiing (winter)",
                "📸 Sunrise at Pahalgam"
            ],
            "rajasthan": [
                "🏰 City Palace Jaipur",
                "🐅 Tiger safari in Ranthambore",
                "🏜️ Camel safari in Thar desert",
                "🕌 Taj Mahal Agra",
                "🏛️ Mehrangarh Fort Jodhpur"
            ],
            "kerala": [
                "🚤 Backwater houseboat cruise",
                "🌴 Beach relaxation at Varkala",
                "🥥 Spice plantations tour",
                "🐠 Fishing village visits",
                "🌅 Sunset at Cochin harbor"
            ]
        }
        
        # Get destination-specific activities
        dest_lower = destination.lower()
        recommended = activities.get(dest_lower, [
            "🗺️ Local exploration",
            "🍽️ Street food tasting",
            "📷 Photography",
            "🏛️ Cultural site visits",
            "🛍️ Local market shopping"
        ])
        
        # Add weather warnings for activities
        if weather and weather.get("precipitation", 0) > 10:
            recommended.append("🌧️ Indoor activities - museums, galleries")
        
        output = "ACTIVITY RECOMMENDATIONS:\n"
        output += "\n".join([f"  {activity}" for activity in recommended[:5]])
        return output


# Singleton instance
context_enrichment_service = ContextEnrichmentService()

"""
Weather Service using Open-Meteo API
Free weather data for any location in India
No API key required - completely free, no rate limits
"""

import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from enum import Enum
from utils.logger import logger

# ============================================================================
# SCHEMAS & MODELS
# ============================================================================

class WeatherCondition(str, Enum):
    """Weather condition codes"""
    CLEAR = "clear_sky"
    MAINLY_CLEAR = "mainly_clear"
    PARTLY_CLOUDY = "partly_cloudy"
    OVERCAST = "overcast"
    LIGHT_RAIN = "light_rain"
    MODERATE_RAIN = "moderate_rain"
    HEAVY_RAIN = "heavy_rain"
    RAIN = "rain"
    THUNDERSTORM = "thunderstorm"
    SNOW = "snow"

class CurrentWeather(BaseModel):
    """Current weather data"""
    temperature: float  # in Celsius
    feels_like: float
    humidity: int  # 0-100%
    wind_speed: float  # km/h
    condition: str  # Description
    condition_code: int
    precipitation: float  # mm
    cloudiness: int  # 0-100%
    visibility: int  # meters
    uv_index: float
    timestamp: str  # ISO format

class DailyForecast(BaseModel):
    """Daily weather forecast"""
    date: str  # YYYY-MM-DD
    max_temp: float
    min_temp: float
    avg_temp: float
    precipitation: float  # mm
    precipitation_prob: int  # 0-100%
    condition: str
    wind_speed_max: float
    uv_index_max: float
    sunrise: str  # HH:MM
    sunset: str  # HH:MM

class WeatherForecast(BaseModel):
    """Complete weather forecast"""
    location: str
    lat: float
    lon: float
    current: CurrentWeather
    daily: List[DailyForecast]

class BestSeason(BaseModel):
    """Best time to visit a destination"""
    destination: str
    months: List[str]  # Best months (e.g., ["October", "November"])
    reason: str
    avg_temp: float
    avg_precipitation: float
    rainfall_season: str
    dry_season: str

# ============================================================================
# WEATHER SERVICE
# ============================================================================

class WeatherService:
    """
    Weather service using Open-Meteo API
    
    Features:
    - Current weather
    - 7-day forecast
    - Historical climate data
    - No API key required
    - No rate limits
    - Full India coverage
    """
    
    BASE_URL = "https://api.open-meteo.com/v1"
    TIMEOUT = 10
    
    # Weather condition mapping
    WMO_CODES = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Foggy",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with hail"
    }
    
    # Best seasons for Indian destinations
    DESTINATION_SEASONS = {
        "goa": {
            "best_months": ["October", "November", "December", "January", "February", "March"],
            "reason": "Pleasant weather, avoid monsoon",
            "avg_temp": 28,
            "rainfall_season": "June-September",
            "dry_season": "October-May"
        },
        "kashmir": {
            "best_months": ["May", "June", "July", "August", "September"],
            "reason": "Snow melts, pleasant climate",
            "avg_temp": 18,
            "rainfall_season": "March-August",
            "dry_season": "September-February"
        },
        "delhi": {
            "best_months": ["October", "November", "February", "March"],
            "reason": "Moderate temperatures",
            "avg_temp": 25,
            "rainfall_season": "July-September",
            "dry_season": "October-May"
        },
        "bengaluru": {
            "best_months": ["September", "October", "November", "December", "January", "February"],
            "reason": "Pleasant weather, moderate temperatures",
            "avg_temp": 23,
            "rainfall_season": "June-September",
            "dry_season": "October-May"
        },
        "maldives": {
            "best_months": ["November", "December", "January", "February", "March", "April"],
            "reason": "Dry season, perfect for beach holidays",
            "avg_temp": 28,
            "rainfall_season": "May-October",
            "dry_season": "November-April"
        },
        "darjeeling": {
            "best_months": ["October", "November", "March", "April", "May"],
            "reason": "Clear skies, avoid monsoon",
            "avg_temp": 15,
            "rainfall_season": "June-September",
            "dry_season": "October-May"
        },
        "rajasthan": {
            "best_months": ["October", "November", "December", "January", "February"],
            "reason": "Cool, avoid extreme heat",
            "avg_temp": 20,
            "rainfall_season": "July-September",
            "dry_season": "October-May"
        }
    }
    
    @staticmethod
    def _get_condition_description(code: int) -> str:
        """Convert WMO weather code to description"""
        return WeatherService.WMO_CODES.get(code, f"Weather code {code}")
    
    @classmethod
    async def get_current_weather(
        cls,
        lat: float,
        lon: float,
        location_name: str = "Location"
    ) -> Optional[CurrentWeather]:
        """
        Get current weather for coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            location_name: Display name
            
        Returns:
            CurrentWeather object or None if request fails
            
        Example:
            weather = await WeatherService.get_current_weather(15.5, 73.8, "Goa")
        """
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.get(
                    f"{cls.BASE_URL}/forecast",
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "current": "temperature_2m,apparent_temperature,weather_code,precipitation,cloud_cover,wind_speed_10m,uv_index",
                        "temperature_unit": "celsius",
                        "wind_speed_unit": "kmh"
                    }
                )
                response.raise_for_status()
            
            data = response.json()
            current = data["current"]
            
            weather = CurrentWeather(
                temperature=float(current["temperature_2m"]),
                feels_like=float(current["apparent_temperature"]),
                humidity=int(current.get("relative_humidity_2m", 50)),  # Use relative humidity from daily if available
                wind_speed=float(current.get("wind_speed_10m", 0)),
                condition=cls._get_condition_description(current["weather_code"]),
                condition_code=current["weather_code"],
                precipitation=float(current.get("precipitation", 0)),
                cloudiness=int(current.get("cloud_cover", 0)),
                visibility=10000,  # Default value since not available
                uv_index=float(current.get("uv_index", 0)),
                timestamp=current["time"]
            )
            
            logger.info(f"Got current weather for {location_name}: {weather.temperature}°C")
            return weather
            
        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            return None
    
    @classmethod
    async def get_forecast(
        cls,
        lat: float,
        lon: float,
        location_name: str = "Location",
        days: int = 7
    ) -> Optional[WeatherForecast]:
        """
        Get weather forecast for up to 16 days
        
        Args:
            lat: Latitude
            lon: Longitude
            location_name: Display name
            days: Number of days to forecast (max 16)
            
        Returns:
            WeatherForecast object with current + daily forecast
            
        Example:
            forecast = await WeatherService.get_forecast(15.5, 73.8, "Goa", days=5)
        """
        try:
            days = min(days, 16)  # Max 16 days available
            
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.get(
                    f"{cls.BASE_URL}/forecast",
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "current": "temperature_2m,apparent_temperature,weather_code,precipitation,cloud_cover,wind_speed_10m,uv_index",
                        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,precipitation_probability_max,weather_code,wind_speed_10m_max,uv_index_max,sunrise,sunset",
                        "temperature_unit": "celsius",
                        "wind_speed_unit": "kmh",
                        "forecast_days": days
                    }
                )
                response.raise_for_status()
            
            data = response.json()
            
            # Parse current weather
            current_data = data["current"]
            current = CurrentWeather(
                temperature=float(current_data["temperature_2m"]),
                feels_like=float(current_data["apparent_temperature"]),
                humidity=int(current_data.get("relative_humidity_2m", 50)),
                wind_speed=float(current_data.get("wind_speed_10m", 0)),
                condition=cls._get_condition_description(current_data["weather_code"]),
                condition_code=current_data["weather_code"],
                precipitation=float(current_data.get("precipitation", 0)),
                cloudiness=int(current_data.get("cloud_cover", 0)),
                visibility=10000,  # Default since not available in API
                uv_index=float(current_data.get("uv_index", 0)),
                timestamp=current_data["time"]
            )
            
            # Parse daily forecast
            daily_data = data["daily"]
            daily_forecast = []
            
            for i in range(len(daily_data["time"])):
                # Extract sunrise/sunset time (HH:MM format)
                sunrise = daily_data["sunrise"][i].split("T")[1][:5] if "sunrise" in daily_data else "06:00"
                sunset = daily_data["sunset"][i].split("T")[1][:5] if "sunset" in daily_data else "18:00"
                
                day_forecast = DailyForecast(
                    date=daily_data["time"][i],
                    max_temp=float(daily_data["temperature_2m_max"][i]),
                    min_temp=float(daily_data["temperature_2m_min"][i]),
                    avg_temp=float(daily_data["temperature_2m_mean"][i]),
                    precipitation=float(daily_data.get("precipitation_sum", [0])[i] or 0),
                    precipitation_prob=int(daily_data.get("precipitation_probability_max", [0])[i] or 0),
                    condition=cls._get_condition_description(daily_data["weather_code"][i]),
                    wind_speed_max=float(daily_data.get("wind_speed_10m_max", [0])[i] or 0),
                    uv_index_max=float(daily_data.get("uv_index_max", [0])[i] or 0),
                    sunrise=sunrise,
                    sunset=sunset
                )
                daily_forecast.append(day_forecast)
            
            forecast = WeatherForecast(
                location=location_name,
                lat=lat,
                lon=lon,
                current=current,
                daily=daily_forecast
            )
            
            logger.info(f"Got {days}-day forecast for {location_name}")
            return forecast
            
        except Exception as e:
            logger.error(f"Error fetching forecast: {e}")
            return None
    
    @classmethod
    def get_best_season(cls, destination: str) -> Optional[BestSeason]:
        """
        Get best time to visit a destination
        
        Args:
            destination: City/destination name
            
        Returns:
            BestSeason object with recommended months
            
        Example:
            season = WeatherService.get_best_season("Goa")
            # Returns: {months: ["October", "November", ...], reason: "..."}
        """
        try:
            dest_lower = destination.lower().strip()
            
            # Check if we have data for this destination
            if dest_lower in cls.DESTINATION_SEASONS:
                data = cls.DESTINATION_SEASONS[dest_lower]
                return BestSeason(
                    destination=destination,
                    months=data["best_months"],
                    reason=data["reason"],
                    avg_temp=data["avg_temp"],
                    avg_precipitation=0.0,  # Not available in free tier
                    rainfall_season=data["rainfall_season"],
                    dry_season=data["dry_season"]
                )
            
            # Generic fallback for unknown destinations
            return BestSeason(
                destination=destination,
                months=["October", "November", "February", "March"],
                reason="Generally pleasant weather in India",
                avg_temp=25,
                avg_precipitation=0.0,
                rainfall_season="June-September",
                dry_season="October-May"
            )
            
        except Exception as e:
            logger.error(f"Error getting best season: {e}")
            return None
    
    @classmethod
    async def get_weather_advisory(
        cls,
        lat: float,
        lon: float,
        trip_date: str  # YYYY-MM-DD
    ) -> str:
        """
        Get weather advisory for a specific date
        
        Args:
            lat: Latitude
            lon: Longitude
            trip_date: Trip date in YYYY-MM-DD format
            
        Returns:
            Advisory message (string)
            
        Example:
            advisory = await WeatherService.get_weather_advisory(15.5, 73.8, "2025-01-15")
        """
        try:
            forecast = await cls.get_forecast(lat, lon, days=16)
            
            if not forecast:
                return "Unable to fetch weather data"
            
            # Find forecast for the trip date
            for day in forecast.daily:
                if day.date == trip_date:
                    message = f"📍 Weather on {trip_date}:\n"
                    message += f"🌡️ {day.min_temp}°C - {day.max_temp}°C\n"
                    message += f"💧 Precipitation: {day.precipitation}mm ({day.precipitation_prob}%)\n"
                    message += f"☁️ {day.condition}\n"
                    
                    if day.precipitation_prob > 70:
                        message += "\n⚠️ High chance of rain - carry umbrella!"
                    elif day.max_temp > 35:
                        message += "\n⚠️ Very hot - stay hydrated!"
                    elif day.max_temp < 10:
                        message += "\n⚠️ Cold weather - wear warm clothes!"
                    
                    return message
            
            return "Date not in forecast range"
            
        except Exception as e:
            logger.error(f"Error generating advisory: {e}")
            return "Unable to generate advisory"

# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

weather_service = WeatherService()

"""
Location Search & Geocoding Service
Uses Nominatim (OpenStreetMap) for location lookup and geocoding
No API key required - free for development and non-commercial use
"""

import httpx
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
from functools import lru_cache
import time
from utils.logger import logger

# IATA CODE MAPPING FOR MAJOR INDIAN DESTINATIONS
DESTINATION_IATA_MAP = {
    # Metro cities
    "delhi": "DEL",
    "mumbai": "BOM",
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "hyderabad": "HYD",
    "kolkata": "CCU",
    "calcutta": "CCU",
    "chennai": "MAA",
    "madras": "MAA",
    "pune": "PNQ",
    "ahmedabad": "AMD",
    "surat": "STV",
    "jaipur": "JAI",
    "lucknow": "LKO",
    "kochi": "COK",
    "cochin": "COK",
    "ernakulam": "COK",
    "thiruvananthapuram": "TRV",
    "trivandrum": "TRV",
    
    # Beach destinations
    "goa": "GOI",
    "panaji": "GOI",
    "dabolim": "GOI",
    
    # Mountain/Adventure
    "manali": "BHO",
    "shimla": "SHL",
    "darjeeling": "BAG",
    "srinagar": "SXR",
    "leh": "LEH",
    "ladakh": "LEH",
    
    # Lake/Nature
    "udaipur": "UDR",
    "kerala": "COK",
    "munnar": "COK",
    "alleppey": "COK",
    "alappuzha": "COK",
    
    # Historical
    "agra": "AGR",
    "varanasi": "VNS",
    "khajuraho": "HJR",
    "ajmer": "AJM",
    "jodhpur": "JDH",
    "pushkar": "JAI",
    "rajasthan": "JAI",
    
    # Northeast
    "guwahati": "GAU",
    "assam": "GAU",
    "shillong": "SHL",
    "dimapur": "DMR",
    
    # Corporate/Business
    "gurugram": "DEL",
    "noida": "DEL",
    "gurgaon": "DEL",
    
    # Tier 2 cities
    "chandigarh": "IXC",
    "indore": "IDR",
    "nagpur": "NAG",
    "bhopal": "BHO",
    "visakhapatnam": "VTZ",
    "vijayawada": "VGA",
    "vadodara": "BRC",
    "baroda": "BRC",
}



class LocationCoords(BaseModel):
    """Location with coordinates"""
    name: str
    lat: float
    lon: float
    display_name: str
    place_type: str  # "city", "town", "state", etc.
    
class LocationSearchResult(BaseModel):
    """Result from location search"""
    name: str
    lat: float
    lon: float
    state: str
    country: str
    display_name: str
    importance: float  # 0-1, higher = more relevant
    
class BoundingBox(BaseModel):
    """Bounding box for an area"""
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    
    def center(self) -> Tuple[float, float]:
        """Get center coordinates"""
        return (
            (self.min_lat + self.max_lat) / 2,
            (self.min_lon + self.max_lon) / 2
        )

# ============================================================================
# LOCATION SERVICE
# ============================================================================

class LocationService:
    """
    Service for location search and geocoding using Nominatim API
    
    Nominatim (OpenStreetMap) free tier:
    - 1 request per second
    - No API key required
    - Full India coverage
    - Reverse geocoding supported
    """
    
    BASE_URL = "https://nominatim.openstreetmap.org"
    TIMEOUT = 10
    
    # Rate limiting: Nominatim requires 1 request per second
    RATE_LIMIT_DELAY = 1.0
    last_request_time = 0.0
    
    # Cache frequently searched locations
    _search_cache: Dict[str, List[LocationSearchResult]] = {}
    _reverse_cache: Dict[str, LocationCoords] = {}
    _bounds_cache: Dict[str, BoundingBox] = {}
    
    CACHE_DURATION = 24 * 3600  # 24 hours
    
    # Indian states for better location context
    INDIAN_STATES = {
        "Goa", "Maharashtra", "Karnataka", "Kerala", "Tamil Nadu",
        "Telangana", "Andhra Pradesh", "Rajasthan", "Gujarat", "Uttar Pradesh",
        "Punjab", "Himachal Pradesh", "Jammu and Kashmir", "Uttarakhand",
        "Haryana", "Madhya Pradesh", "Chhattisgarh", "Odisha", "West Bengal",
        "Assam", "Meghalaya", "Nagaland", "Manipur", "Mizoram", "Tripura",
        "Sikkim", "Arunachal Pradesh", "Bihar", "Jharkhand"
    }
    
    @classmethod
    async def _rate_limit(cls):
        """Enforce Nominatim rate limit (1 request per second)"""
        current_time = time.time()
        time_since_last_request = current_time - cls.last_request_time
        
        if time_since_last_request < cls.RATE_LIMIT_DELAY:
            delay_needed = cls.RATE_LIMIT_DELAY - time_since_last_request
            await asyncio.sleep(delay_needed)
        
        cls.last_request_time = time.time()
    
    @classmethod
    async def search_locations(
        cls,
        query: str,
        country: str = "India",
        limit: int = 10
    ) -> List[LocationSearchResult]:
        """
        Search for locations by name
        
        Args:
            query: Search string (e.g., "Goa", "Mumbai")
            country: Country to search in (default: India)
            limit: Max results to return (default: 10)
            
        Returns:
            List of LocationSearchResult with coordinates and details
            
        Example:
            results = await LocationService.search_locations("Goa")
            # Returns: [{name: "Goa", lat: 15.5, lon: 73.8, ...}]
        """
        try:
            # Check cache first
            cache_key = f"{query.lower()}:{country}"
            if cache_key in cls._search_cache:
                logger.info(f"Location search cache hit: {query}")
                return cls._search_cache[cache_key]
            
            # Rate limiting
            await cls._rate_limit()
            
            # Make API request
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.get(
                    f"{cls.BASE_URL}/search",
                    params={
                        "q": f"{query}, {country}",
                        "format": "json",
                        "limit": limit,
                        "addressdetails": 1,
                        "countrycodes": "in"  # India country code
                    },
                    headers={"User-Agent": "SimpliTrip/1.0"}
                )
                response.raise_for_status()
                
            data = response.json()
            
            if not data:
                logger.warning(f"No locations found for query: {query}")
                return []
            
            # Parse results
            results = []
            for item in data:
                try:
                    # Extract state from address details
                    address = item.get("address", {})
                    state = address.get("state", "Unknown")
                    
                    result = LocationSearchResult(
                        name=item.get("name", "Unknown"),
                        lat=float(item["lat"]),
                        lon=float(item["lon"]),
                        state=state,
                        country=address.get("country", "India"),
                        display_name=item.get("display_name", ""),
                        importance=float(item.get("importance", 0))
                    )
                    results.append(result)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Failed to parse location result: {e}")
                    continue
            
            # Sort by importance
            results.sort(key=lambda x: x.importance, reverse=True)
            
            # Cache results
            cls._search_cache[cache_key] = results
            
            logger.info(f"Found {len(results)} locations for: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Location search error: {e}")
            raise
    
    @classmethod
    async def reverse_geocode(
        cls,
        lat: float,
        lon: float
    ) -> Optional[LocationCoords]:
        """
        Get location name from coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            LocationCoords with name and details, or None if not found
            
        Example:
            location = await LocationService.reverse_geocode(15.5, 73.8)
            # Returns: {name: "Goa", lat: 15.5, lon: 73.8, ...}
        """
        try:
            # Check cache
            cache_key = f"{lat}:{lon}"
            if cache_key in cls._reverse_cache:
                logger.info(f"Reverse geocode cache hit: {lat}, {lon}")
                return cls._reverse_cache[cache_key]
            
            # Rate limiting
            await cls._rate_limit()
            
            # Make API request
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.get(
                    f"{cls.BASE_URL}/reverse",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "format": "json",
                        "zoom": 10,
                        "addressdetails": 1
                    },
                    headers={"User-Agent": "SimpliTrip/1.0"}
                )
                response.raise_for_status()
            
            data = response.json()
            
            if not data:
                logger.warning(f"No location found for coords: {lat}, {lon}")
                return None
            
            address = data.get("address", {})
            
            result = LocationCoords(
                name=data.get("name") or address.get("city") or address.get("town") or "Unknown",
                lat=float(data["lat"]),
                lon=float(data["lon"]),
                display_name=data.get("display_name", ""),
                place_type=data.get("type", "location")
            )
            
            # Cache result
            cls._reverse_cache[cache_key] = result
            
            logger.info(f"Reverse geocoded: {result.name} at {lat}, {lon}")
            return result
            
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
            return None
    
    @classmethod
    async def get_city_bounds(
        cls,
        city_name: str
    ) -> Optional[BoundingBox]:
        """
        Get bounding box for a city (useful for map display)
        
        Args:
            city_name: Name of city (e.g., "Goa", "Mumbai")
            
        Returns:
            BoundingBox with min/max coordinates, or None if not found
            
        Example:
            bounds = await LocationService.get_city_bounds("Goa")
            # Returns: {min_lat: 14.8, max_lat: 15.9, min_lon: 73.7, max_lon: 74.3}
        """
        try:
            # Check cache
            if city_name in cls._bounds_cache:
                logger.info(f"Bounds cache hit: {city_name}")
                return cls._bounds_cache[city_name]
            
            # Search for city first
            results = await cls.search_locations(city_name, limit=1)
            if not results:
                return None
            
            # Rate limiting
            await cls._rate_limit()
            
            # Get detailed info with bbox
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.get(
                    f"{cls.BASE_URL}/search",
                    params={
                        "q": f"{city_name}, India",
                        "format": "json",
                        "limit": 1,
                        "addressdetails": 1,
                        "countrycodes": "in"
                    },
                    headers={"User-Agent": "SimpliTrip/1.0"}
                )
                response.raise_for_status()
            
            data = response.json()
            if not data:
                return None
            
            item = data[0]
            
            # Extract bounding box
            if "boundingbox" in item:
                bbox = item["boundingbox"]
                # Format: [min_lat, max_lat, min_lon, max_lon]
                bounds = BoundingBox(
                    min_lat=float(bbox[0]),
                    max_lat=float(bbox[1]),
                    min_lon=float(bbox[2]),
                    max_lon=float(bbox[3])
                )
                
                # Cache
                cls._bounds_cache[city_name] = bounds
                logger.info(f"Got bounds for {city_name}: {bounds}")
                return bounds
            
            return None
            
        except Exception as e:
            logger.error(f"Get bounds error: {e}")
            return None
    
    @classmethod
    async def autocomplete_locations(
        cls,
        query: str,
        limit: int = 5
    ) -> List[str]:
        """
        Get location suggestions for autocomplete
        
        Args:
            query: Partial city/location name
            limit: Max suggestions
            
        Returns:
            List of location display names
            
        Example:
            suggestions = await LocationService.autocomplete_locations("Mu")
            # Returns: ["Mumbai", "Mulund", "Mussorie", ...]
        """
        try:
            if len(query) < 2:
                return []
            
            results = await cls.search_locations(query, limit=limit)
            return [r.display_name.split(",")[0] for r in results]
            
        except Exception as e:
            logger.error(f"Autocomplete error: {e}")
            return []
    
    @classmethod
    def clear_cache(cls):
        """Clear all cached data"""
        cls._search_cache.clear()
        cls._reverse_cache.clear()
        cls._bounds_cache.clear()
        logger.info("Location service cache cleared")
    
    @classmethod
    def get_iata_code(cls, destination: str) -> Optional[str]:
        """
        Get IATA airport code for a destination
        
        Args:
            destination: City or destination name (e.g., "Goa", "Mumbai")
            
        Returns:
            3-letter IATA code (e.g., "GOI", "BOM"), or None if not found
            
        Example:
            iata = LocationService.get_iata_code("Goa")
            # Returns: "GOI"
        """
        if not destination:
            return None
        
        # Normalize to lowercase
        normalized = destination.strip().lower()
        
        # Check direct mapping
        if normalized in DESTINATION_IATA_MAP:
            iata = DESTINATION_IATA_MAP[normalized]
            logger.info(f"✈️ Found IATA for {destination}: {iata}")
            return iata
        
        # Try partial matching
        for dest_key, iata_code in DESTINATION_IATA_MAP.items():
            if dest_key in normalized or normalized in dest_key:
                logger.info(f"✈️ Partial match IATA for {destination}: {iata_code}")
                return iata_code
        
        logger.warning(f"⚠️ No IATA code found for destination: {destination}")
        # Default to Delhi if not found
        return "DEL"



# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

location_service = LocationService()

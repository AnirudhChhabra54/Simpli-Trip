import os
import logging
from amadeus import Client, ResponseError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger("AmadeusService")

class AmadeusService:
    def __init__(self):
        self.amadeus = Client(
            client_id=os.getenv("AMADEUS_API_KEY"),
            client_secret=os.getenv("AMADEUS_API_SECRET")
        )
        self.is_available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if Amadeus API is available"""
        api_key = os.getenv("AMADEUS_API_KEY")
        api_secret = os.getenv("AMADEUS_API_SECRET")
        
        if not api_key or not api_secret:
            logger.warning("⚠️ Amadeus API keys not configured")
            return False
        
        logger.info("✅ Amadeus API service initialized")
        return True

    def search_flights(self, origin: str, destination: str, departure_date: str, 
                      adults: int = 1, return_date: str = None, max_results: int = 10):
        """
        Searches for flights and returns results in INR.
        
        Args:
            origin: IATA code of origin (e.g., 'DEL')
            destination: IATA code of destination (e.g., 'GOI')
            departure_date: Date in YYYY-MM-DD format
            adults: Number of adult passengers (default 1)
            return_date: Return date for round trip (optional)
            max_results: Maximum number of results (default 10)
            
        Returns:
            List of flight offers or error dict
        """
        try:
            if not self.is_available:
                return {"error": "Amadeus API not configured", "status": "unavailable"}
            
            # Prepare search parameters
            params = {
                "originLocationCode": origin.upper(),
                "destinationLocationCode": destination.upper(),
                "departureDate": departure_date,
                "adults": adults,
                "currencyCode": "INR",  # Force INR currency
                "max": max_results
            }
            
            # Add return date for round trip
            if return_date:
                params["returnDate"] = return_date
            
            logger.info(f"🔍 Searching flights: {origin} → {destination} on {departure_date}")
            
            response = self.amadeus.shopping.flight_offers_search.get(**params)
            
            flights = self._parse_flight_data(response.data)
            logger.info(f"✅ Found {len(flights)} flights")
            return flights

        except ResponseError as error:
            logger.error(f"❌ Amadeus API Error: {error}")
            return {"error": str(error), "status": "api_error"}
        except Exception as e:
            logger.error(f"❌ Unexpected Error: {e}")
            return {"error": str(e), "status": "error"}

    def _parse_flight_data(self, offers):
        """
        Parse and clean Amadeus API response
        
        Returns structured flight data with all important info
        """
        clean_results = []
        
        for offer in offers:
            try:
                flight_info = {
                    "id": offer['id'],
                    "price": float(offer['price']['total']),
                    "pricingPerAdult": float(offer['price'].get('base', offer['price']['total'])),
                    "currency": offer['price']['currency'],
                    "airline": "",
                    "flight_number": "",
                    "duration": "",
                    "stops": 0,
                    "segments": [],
                    "departure": "",
                    "arrival": "",
                    "departureTime": "",
                    "arrivalTime": ""
                }
                
                # Process itinerary (assuming first itinerary for simplicity)
                if offer['itineraries']:
                    itinerary = offer['itineraries'][0]
                    flight_info['duration'] = itinerary.get('duration', 'N/A')
                    flight_info['stops'] = len(itinerary['segments']) - 1
                    
                    for idx, segment in enumerate(itinerary['segments']):
                        segment_detail = {
                            "departure": segment['departure']['iataCode'],
                            "departureTime": segment['departure']['at'],
                            "arrival": segment['arrival']['iataCode'],
                            "arrivalTime": segment['arrival']['at'],
                            "airline": segment['carrierCode'],
                            "flightNumber": f"{segment['carrierCode']}{segment['number']}",
                            "aircraft": segment.get('aircraft', {}).get('code', 'N/A'),
                            "duration": segment.get('duration', 'N/A')
                        }
                        flight_info['segments'].append(segment_detail)
                        
                        # Set main departure/arrival from first segment
                        if idx == 0:
                            flight_info['departure'] = segment['departure']['iataCode']
                            flight_info['departureTime'] = segment['departure']['at']
                            flight_info['airline'] = segment['carrierCode']
                            flight_info['flight_number'] = f"{segment['carrierCode']}{segment['number']}"
                        
                        # Update arrival from last segment
                        flight_info['arrival'] = segment['arrival']['iataCode']
                        flight_info['arrivalTime'] = segment['arrival']['at']
                    
                    # Add passenger info if available
                    if 'travelerPricings' in offer:
                        flight_info['passengers'] = len(offer['travelerPricings'])
                
                clean_results.append(flight_info)
                
            except Exception as e:
                logger.warning(f"Error parsing flight offer: {e}")
                continue
        
        return clean_results

# --- Simple Test Block ---
if __name__ == '__main__':
    # Ensure keys are set in your terminal or .env before running
    # export AMADEUS_API_KEY="your_key"
    # export AMADEUS_API_SECRET="your_secret"
    
    service = AmadeusService()
    print("Searching for flights (INR)...")
    
    # Test with tomorrow's date or a valid future date
    results = service.search_flights("DEL", "GOI", "2025-12-25")
    
    if isinstance(results, list):
        print(f"✅ Found {len(results)} flights:\n")
        for flight in results[:3]: # Print first 3
            print(f"✈️  {flight['airline']} {flight['flight_number']}")
            print(f"💰 Price: ₹{flight['price']}")
            print(f"📍 Route: {flight['segments'][0]['departure']} -> {flight['segments'][-1]['arrival']}")
            print("-" * 30)
    else:
        print(results)
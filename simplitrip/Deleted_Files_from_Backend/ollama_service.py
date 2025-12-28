"""
Enhanced Ollama Service with better error handling, fallbacks, and health checks
"""
import re
import os
import time
import json
import logging
from typing import Dict, Any, Optional, List
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("OllamaService")

# Configuration with defaults
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi:latest")  # Default to phi model
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", 30))
OLLAMA_RETRIES = int(os.getenv("OLLAMA_RETRIES", 2))
OLLAMA_BACKOFF = float(os.getenv("OLLAMA_BACKOFF", 1.0))

class OllamaService:
    def __init__(self, host: str = OLLAMA_HOST, model: str = OLLAMA_MODEL):
        self.host = host.rstrip("/")
        self.model = model
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "SimpliTrip/1.0"
        })
        self.timeout = OLLAMA_TIMEOUT
        self._available = None
        self._last_health_check = 0
        self.health_check_interval = 30  # seconds

    def _health_check(self) -> bool:
        """Check if Ollama is available with caching"""
        current_time = time.time()
        if (self._available is None or 
            current_time - self._last_health_check > self.health_check_interval):
            
            try:
                # Try multiple endpoints
                endpoints = ["/api/tags", "/api/version", "/"]
                for endpoint in endpoints:
                    try:
                        resp = self.session.get(
                            f"{self.host}{endpoint}", 
                            timeout=5
                        )
                        if resp.status_code == 200:
                            self._available = True
                            self._last_health_check = current_time
                            logger.info("Ollama service is available")
                            return True
                    except requests.exceptions.RequestException:
                        continue
                
                self._available = False
                logger.warning("Ollama service is not available")
                
            except Exception as e:
                self._available = False
                logger.error(f"Health check failed: {e}")
        
        return self._available

    def is_available(self) -> bool:
        """Public method to check availability"""
        return self._health_check()

    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        if not self.is_available():
            return []
        
        try:
            resp = self.session.get(f"{self.host}/api/tags", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            logger.error(f"Failed to get models: {e}")
        
        return []

    def _make_request(self, endpoint: str, payload: Dict[str, Any], stream: bool = False):
        """Make request with retries and proper error handling"""
        url = f"{self.host}{endpoint}"
        
        for attempt in range(OLLAMA_RETRIES + 1):
            try:
                logger.debug(f"Attempt {attempt + 1} to {url}")
                
                if stream:
                    response = self.session.post(
                        url, 
                        json=payload, 
                        timeout=self.timeout,
                        stream=True
                    )
                else:
                    response = self.session.post(
                        url, 
                        json=payload, 
                        timeout=self.timeout
                    )
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error (attempt {attempt + 1}): {e}")
                if attempt < OLLAMA_RETRIES:
                    time.sleep(OLLAMA_BACKOFF * (attempt + 1))
                    continue
                raise RuntimeError(f"Cannot connect to Ollama at {self.host}. Please ensure Ollama is running.")
                
            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout error (attempt {attempt + 1}): {e}")
                if attempt < OLLAMA_RETRIES:
                    continue
                raise RuntimeError("Ollama request timed out. The model might be busy or too slow.")
                
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error {response.status_code}: {e}")
                if response.status_code == 404:
                    raise RuntimeError(f"Model '{self.model}' not found. Available models: {', '.join(self.get_available_models())}")
                raise RuntimeError(f"Ollama API error: {e}")
                
            except Exception as e:
                logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
                if attempt < OLLAMA_RETRIES:
                    time.sleep(OLLAMA_BACKOFF * (attempt + 1))
                    continue
                raise RuntimeError(f"Ollama request failed: {e}")

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 300,
        stream: bool = False  # Default to non-streaming for reliability
    ) -> str:
        """
        Generate text using Ollama with robust error handling
        """
        if not self.is_available():
            available_models = self.get_available_models()
            error_msg = f"Ollama is not available at {self.host}. "
            if available_models:
                error_msg += f"Available models: {', '.join(available_models)}"
            else:
                error_msg += "Please install and run Ollama first."
            raise RuntimeError(error_msg)

        if not self.model:
            available_models = self.get_available_models()
            raise RuntimeError(
                f"No model specified. Available models: {', '.join(available_models)}"
            )

        # Check if model is available
        available_models = self.get_available_models()
        if available_models and self.model not in available_models:
            raise RuntimeError(
                f"Model '{self.model}' not found. Available models: {', '.join(available_models)}"
            )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system or "You are a helpful assistant.",
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            },
            "stream": stream
        }

        try:
            response = self._make_request("/api/generate", payload, stream=stream)
            
            if stream:
                return self._handle_stream_response(response)
            else:
                return self._handle_json_response(response)
                
        except RuntimeError as e:
            # Re-raise our custom errors
            raise
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise RuntimeError(f"Text generation failed: {e}")

    def _handle_json_response(self, response) -> str:
        """Handle non-streaming JSON response"""
        try:
            data = response.json()
            return data.get("response", "").strip()
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return response.text.strip()

    def _handle_stream_response(self, response) -> str:
        """Handle streaming response"""
        full_response = []
        
        try:
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            full_response.append(data["response"])
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Error processing stream: {e}")
        
        return "".join(full_response).strip()

    def parse_trip_query(self, query: str) -> Dict[str, Any]:
        """
        Parse travel query with fallback to regex if Ollama is unavailable
        """
        # Always try regex fallback first - it's faster and more reliable
        fallback_result = self._regex_parse_query(query)
        
        # If Ollama is available and we want to use LLM for better parsing
        if self.is_available():
            try:
                llm_result = self._llm_parse_query(query)
                # Use LLM result if it has higher confidence or found more fields
                if (llm_result.get('confidence', 0) > fallback_result.get('confidence', 0) or
                    (llm_result.get('destination') and not fallback_result.get('destination'))):
                    return llm_result
            except Exception as e:
                logger.warning(f"LLM parsing failed, using regex fallback: {e}")
        
        return fallback_result

    def _regex_parse_query(self, query: str) -> Dict[str, Any]:
        """Robust regex-based query parsing"""
        import re
        
        query_lower = query.lower()
        result = {
            "destination": None,
            "duration": None,
            "budget": None,
            "travelers": None,
            "preferences": [],
            "meal_preference": "veg",
            "accommodation_type": "hotel",
            "transport_mode": "flight",
            "season": None,
            "confidence": 0.7,
            "raw_query": query
        }
        
        # Destination mapping
        destinations = {
            'delhi': 'Delhi', 'mumbai': 'Mumbai', 'goa': 'Goa', 
            'jaipur': 'Jaipur', 'kerala': 'Kerala', 'manali': 'Manali',
            'ladakh': 'Ladakh', 'shimla': 'Shimla', 'darjeeling': 'Darjeeling',
            'varanasi': 'Varanasi', 'agra': 'Agra', 'hyderabad': 'Hyderabad',
            'chennai': 'Chennai', 'bangalore': 'Bangalore', 'kolkata': 'Kolkata',
            'ahmedabad': 'Ahmedabad', 'pune': 'Pune', 'kochi': 'Kochi'
        }
        
        # Find destination
        for dest_key, dest_name in destinations.items():
            if dest_key in query_lower:
                result["destination"] = dest_name
                result["confidence"] = 0.9
                break
        
        # Duration (days)
        day_match = re.search(r'(\d+)\s*day', query_lower)
        if day_match:
            result["duration"] = int(day_match.group(1))
        
        # Travelers
        traveler_match = re.search(r'(\d+)\s*(?:people|persons|person|travelers|friends)', query_lower)
        if traveler_match:
            result["travelers"] = int(traveler_match.group(1))
        else:
            # Default to 2 travelers
            result["travelers"] = 2
        
        # Budget
        budget_match = re.search(r'[₹$]?\s*(\d+[,]?\d*)\s*(?:k|thousand)?', query_lower)
        if budget_match:
            budget_str = budget_match.group(1).replace(',', '')
            result["budget"] = int(budget_str) * 1000 if 'k' in query_lower else int(budget_str)
        
        # Preferences
        preference_keywords = {
            'beach': 'beach', 'mountain': 'mountain', 'adventure': 'adventure',
            'historical': 'historical', 'cultural': 'cultural', 'religious': 'religious',
            'honeymoon': 'romantic', 'romantic': 'romantic', 'family': 'family',
            'budget': 'budget', 'luxury': 'luxury', 'wildlife': 'wildlife'
        }
        
        for keyword, preference in preference_keywords.items():
            if keyword in query_lower:
                result["preferences"].append(preference)
        
        # Meal preference
        if 'non-veg' in query_lower or 'non veg' in query_lower:
            result["meal_preference"] = "non-veg"
        elif 'veg' in query_lower:
            result["meal_preference"] = "veg"
        elif 'vegan' in query_lower:
            result["meal_preference"] = "vegan"
        
        return result

    def _llm_parse_query(self, query: str) -> Dict[str, Any]:
        """Use LLM for more sophisticated query parsing"""
        prompt = f"""
        Parse this travel query into structured JSON. Extract:
        - destination (city/place name)
        - duration (number of days)
        - budget (numeric amount in INR)
        - travelers (number of people)
        - preferences (list: beach, mountain, adventure, historical, cultural, religious, romantic, family, budget, luxury, wildlife)
        - meal_preference (veg/non-veg/vegan)
        - accommodation_type (hotel/resort/hostel)
        - transport_mode (flight/train/bus)
        - season (summer/winter/monsoon/autumn/spring)
        - confidence (0.0 to 1.0)

        Query: "{query}"

        Return ONLY valid JSON, no other text.
        Example: {{"destination": "Goa", "duration": 5, "budget": 50000, "travelers": 2, "preferences": ["beach", "adventure"], "meal_preference": "non-veg", "accommodation_type": "hotel", "transport_mode": "flight", "season": "winter", "confidence": 0.9}}
        """
        
        try:
            response = self.generate(
                prompt=prompt,
                system="You are a travel query parser. Return only valid JSON.",
                temperature=0.1,
                max_tokens=200,
                stream=False
            )
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._regex_parse_query(query)
                
        except Exception as e:
            logger.warning(f"LLM parsing failed: {e}")
            return self._regex_parse_query(query)

# Global instance
ollama_service = OllamaService()
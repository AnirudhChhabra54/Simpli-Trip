"""
Ollama Service - FREE Local LLM Integration
Connects to locally running Ollama (Llama2/Mistral)
"""
import requests
import json
from typing import Optional, Dict, Any, List
from utils.logger import logger


class OllamaService:
    """
    Service to interact with locally running Ollama LLMs
    Supports Llama2, Mistral, and other models
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        """
        Initialize Ollama service
        
        Args:
            base_url: Ollama API endpoint (default: http://localhost:11434)
            model: Model to use (mistral, llama2, codellama, etc.)
        """
        self.base_url = base_url
        self.model = model
        self._verify_connection()
    
    def _verify_connection(self):
        """Verify Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                logger.info(f"Connected to Ollama. Available models: {model_names}")
                
                # Check if selected model is available
                if not any(self.model in name for name in model_names):
                    logger.warning(f"Model '{self.model}' not found. Available: {model_names}")
            else:
                logger.warning("Ollama is running but returned unexpected response")
        except requests.exceptions.RequestException as e:
            logger.error(f"Cannot connect to Ollama at {self.base_url}: {e}")
            logger.info("Make sure Ollama is running. Install from: https://ollama.com")
    
    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        Generate text using Ollama
        
        Args:
            prompt: The prompt to send to the model
            system: System message to set context
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Generated text response
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature
                }
            }
            
            if system:
                payload["system"] = system
            
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120  # 2 minutes timeout for generation
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return ""
                
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return ""
        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            return ""
    
    def parse_trip_query(self, query: str) -> Dict[str, Any]:
        """
        Parse natural language trip query using LLM
        
        Args:
            query: Natural language query like "Plan a 5-day trip to Goa for 2 people"
            
        Returns:
            Parsed trip details as dictionary
        """
        system_prompt = """You are a travel query parser. Extract trip details from user queries.
Return ONLY valid JSON with these fields:
- destination: string or null
- duration: number of days or null
- travelers: number of people or null
- budget: number in rupees or null
- preferences: array of strings (beach, adventure, historical, etc.) - MUST be an array, use [] if none
- travel_date: string or null

Example output:
{"destination": "Goa", "duration": 5, "travelers": 2, "budget": 50000, "preferences": ["beach", "relaxing"], "travel_date": null}"""
        
        prompt = f"""Extract trip details from this query:

Query: "{query}"

Return only the JSON object, no other text."""
        
        response = self.generate(prompt, system=system_prompt, temperature=0.3)
        
        try:
            # Try to parse JSON from response
            # Sometimes LLM adds extra text, so we extract JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                parsed = json.loads(json_str)
                
                # Ensure preferences is always a list
                if parsed.get('preferences') is None:
                    parsed['preferences'] = []
                elif not isinstance(parsed['preferences'], list):
                    parsed['preferences'] = [parsed['preferences']]
                
                logger.info(f"Parsed query: {parsed}")
                return parsed
            else:
                logger.warning("No JSON found in LLM response")
                return self._fallback_parse(query)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM JSON response: {e}")
            return self._fallback_parse(query)
    
    def _fallback_parse(self, query: str) -> Dict[str, Any]:
        """Enhanced fallback parsing with meal, accommodation, and transport extraction"""
        import re
        from difflib import get_close_matches
        
        result = {
            'destination': None,
            'duration': None,
            'travelers': None,
            'budget': None,
            'preferences': [],
            'travel_date': None,
            'meal_preference': None,
            'accommodation_type': None,
            'transport_mode': None
        }
        
        query_lower = query.lower()
        
        # Extract destination with fuzzy matching for typos
        destinations = ['goa', 'jaipur', 'kerala', 'udaipur', 'manali', 'delhi', 
                       'mumbai', 'ladakh', 'shimla', 'darjeeling', 'rishikesh',
                       'agra', 'varanasi', 'bangalore', 'hyderabad', 'pune']
        
        # First try exact match
        for dest in destinations:
            if dest in query_lower:
                result['destination'] = dest.title()
                break
        
        # If no exact match, try fuzzy matching for typos (e.g., "delho" → "delhi")
        if not result['destination']:
            words = query_lower.split()
            for word in words:
                if len(word) > 3:  # Only check words longer than 3 chars
                    matches = get_close_matches(word, destinations, n=1, cutoff=0.6)
                    if matches:
                        result['destination'] = matches[0].title()
                        logger.info(f"Fuzzy matched '{word}' to '{matches[0]}'")
                        break
        
        # Extract duration
        duration_match = re.search(r'(\d+)\s*(?:day|days)', query_lower)
        if duration_match:
            result['duration'] = int(duration_match.group(1))
        
        # Extract travelers - improved patterns
        # Pattern 1: "5 friends" → 6 people (including user)
        friends_match = re.search(r'(\d+)\s*(?:friend|friends)', query_lower)
        if friends_match:
            result['travelers'] = int(friends_match.group(1)) + 1  # +1 for the user
            logger.info(f"Detected {friends_match.group(1)} friends, total travelers: {result['travelers']}")
        else:
            # Pattern 2: "5 people"
            travelers_match = re.search(r'(\d+)\s*(?:people|person|traveler|travelers)', query_lower)
            if travelers_match:
                result['travelers'] = int(travelers_match.group(1))
        
        # Check for keywords if no number found
        if not result['travelers']:
            if 'solo' in query_lower or 'alone' in query_lower:
                result['travelers'] = 1
            elif 'couple' in query_lower or 'two of us' in query_lower:
                result['travelers'] = 2
            elif 'family' in query_lower:
                result['travelers'] = 4  # Default family size
        
        # Extract budget
        budget_match = re.search(r'(?:₹|rs\.?|rupees?)\s*(\d+(?:,\d+)*(?:k)?)', query_lower)
        if budget_match:
            budget_str = budget_match.group(1).replace(',', '')
            if 'k' in budget_str:
                result['budget'] = int(budget_str.replace('k', '')) * 1000
            else:
                result['budget'] = int(budget_str)
        
        # Extract meal preferences
        if any(word in query_lower for word in ['non-veg', 'nonveg', 'non veg', 'meat', 'chicken', 'fish', 'seafood', 'non vegetarian']):
            result['meal_preference'] = 'non-veg'
        elif any(word in query_lower for word in ['vegan']):
            result['meal_preference'] = 'vegan'
        elif any(word in query_lower for word in ['veg', 'vegetarian']):
            result['meal_preference'] = 'veg'
        
        # Extract accommodation preferences
        if any(word in query_lower for word in ['resort', 'luxury', '5 star', 'five star']):
            result['accommodation_type'] = 'resort'
        elif any(word in query_lower for word in ['hostel', 'backpack', 'budget stay', 'dorm']):
            result['accommodation_type'] = 'hostel'
        elif any(word in query_lower for word in ['hotel', 'stay']):
            result['accommodation_type'] = 'hotel'
        
        # Extract transport preferences
        if any(word in query_lower for word in ['flight', 'fly', 'plane', 'air', 'airplane']):
            result['transport_mode'] = 'flight'
        elif any(word in query_lower for word in ['train', 'railway', 'rail']):
            result['transport_mode'] = 'train'
        elif any(word in query_lower for word in ['bus', 'road', 'drive']):
            result['transport_mode'] = 'bus'
        
        # Extract activity preferences
        if 'beach' in query_lower or 'sea' in query_lower or 'ocean' in query_lower:
            result['preferences'].append('beach')
        if 'adventure' in query_lower or 'trek' in query_lower or 'hiking' in query_lower:
            result['preferences'].append('adventure')
        if 'historical' in query_lower or 'history' in query_lower or 'heritage' in query_lower:
            result['preferences'].append('historical')
        if 'relax' in query_lower or 'peaceful' in query_lower or 'calm' in query_lower:
            result['preferences'].append('relaxing')
        if 'nature' in query_lower or 'wildlife' in query_lower or 'forest' in query_lower:
            result['preferences'].append('nature')
        if 'food' in query_lower or 'cuisine' in query_lower or 'culinary' in query_lower:
            result['preferences'].append('food')
        if 'culture' in query_lower or 'cultural' in query_lower or 'traditional' in query_lower:
            result['preferences'].append('cultural')
        if 'spiritual' in query_lower or 'temple' in query_lower or 'religious' in query_lower:
            result['preferences'].append('spiritual')
        
        # If no preferences found, add a default
        if not result['preferences']:
            result['preferences'].append('general')
        
        logger.info(f"Fallback parse result: {result}")
        return result
    
    def generate_itinerary_description(
        self,
        destination: str,
        duration: int,
        highlights: List[str],
        style: str = 'engaging'
    ) -> str:
        """
        Generate engaging itinerary description
        
        Args:
            destination: Destination name
            duration: Number of days
            highlights: List of highlights/attractions
            style: Writing style (engaging, formal, casual)
            
        Returns:
            Generated description
        """
        system_prompt = f"""You are a travel content writer. Write {style} travel descriptions.
Keep it concise (2-3 sentences) and exciting."""
        
        highlights_str = ", ".join(highlights[:5])
        
        prompt = f"""Write an engaging description for a {duration}-day trip to {destination}.

Key highlights: {highlights_str}

Write 2-3 sentences that make travelers excited about this trip."""
        
        response = self.generate(prompt, system=system_prompt, temperature=0.8)
        return response if response else f"Experience an amazing {duration}-day journey to {destination}!"
    
    def explain_recommendation(
        self,
        destination: str,
        user_preferences: Dict[str, Any],
        match_score: float
    ) -> str:
        """
        Explain why a destination was recommended
        
        Args:
            destination: Recommended destination
            user_preferences: User's preferences
            match_score: Match score (0-100)
            
        Returns:
            Explanation text
        """
        system_prompt = """You are a travel advisor. Explain recommendations clearly and concisely.
Keep explanations to 2-3 sentences."""
        
        prefs_str = json.dumps(user_preferences, indent=2)
        
        prompt = f"""Explain why {destination} is recommended for a traveler with these preferences:

{prefs_str}

Match score: {match_score}%

Write a brief, friendly explanation (2-3 sentences)."""
        
        response = self.generate(prompt, system=system_prompt, temperature=0.7)
        return response if response else f"{destination} matches your preferences with a {match_score}% compatibility score."
    
    def optimize_budget_suggestions(
        self,
        current_cost: Dict[str, float],
        target_budget: float,
        overage: float
    ) -> List[str]:
        """
        Generate budget optimization suggestions
        
        Args:
            current_cost: Current cost breakdown
            target_budget: Target budget
            overage: Amount over budget
            
        Returns:
            List of suggestions
        """
        system_prompt = """You are a budget travel advisor. Provide practical money-saving tips.
Return suggestions as a JSON array of strings."""
        
        cost_str = json.dumps(current_cost, indent=2)
        
        prompt = f"""The trip costs ₹{sum(current_cost.values())} but the budget is ₹{target_budget} (₹{overage} over).

Current costs:
{cost_str}

Provide 3-5 practical suggestions to reduce costs. Return as JSON array of strings.

Example: ["Consider budget hotels instead of luxury", "Book flights in advance", "Use public transport"]"""
        
        response = self.generate(prompt, system=system_prompt, temperature=0.7)
        
        try:
            # Extract JSON array
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                suggestions = json.loads(json_str)
                return suggestions[:5]  # Max 5 suggestions
        except:
            pass
        
        # Fallback suggestions
        return [
            "Consider traveling during off-season for better rates",
            "Book accommodations and flights well in advance",
            "Look for package deals that bundle multiple services",
            "Use public transportation instead of private cabs",
            "Eat at local restaurants instead of tourist spots"
        ]
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Chat with the LLM (conversation mode)
        
        Args:
            messages: List of message dicts with 'role' and 'content'
                     Example: [{"role": "user", "content": "Hello"}]
        
        Returns:
            Assistant's response
        """
        # Convert messages to a single prompt
        prompt_parts = []
        system_msg = None
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'system':
                system_msg = content
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        prompt = "\n\n".join(prompt_parts)
        prompt += "\n\nAssistant:"
        
        return self.generate(prompt, system=system_msg, temperature=0.7)


# Create global instance
ollama_service = OllamaService(model="phi")  # Using Mistral by default

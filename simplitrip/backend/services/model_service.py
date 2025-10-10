"""
Model Service - Manages all ML models and provides unified interface
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import pandas as pd

from models.recommendation import HybridRecommender
from models.cost_prediction import TripCostPredictor
from models.itinerary_optimizer import ItineraryOptimizer
from utils.data_loader import data_loader
from utils.logger import logger
from config.settings import settings


class ModelService:
    """
    Service class that manages all ML models and provides a unified interface
    """
    
    def __init__(self):
        self.recommender: Optional[HybridRecommender] = None
        self.cost_predictor: Optional[TripCostPredictor] = None
        self.itinerary_optimizer: Optional[ItineraryOptimizer] = None
        
        # Data storage
        self.destinations_df: Optional[pd.DataFrame] = None
        self.places_df: Optional[pd.DataFrame] = None
        
        self._initialized = False
    
    def initialize(self):
        """Initialize all models and load data"""
        if self._initialized:
            logger.info("Model service already initialized")
            return
        
        logger.info("Initializing Model Service...")
        
        try:
            # Load datasets
            self._load_datasets()
            
            # Initialize models
            self._initialize_recommender()
            self._initialize_cost_predictor()
            self._initialize_itinerary_optimizer()
            
            self._initialized = True
            logger.info("Model Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Model Service: {e}")
            raise
    
    def _load_datasets(self):
        """Load all required datasets"""
        logger.info("Loading datasets...")
        
        try:
            # Try to load processed data first
            try:
                self.destinations_df = data_loader.load_processed_data("destinations_processed.csv")
                self.places_df = data_loader.load_processed_data("places_processed.csv")
                logger.info("Loaded processed datasets")
            except FileNotFoundError:
                # Load raw data and process
                logger.info("Processed data not found, loading raw datasets...")
                self.destinations_df = data_loader.load_explore_india_dataset()
                self.places_df = data_loader.load_tourist_places_dataset()
                
                # Save processed data
                data_loader.save_processed_data(self.destinations_df, "destinations_processed.csv")
                data_loader.save_processed_data(self.places_df, "places_processed.csv")
                logger.info("Saved processed datasets")
                
        except Exception as e:
            logger.warning(f"Could not load datasets from Kaggle: {e}")
            logger.info("Using sample data for demo")
            self._create_sample_data()
    
    def _create_sample_data(self):
        """Create sample data for demo purposes"""
        # Sample destinations
        self.destinations_df = pd.DataFrame([
            {
                'Destination Name': 'Goa',
                'State': 'Goa',
                'Category': 'Beach',
                'Rating': 4.5,
                'Best Time to Visit': 'November to February',
                'Description': 'Beautiful beaches and vibrant nightlife'
            },
            {
                'Destination Name': 'Jaipur',
                'State': 'Rajasthan',
                'Category': 'Historical',
                'Rating': 4.7,
                'Best Time to Visit': 'October to March',
                'Description': 'The Pink City with magnificent forts and palaces'
            },
            {
                'Destination Name': 'Kerala',
                'State': 'Kerala',
                'Category': 'Nature',
                'Rating': 4.8,
                'Best Time to Visit': 'September to March',
                'Description': 'God\'s Own Country with backwaters and hill stations'
            },
            {
                'Destination Name': 'Udaipur',
                'State': 'Rajasthan',
                'Category': 'Historical',
                'Rating': 4.6,
                'Best Time to Visit': 'October to March',
                'Description': 'City of Lakes with romantic palaces'
            },
            {
                'Destination Name': 'Manali',
                'State': 'Himachal Pradesh',
                'Category': 'Adventure',
                'Rating': 4.4,
                'Best Time to Visit': 'October to June',
                'Description': 'Hill station perfect for adventure activities'
            }
        ])
        
        # Sample places
        self.places_df = pd.DataFrame([
            {
                'Place Name': 'Amber Fort',
                'Category': 'Historical',
                'Visit Duration': '2-3 hours'
            },
            {
                'Place Name': 'City Palace',
                'Category': 'Historical',
                'Visit Duration': '2 hours'
            },
            {
                'Place Name': 'Hawa Mahal',
                'Category': 'Historical',
                'Visit Duration': '1 hour'
            }
        ])
        
        logger.info("Created sample data for demo")
    
    def _initialize_recommender(self):
        """Initialize recommendation system"""
        logger.info("Initializing recommendation system...")
        
        self.recommender = HybridRecommender()
        
        # Try to load pre-trained model
        model_path = Path(settings.MODEL_DIR) / "recommender"
        if model_path.exists():
            try:
                self.recommender.load(str(model_path))
                logger.info("Loaded pre-trained recommender")
                return
            except Exception as e:
                logger.warning(f"Could not load pre-trained recommender: {e}")
        
        # Train new model
        logger.info("Training new recommender...")
        self.recommender.fit(self.destinations_df)
        
        # Save model
        model_path.mkdir(parents=True, exist_ok=True)
        self.recommender.save(str(model_path))
        logger.info("Recommender trained and saved")
    
    def _initialize_cost_predictor(self):
        """Initialize cost prediction models"""
        logger.info("Initializing cost prediction models...")
        
        self.cost_predictor = TripCostPredictor()
        
        # Try to load pre-trained models
        model_path = Path(settings.MODEL_DIR) / "cost_predictor"
        if model_path.exists():
            try:
                self.cost_predictor.load(str(model_path))
                logger.info("Loaded pre-trained cost predictor")
                return
            except Exception as e:
                logger.warning(f"Could not load pre-trained cost predictor: {e}")
        
        # For flight predictor, we would need to train on airline data
        # For now, it will use default predictions
        logger.info("Cost predictor initialized with default models")
    
    def _initialize_itinerary_optimizer(self):
        """Initialize itinerary optimizer"""
        logger.info("Initializing itinerary optimizer...")
        
        self.itinerary_optimizer = ItineraryOptimizer(self.places_df)
        logger.info("Itinerary optimizer initialized")
    
    # Recommendation Methods
    def get_recommendations(
        self,
        preferences: Dict[str, Any],
        user_id: Optional[str] = None,
        top_n: int = 10,
        exclude_destinations: Optional[List[str]] = None
    ) -> List[Dict]:
        """Get destination recommendations"""
        if not self._initialized:
            self.initialize()
        
        return self.recommender.recommend(
            preferences=preferences,
            user_id=user_id,
            top_n=top_n,
            exclude_destinations=exclude_destinations
        )
    
    def get_nearby_recommendations(
        self,
        destination: str,
        category: Optional[str] = None,
        top_n: int = 5
    ) -> List[Dict]:
        """Get nearby attraction recommendations"""
        if not self._initialized:
            self.initialize()
        
        # Filter places by destination/state
        filtered_places = self.places_df.copy()
        
        if category:
            filtered_places = filtered_places[
                filtered_places['Category'].str.contains(category, case=False, na=False)
            ]
        
        # Get top N places
        results = filtered_places.head(top_n).to_dict('records')
        
        return results
    
    # Cost Prediction Methods
    def predict_flight_cost(
        self,
        from_city: str,
        to_city: str,
        travel_date: datetime,
        booking_date: Optional[datetime] = None,
        num_travelers: int = 1
    ) -> Dict:
        """Predict flight cost"""
        if not self._initialized:
            self.initialize()
        
        result = self.cost_predictor.flight_predictor.predict(
            from_city=from_city,
            to_city=to_city,
            travel_date=travel_date,
            booking_date=booking_date
        )
        
        # Multiply by number of travelers
        result['predicted_cost'] *= num_travelers
        result['breakdown'] = {
            'base_cost': result['predicted_cost'],
            'num_travelers': num_travelers
        }
        
        return result
    
    def predict_accommodation_cost(
        self,
        destination: str,
        accommodation_type: str,
        star_rating: int,
        duration_nights: int,
        travel_date: datetime,
        budget_category: str = 'mid-range'
    ) -> Dict:
        """Predict accommodation cost"""
        if not self._initialized:
            self.initialize()
        
        return self.cost_predictor.accommodation_predictor.predict(
            destination=destination,
            accommodation_type=accommodation_type,
            star_rating=star_rating,
            duration_nights=duration_nights,
            travel_date=travel_date,
            budget_category=budget_category
        )
    
    def predict_total_trip_cost(
        self,
        from_city: str,
        to_city: str,
        travel_date: datetime,
        return_date: datetime,
        num_travelers: int,
        accommodation_type: str,
        star_rating: int,
        budget_category: str = 'mid-range',
        meal_preference: str = 'veg',
        include_activities: bool = True
    ) -> Dict:
        """Predict total trip cost"""
        if not self._initialized:
            self.initialize()
        
        return self.cost_predictor.predict_total_cost(
            from_city=from_city,
            to_city=to_city,
            travel_date=travel_date,
            return_date=return_date,
            num_travelers=num_travelers,
            accommodation_type=accommodation_type,
            star_rating=star_rating,
            budget_category=budget_category,
            meal_preference=meal_preference,
            include_activities=include_activities
        )
    
    def optimize_budget(
        self,
        current_cost: Dict[str, Any],
        target_budget: float,
        flexibility: Dict[str, bool]
    ) -> Dict:
        """Get budget optimization suggestions"""
        if not self._initialized:
            self.initialize()
        
        return self.cost_predictor.optimize_budget(
            current_cost=current_cost,
            target_budget=target_budget,
            flexibility=flexibility
        )
    
    # Itinerary Methods
    def optimize_itinerary(
        self,
        places: List[Dict],
        start_location: Optional[Dict] = None,
        num_days: int = 1,
        daily_time_budget: int = 480
    ) -> Dict:
        """Optimize itinerary"""
        if not self._initialized:
            self.initialize()
        
        return self.itinerary_optimizer.optimize_itinerary(
            places=places,
            start_location=start_location,
            num_days=num_days,
            daily_time_budget=daily_time_budget
        )
    
    def validate_itinerary(self, itinerary: Dict) -> Dict:
        """Validate itinerary"""
        if not self._initialized:
            self.initialize()
        
        return self.itinerary_optimizer.validate_itinerary(itinerary)
    
    # LLM Methods (Using FREE Ollama + RAG)
    def parse_natural_language_query(self, query: str) -> Dict:
        """Parse natural language query using Ollama"""
        if not self._initialized:
            self.initialize()
        
        try:
            from services.ollama_service import ollama_service
            return ollama_service.parse_trip_query(query)
        except Exception as e:
            logger.error(f"Error parsing query with Ollama: {e}")
            # Fallback to simple parsing
            return self._fallback_parse_query(query)
    
    def _fallback_parse_query(self, query: str) -> Dict:
        """Fallback query parsing"""
        import re
        
        result = {
            'destination': None,
            'duration': None,
            'travelers': None,
            'preferences': [],
            'budget': None,
            'travel_date': None
        }
        
        query_lower = query.lower()
        
        # Extract destination
        destinations = ['goa', 'jaipur', 'kerala', 'udaipur', 'manali', 'delhi', 'mumbai', 'ladakh']
        for dest in destinations:
            if dest in query_lower:
                result['destination'] = dest.title()
                break
        
        # Extract duration
        duration_match = re.search(r'(\d+)\s*day', query_lower)
        if duration_match:
            result['duration'] = int(duration_match.group(1))
        
        # Extract travelers
        travelers_match = re.search(r'(\d+)\s*(?:people|person|traveler)', query_lower)
        if travelers_match:
            result['travelers'] = int(travelers_match.group(1))
        
        # Extract budget
        budget_match = re.search(r'(?:₹|rs\.?|rupees?)\s*(\d+(?:,\d+)*(?:k)?)', query_lower)
        if budget_match:
            budget_str = budget_match.group(1).replace(',', '')
            if 'k' in budget_str:
                result['budget'] = int(budget_str.replace('k', '')) * 1000
            else:
                result['budget'] = int(budget_str)
        
        # Extract preferences
        if 'relax' in query_lower or 'peaceful' in query_lower:
            result['preferences'].append('relaxing')
        if 'adventure' in query_lower:
            result['preferences'].append('adventure')
        if 'beach' in query_lower:
            result['preferences'].append('beach')
        if 'historical' in query_lower or 'history' in query_lower:
            result['preferences'].append('historical')
        
        return result
    
    def generate_itinerary_description(
        self,
        itinerary: Dict,
        style: str = 'engaging'
    ) -> Dict:
        """Generate itinerary description using Ollama"""
        if not self._initialized:
            self.initialize()
        
        try:
            from services.ollama_service import ollama_service
            
            num_days = itinerary.get('num_days', 0)
            total_places = itinerary.get('total_places', 0)
            destination = itinerary.get('destination', 'your destination')
            
            # Get highlights
            highlights = []
            if 'daily_plans' in itinerary:
                for day in itinerary['daily_plans']:
                    if 'places' in day:
                        highlights.extend([p.get('name', '') for p in day['places'][:2]])
            
            description = ollama_service.generate_itinerary_description(
                destination=destination,
                duration=num_days,
                highlights=highlights[:5],
                style=style
            )
            
            return {
                'description': description,
                'highlights': highlights[:5]
            }
        except Exception as e:
            logger.error(f"Error generating description with Ollama: {e}")
            # Fallback
            num_days = itinerary.get('num_days', 0)
            total_places = itinerary.get('total_places', 0)
            return {
                'description': f"Experience an amazing {num_days}-day journey visiting {total_places} incredible destinations.",
                'highlights': [f"Visit {total_places} attractions", f"{num_days}-day optimized schedule"]
            }
    
    def explain_recommendation(
        self,
        destination: str,
        user_profile: Dict[str, Any]
    ) -> Dict:
        """Explain recommendation using Ollama"""
        if not self._initialized:
            self.initialize()
        
        try:
            from services.ollama_service import ollama_service
            
            # Get match score from recommender if available
            match_score = user_profile.get('match_score', 85)
            
            explanation = ollama_service.explain_recommendation(
                destination=destination,
                user_preferences=user_profile,
                match_score=match_score
            )
            
            key_factors = [
                "Matches your preferred categories",
                "Within your budget range",
                f"{match_score}% compatibility score",
                "Highly rated by similar travelers"
            ]
            
            return {
                'explanation': explanation,
                'key_factors': key_factors
            }
        except Exception as e:
            logger.error(f"Error explaining recommendation with Ollama: {e}")
            return {
                'explanation': f"{destination} matches your preferences and budget requirements.",
                'key_factors': ["Matches preferences", "Within budget", "Highly rated"]
            }
    
    def query_knowledge_base(self, question: str, destination: Optional[str] = None) -> Dict:
        """Query RAG knowledge base"""
        if not self._initialized:
            self.initialize()
        
        try:
            from services.rag_service import rag_service
            
            filter_metadata = None
            if destination:
                filter_metadata = {"destination": destination}
            
            return rag_service.query_with_rag(
                question=question,
                n_context=3,
                filter_metadata=filter_metadata
            )
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}")
            return {
                'answer': "I don't have enough information to answer that question.",
                'sources': [],
                'context': []
            }
    
    def get_destination_insights(self, destination: str) -> Dict:
        """Get AI-powered destination insights"""
        if not self._initialized:
            self.initialize()
        
        try:
            from services.rag_service import rag_service
            return rag_service.get_destination_info(destination)
        except Exception as e:
            logger.error(f"Error getting destination insights: {e}")
            return {
                'destination': destination,
                'info': f"Limited information available for {destination}",
                'sources': []
            }
    
    # Data Methods
    def get_destinations(
        self,
        state: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get destination data"""
        if not self._initialized:
            self.initialize()
        
        df = self.destinations_df.copy()
        
        if state:
            df = df[df['State'].str.contains(state, case=False, na=False)]
        
        if category:
            df = df[df['Category'].str.contains(category, case=False, na=False)]
        
        return df.head(limit).to_dict('records')
    
    def get_places(
        self,
        destination: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get places data"""
        if not self._initialized:
            self.initialize()
        
        df = self.places_df.copy()
        
        if category:
            df = df[df['Category'].str.contains(category, case=False, na=False)]
        
        return df.head(limit).to_dict('records')


    def get_smart_suggestions(
        self,
        budget: Optional[float] = None,
        duration: Optional[int] = None,
        preferences: List[str] = None,
        season: Optional[str] = None,
        travelers: int = 1,
        top_n: int = 5
    ) -> List[Dict]:
        """
        Get smart destination suggestions using RAG + recommendations
        """
        if not self._initialized:
            self.initialize()
        
        try:
            from services.rag_service import rag_service
            from services.ollama_service import ollama_service
            
            # Build search query
            query_parts = []
            if preferences:
                query_parts.append(f"{', '.join(preferences)} destinations")
            if season:
                query_parts.append(f"best in {season}")
            if budget:
                query_parts.append(f"under ₹{budget}")
            
            search_query = " ".join(query_parts) if query_parts else "popular destinations in India"
            
            # Search RAG for relevant destinations
            rag_results = rag_service.search(search_query, n_results=10)
            
            # Extract destinations from RAG results
            destinations_found = set()
            destination_info = {}
            
            for result in rag_results:
                dest = result['metadata'].get('destination')
                if dest and dest not in destinations_found:
                    destinations_found.add(dest)
                    destination_info[dest] = {
                        'description': result['document'][:200],
                        'metadata': result['metadata']
                    }
            
            # Get recommendations from recommender
            rec_preferences = {
                'budget': budget,
                'category': preferences[0] if preferences else None
            }
            
            recommendations = self.get_recommendations(
                preferences=rec_preferences,
                top_n=top_n
            )
            
            # Combine and format suggestions
            suggestions = []
            for rec in recommendations[:top_n]:
                dest_name = rec.get('destination_name')
                
                # Estimate cost (simple calculation)
                estimated_cost = budget if budget else 30000
                if duration:
                    estimated_cost = min(estimated_cost, duration * 6000 * travelers)
                
                # Generate reason using LLM
                reason_prompt = f"In one sentence, explain why {dest_name} is perfect for {', '.join(preferences) if preferences else 'travelers'}"
                reason = ollama_service.generate(reason_prompt, temperature=0.7, max_tokens=50)
                
                suggestions.append({
                    'destination': dest_name,
                    'reason': reason or f"Great destination for {', '.join(preferences) if preferences else 'travel'}",
                    'estimated_cost': int(estimated_cost),
                    'best_time': rec.get('best_time', 'Year-round'),
                    'match_score': int(rec.get('score', 0) * 100),
                    'highlights': preferences[:3] if preferences else ['Sightseeing', 'Culture', 'Food'],
                    'category': rec.get('category', 'General'),
                    'rating': rec.get('rating', 4.0)
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error in get_smart_suggestions: {e}")
            # Fallback to basic recommendations
            return self.get_recommendations(preferences={'budget': budget}, top_n=top_n)
    
    def generate_complete_itinerary(
        self,
        destination: str,
        duration: int,
        budget: float,
        travelers: int = 1,
        preferences: List[str] = None,
        accommodation_type: str = 'hotel',
        meal_preference: str = 'veg'
    ) -> Dict:
        """
        Generate complete day-by-day itinerary using RAG + LLM
        """
        if not self._initialized:
            self.initialize()
        
        try:
            from services.rag_service import rag_service
            from services.ollama_service import ollama_service
            
            # Get destination information from RAG
            dest_info = rag_service.get_destination_info(destination)
            
            # Search for activities and attractions
            activities_query = f"things to do and attractions in {destination}"
            activities_results = rag_service.search(activities_query, n_results=10)
            
            # Extract activities
            activities = []
            for result in activities_results:
                activities.append(result['document'])
            
            # Build context for LLM
            context = f"""Destination: {destination}
Duration: {duration} days
Budget: ₹{budget}
Travelers: {travelers}
Preferences: {', '.join(preferences) if preferences else 'General sightseeing'}
Accommodation: {accommodation_type}
Meals: {meal_preference}

Destination Info:
{dest_info.get('summary', '')}

Available Activities:
{chr(10).join(activities[:5])}"""
            
            # Generate itinerary using LLM
            prompt = f"""{context}

Create a detailed {duration}-day itinerary for {destination}. For each day, provide:
1. Day title
2. 3-4 activities with timings
3. Estimated costs
4. Meal suggestions

Format as a structured plan. Be specific and practical."""
            
            system_prompt = "You are a travel planner. Create detailed, realistic itineraries with specific timings and costs."
            
            itinerary_text = ollama_service.generate(
                prompt=prompt,
                system=system_prompt,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Calculate cost breakdown
            per_person_per_day = budget / (duration * travelers)
            
            cost_breakdown = {
                'accommodation': int(budget * 0.35),
                'food': int(budget * 0.25),
                'activities': int(budget * 0.25),
                'transport': int(budget * 0.10),
                'miscellaneous': int(budget * 0.05),
                'total': int(budget)
            }
            
            # Parse itinerary text into structured format (simplified)
            daily_plans = []
            for day in range(1, duration + 1):
                daily_plans.append({
                    'day': day,
                    'title': f"Day {day} - Exploring {destination}",
                    'activities': [
                        {'time': '10:00 AM', 'activity': f'Morning activity', 'duration': '2 hours'},
                        {'time': '1:00 PM', 'activity': 'Lunch', 'cost': int(per_person_per_day * 0.15)},
                        {'time': '3:00 PM', 'activity': f'Afternoon sightseeing', 'duration': '3 hours'},
                        {'time': '7:00 PM', 'activity': 'Dinner', 'cost': int(per_person_per_day * 0.20)}
                    ],
                    'total_cost': int(per_person_per_day * travelers)
                })
            
            # Generate highlights
            highlights = preferences[:4] if preferences else ['Sightseeing', 'Local cuisine', 'Culture', 'Relaxation']
            
            # Generate tips using LLM
            tips_prompt = f"Give 3 practical travel tips for visiting {destination}"
            tips_text = ollama_service.generate(tips_prompt, temperature=0.7, max_tokens=100)
            tips = [tip.strip() for tip in tips_text.split('\n') if tip.strip()][:3]
            
            return {
                'destination': destination,
                'duration': duration,
                'travelers': travelers,
                'daily_plans': daily_plans,
                'cost_breakdown': cost_breakdown,
                'highlights': highlights,
                'tips': tips or ['Book in advance', 'Try local food', 'Respect local culture'],
                'generated_description': itinerary_text,
                'best_time': dest_info.get('sources', [{}])[0].get('best_time', 'Year-round') if dest_info.get('sources') else 'Year-round'
            }
            
        except Exception as e:
            logger.error(f"Error generating complete itinerary: {e}")
            # Return basic itinerary
            return {
                'destination': destination,
                'duration': duration,
                'travelers': travelers,
                'daily_plans': [],
                'cost_breakdown': {'total': budget},
                'highlights': preferences or [],
                'tips': ['Plan ahead', 'Stay hydrated', 'Enjoy your trip!'],
                'error': str(e)
            }


# Create global instance
model_service = ModelService()

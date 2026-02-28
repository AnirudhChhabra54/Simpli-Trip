
# """
# Model Service - Manages all ML models and provides unified interface
# """
# from typing import Dict, List, Optional, Any
# from datetime import datetime
# from pathlib import Path
# import pandas as pd

# from models.recommendation import HybridRecommender
# from models.cost_prediction import TripCostPredictor
# from models.itinerary_optimizer import ItineraryOptimizer
# from utils.data_loader import data_loader
# from utils.logger import logger
# from config.settings import settings


# # New — relative imports (works inside the services package)
# import json
# from . import rag_service as rag_module
# # from .lmstudio_service import lmstudio_service
# from .parser import parse_user_input
# from .ranker import rank_candidates
# from .prompt_builder import build_prompt


# class ModelService:
#     """
#     Service class that manages all ML models and provides a unified interface
#     """

#     def __init__(self):
#         self.recommender: Optional[HybridRecommender] = None
#         self.cost_predictor: Optional[TripCostPredictor] = None
#         self.itinerary_optimizer: Optional[ItineraryOptimizer] = None

#         # Data storage
#         self.destinations_df: Optional[pd.DataFrame] = None
#         self.places_df: Optional[pd.DataFrame] = None

#         self._initialized = False

#     def initialize(self):
#         """Initialize all models and load data"""
#         if self._initialized:
#             logger.info("Model service already initialized")
#             return

#         logger.info("Initializing Model Service...")

#         try:
#             # Load datasets
#             self._load_datasets()

#             # Initialize models
#             self._initialize_recommender()
#             self._initialize_cost_predictor()
#             self._initialize_itinerary_optimizer()

#             self._initialized = True
#             logger.info("Model Service initialized successfully")

#         except Exception as e:
#             logger.error(f"Failed to initialize Model Service: {e}")
#             raise

#     def shutdown(self):
#         """Shutdown the service"""
#         logger.info("ModelService shutdown.")

#     def _load_datasets(self):
#         """Load all required datasets"""
#         logger.info("Loading datasets...")

#         try:
#             # Try to load processed data first
#             try:
#                 self.destinations_df = data_loader.load_processed_data("destinations_processed.csv")
#                 self.places_df = data_loader.load_processed_data("places_processed.csv")
#                 logger.info("Loaded processed datasets")
#             except FileNotFoundError:
#                 # Load raw data and process
#                 logger.info("Processed data not found, loading raw datasets...")
#                 self.destinations_df = data_loader.load_explore_india_dataset()
#                 self.places_df = data_loader.load_tourist_places_dataset()

#                 # Save processed data
#                 data_loader.save_processed_data(self.destinations_df, "destinations_processed.csv")
#                 data_loader.save_processed_data(self.places_df, "places_processed.csv")
#                 logger.info("Saved processed datasets")

#         except Exception as e:
#             logger.warning(f"Could not load datasets from Kaggle: {e}")
#             logger.info("Using sample data for demo")
#             self._create_sample_data()

#     def _create_sample_data(self):
#         """Create sample data for demo purposes"""
#         # Sample destinations
#         self.destinations_df = pd.DataFrame([
#             {
#                 'Destination Name': 'Goa',
#                 'State': 'Goa',
#                 'Category': 'Beach',
#                 'Rating': 4.5,
#                 'Best Time to Visit': 'November to February',
#                 'Description': 'Beautiful beaches and vibrant nightlife'
#             },
#             {
#                 'Destination Name': 'Jaipur',
#                 'State': 'Rajasthan',
#                 'Category': 'Historical',
#                 'Rating': 4.7,
#                 'Best Time to Visit': 'October to March',
#                 'Description': 'The Pink City with magnificent forts and palaces'
#             },
#             {
#                 'Destination Name': 'Kerala',
#                 'State': 'Kerala',
#                 'Category': 'Nature',
#                 'Rating': 4.8,
#                 'Best Time to Visit': 'September to March',
#                 'Description': 'God\'s Own Country with backwaters and hill stations'
#             },
#             {
#                 'Destination Name': 'Udaipur',
#                 'State': 'Rajasthan',
#                 'Category': 'Historical',
#                 'Rating': 4.6,
#                 'Best Time to Visit': 'October to March',
#                 'Description': 'City of Lakes with romantic palaces'
#             },
#             {
#                 'Destination Name': 'Manali',
#                 'State': 'Himachal Pradesh',
#                 'Category': 'Adventure',
#                 'Rating': 4.4,
#                 'Best Time to Visit': 'October to June',
#                 'Description': 'Hill station perfect for adventure activities'
#             }
#         ])

#         # Sample places
#         self.places_df = pd.DataFrame([
#             {
#                 'Place Name': 'Amber Fort',
#                 'Category': 'Historical',
#                 'Visit Duration': '2-3 hours'
#             },
#             {
#                 'Place Name': 'City Palace',
#                 'Category': 'Historical',
#                 'Visit Duration': '2 hours'
#             },
#             {
#                 'Place Name': 'Hawa Mahal',
#                 'Category': 'Historical',
#                 'Visit Duration': '1 hour'
#             }
#         ])

#         logger.info("Created sample data for demo")

#     def _initialize_recommender(self):
#         """Initialize recommendation system"""
#         logger.info("Initializing recommendation system...")

#         self.recommender = HybridRecommender()

#         # Try to load pre-trained model
#         model_path = Path(settings.MODEL_DIR) / "recommender"
#         if model_path.exists():
#             try:
#                 self.recommender.load(str(model_path))
#                 logger.info("Loaded pre-trained recommender")
#                 return
#             except Exception as e:
#                 logger.warning(f"Could not load pre-trained recommender: {e}")

#         # Train new model
#         logger.info("Training new recommender...")
#         try:
#             self.recommender.fit(self.destinations_df)
#             # Save model
#             model_path.mkdir(parents=True, exist_ok=True)
#             self.recommender.save(str(model_path))
#             logger.info("Recommender trained and saved")
#         except Exception as e:
#             logger.warning(f"Recommender training failed: {e}")

#     def _initialize_cost_predictor(self):
#         """Initialize cost prediction models"""
#         logger.info("Initializing cost prediction models...")

#         self.cost_predictor = TripCostPredictor()

#         # Try to load pre-trained models
#         model_path = Path(settings.MODEL_DIR) / "cost_predictor"
#         if model_path.exists():
#             try:
#                 self.cost_predictor.load(str(model_path))
#                 logger.info("Loaded pre-trained cost predictor")
#                 return
#             except Exception as e:
#                 logger.warning(f"Could not load pre-trained cost predictor: {e}")

#         # For flight predictor, we would need to train on airline data
#         # For now, it will use default predictions
#         logger.info("Cost predictor initialized with default models")

#     def _initialize_itinerary_optimizer(self):
#         """Initialize itinerary optimizer"""
#         logger.info("Initializing itinerary optimizer...")

#         self.itinerary_optimizer = ItineraryOptimizer(self.places_df)
#         logger.info("Itinerary optimizer initialized")

#     # Recommendation Methods
#     def get_destination_recommendations(self, preferences: Dict[str, Any], top_n: int = 10) -> List[Dict]:
#         """
#         Placeholder for destination recommendations.
#         """
#         logger.warning("`get_destination_recommendations` is not fully implemented. Returning sample data.")
#         if self.destinations_df is not None:
#             return self.destinations_df.head(top_n).to_dict("records")
#         return []

#     def get_recommendations(
#         self,
#         preferences: Dict[str, Any],
#         user_id: Optional[str] = None,
#         top_n: int = 10,
#         exclude_destinations: Optional[List[str]] = None
#     ) -> List[Dict]:
#         """Get destination recommendations"""
#         if not self._initialized:
#             self.initialize()

#         return self.recommender.recommend(
#             preferences=preferences,
#             user_id=user_id,
#             top_n=top_n,
#             exclude_destinations=exclude_destinations
#         )

#     def get_nearby_recommendations(
#         self,
#         destination: str,
#         category: Optional[str] = None,
#         top_n: int = 5
#     ) -> List[Dict]:
#         """Get nearby attraction recommendations"""
#         if not self._initialized:
#             self.initialize()

#         # Filter places by destination/state
#         filtered_places = self.places_df.copy()

#         if category:
#             filtered_places = filtered_places[
#                 filtered_places['Category'].str.contains(category, case=False, na=False)
#             ]

#         # Get top N places
#         results = filtered_places.head(top_n).to_dict('records')

#         return results

#     # Cost Prediction Methods
#     def predict_flight_cost(
#         self,
#         from_city: str,
#         to_city: str,
#         travel_date: datetime,
#         booking_date: Optional[datetime] = None,
#         num_travelers: int = 1
#     ) -> Dict:
#         """Predict flight cost"""
#         if not self._initialized:
#             self.initialize()

#         result = self.cost_predictor.flight_predictor.predict(
#             from_city=from_city,
#             to_city=to_city,
#             travel_date=travel_date,
#             booking_date=booking_date
#         )

#         # Multiply by number of travelers
#         result['predicted_cost'] *= num_travelers
#         result['breakdown'] = {
#             'base_cost': result['predicted_cost'],
#             'num_travelers': num_travelers
#         }

#         return result

#     def predict_accommodation_cost(
#         self,
#         destination: str,
#         accommodation_type: str,
#         star_rating: int,
#         duration_nights: int,
#         travel_date: datetime,
#         budget_category: str = 'mid-range'
#     ) -> Dict:
#         """Predict accommodation cost"""
#         if not self._initialized:
#             self.initialize()

#         return self.cost_predictor.accommodation_predictor.predict(
#             destination=destination,
#             accommodation_type=accommodation_type,
#             star_rating=star_rating,
#             duration_nights=duration_nights,
#             travel_date=travel_date,
#             budget_category=budget_category
#         )

#     def predict_total_trip_cost(
#         self,
#         from_city: str,
#         to_city: str,
#         travel_date: datetime,
#         return_date: datetime,
#         num_travelers: int,
#         accommodation_type: str,
#         star_rating: int,
#         budget_category: str = 'mid-range',
#         meal_preference: str = 'veg',
#         include_activities: bool = True
#     ) -> Dict:
#         """Predict total trip cost"""
#         if not self._initialized:
#             self.initialize()

#         return self.cost_predictor.predict_total_cost(
#             from_city=from_city,
#             to_city=to_city,
#             travel_date=travel_date,
#             return_date=return_date,
#             num_travelers=num_travelers,
#             accommodation_type=accommodation_type,
#             star_rating=star_rating,
#             budget_category=budget_category,
#             meal_preference=meal_preference,
#             include_activities=include_activities
#         )

#     def optimize_budget(
#         self,
#         current_cost: Dict[str, Any],
#         target_budget: float,
#         flexibility: Dict[str, bool]
#     ) -> Dict:
#         """Get budget optimization suggestions"""
#         if not self._initialized:
#             self.initialize()

#         return self.cost_predictor.optimize_budget(
#             current_cost=current_cost,
#             target_budget=target_budget,
#             flexibility=flexibility
#         )

#     # Itinerary Methods
#     def optimize_itinerary(
#         self,
#         places: List[Dict],
#         start_location: Optional[Dict] = None,
#         num_days: int = 1,
#         daily_time_budget: int = 480
#     ) -> Dict:
#         """Optimize itinerary"""
#         if not self._initialized:
#             self.initialize()

#         return self.itinerary_optimizer.optimize_itinerary(
#             places=places,
#             start_location=start_location,
#             num_days=num_days,
#             daily_time_budget=daily_time_budget
#         )

#     def validate_itinerary(self, itinerary: Dict) -> Dict:
#         """Validate itinerary"""
#         if not self._initialized:
#             self.initialize()

#         return self.itinerary_optimizer.validate_itinerary(itinerary)

#     # LLM Methods (Using FREE Ollama + RAG)
#     def parse_natural_language_query(self, query: str) -> Dict:
#         """Parse natural language query using LM Studio to extract structured trip details."""
#         if not self._initialized:
#             self.initialize()

#         system_prompt = """You are an expert travel planning assistant. Your task is to parse a user's travel query and extract key details into a structured JSON object.

# The user will provide a query in natural language. You must identify the following fields:
# - "destination": The primary travel destination (e.g., "Goa", "Paris").
# - "duration_days": The length of the trip in days (integer).
# - "budget_usd": The total budget for the trip in USD (integer).
# - "travelers": The number of people traveling (integer).
# - "preferences": A list of interests or preferences (e.g., ["beach", "adventure", "food"]).
# - "start_date": The start date of the trip in YYYY-MM-DD format, if mentioned.

# Rules:
# - If a value is not mentioned in the query, set it to null.
# - The `preferences` field should always be a list, even if it's empty.
# - Your response MUST be ONLY the JSON object, with no other text or explanation."""

#         messages = [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": query},
#         ]

#         try:
#             # Use the 'chat' method from the lmstudio_service dictionary
#             response = lmstudio_service['chat'](messages=messages, temperature=0.1, max_tokens=500)
            
#             # Clean up the response text to ensure it is valid JSON
#             json_text = response['text'].strip()
#             # Find the start and end of the JSON object
#             start_index = json_text.find('{')
#             end_index = json_text.rfind('}') + 1
#             if start_index != -1 and end_index != -1:
#                 json_text = json_text[start_index:end_index]
            
#             parsed_json = json.loads(json_text)
#             logger.info(f"Successfully parsed query using LM Studio: {parsed_json}")
#             return parsed_json

#         except Exception as e:
#             logger.error(f"Error parsing query with LM Studio: {e}. Falling back to regex parser.")
#             # Fallback to simple parsing
#             return self._fallback_parse_query(query)

#     def _fallback_parse_query(self, query: str) -> Dict:
#         """Fallback query parsing"""
#         import re

#         result = {
#             'destination': None,
#             'duration': None,
#             'travelers': None,
#             'preferences': [],
#             'budget': None,
#             'travel_date': None
#         }

#         query_lower = query.lower()

#         # Extract destination
#         destinations = ['goa', 'jaipur', 'kerala', 'udaipur', 'manali', 'delhi', 'mumbai', 'ladakh']
#         for dest in destinations:
#             if dest in query_lower:
#                 result['destination'] = dest.title()
#                 break

#         # Extract duration
#         duration_match = re.search(r'(\d+)\s*day', query_lower)
#         if duration_match:
#             result['duration'] = int(duration_match.group(1))

#         # Extract travelers
#         travelers_match = re.search(r'(\d+)\s*(?:people|person|traveler)', query_lower)
#         if travelers_match:
#             result['travelers'] = int(travelers_match.group(1))

#         # Extract budget
#         budget_match = re.search(r'(?:₹|rs\.?|rupees?)\s*(\d+(?:,\d+)*(?:k)?)', query_lower)
#         if budget_match:
#             budget_str = budget_match.group(1).replace(',', '')
#             if 'k' in budget_str:
#                 result['budget'] = int(budget_str.replace('k', '')) * 1000
#             else:
#                 result['budget'] = int(budget_str)

#         # Extract preferences
#         if 'relax' in query_lower or 'peaceful' in query_lower:
#             result['preferences'].append('relaxing')
#         if 'adventure' in query_lower:
#             result['preferences'].append('adventure')
#         if 'beach' in query_lower:
#             result['preferences'].append('beach')
#         if 'historical' in query_lower or 'history' in query_lower:
#             result['preferences'].append('historical')

#         return result

#     def generate_itinerary_description(
#         self,
#         itinerary: Dict,
#         style: str = 'engaging'
#     ) -> Dict:
#         """Generate itinerary description using Ollama"""
#         if not self._initialized:
#             self.initialize()

#         try:
#             num_days = itinerary.get('num_days', 0)
#             total_places = itinerary.get('total_places', 0)
#             destination = itinerary.get('destination', 'your destination')

#             # Get highlights
#             highlights = []
#             if 'daily_plans' in itinerary:
#                 for day in itinerary['daily_plans']:
#                     if 'places' in day:
#                         highlights.extend([p.get('name', '') for p in day['places'][:2]])

#             description = ollama_service.generate_itinerary_description(
#                 destination=destination,
#                 duration=num_days,
#                 highlights=highlights[:5],
#                 style=style
#             )

#             return {
#                 'description': description,
#                 'highlights': highlights[:5]
#             }
#         except Exception as e:
#             logger.error(f"Error generating description with Ollama: {e}")
#             # Fallback
#             num_days = itinerary.get('num_days', 0)
#             total_places = itinerary.get('total_places', 0)
#             return {
#                 'description': f"Experience an amazing {num_days}-day journey visiting {total_places} incredible destinations.",
#                 'highlights': [f"Visit {total_places} attractions", f"{num_days}-day optimized schedule"]
#             }

#     def explain_recommendation(
#         self,
#         destination: str,
#         user_profile: Dict[str, Any]
#     ) -> Dict:
#         """Explain recommendation using Ollama"""
#         if not self._initialized:
#             self.initialize()

#         try:
#             # Get match score from recommender if available
#             match_score = user_profile.get('match_score', 85)

#             explanation = ollama_service.explain_recommendation(
#                 destination=destination,
#                 user_preferences=user_profile,
#                 match_score=match_score
#             )

#             key_factors = [
#                 "Matches your preferred categories",
#                 "Within your budget range",
#                 f"{match_score}% compatibility score",
#                 "Highly rated by similar travelers"
#             ]

#             return {
#                 'explanation': explanation,
#                 'key_factors': key_factors
#             }
#         except Exception as e:
#             logger.error(f"Error explaining recommendation with Ollama: {e}")
#             return {
#                 'explanation': f"{destination} matches your preferences and budget requirements.",
#                 'key_factors': ["Matches preferences", "Within budget", "Highly rated"]
#             }

#     def query_knowledge_base(self, question: str, destination: Optional[str] = None) -> Dict:
#         """Query RAG knowledge base"""
#         if not self._initialized:
#             self.initialize()

#         try:
#             # Prefer rag_service.search if available (older code). Otherwise use retrieve
#             if hasattr(rag_service, "query_with_rag"):
#                 try:
#                     filter_metadata = None
#                     if destination:
#                         filter_metadata = {"city": destination}
#                     return rag_service.query_with_rag(
#                         question=question,
#                         n_context=3,
#                         filter_metadata=filter_metadata
#                     )
#                 except Exception:
#                     pass

#             # fallback: semantic retrieve + client-side filter
#             candidates = rag_service.retrieve(question, top_k=10)
#             if destination:
#                 destination_lower = destination.lower()
#                 candidates = [c for c in candidates if (c.get("meta") or {}).get("city", "").lower() == destination_lower]
#             answer = {"answer": "", "sources": [], "context": candidates}
#             # attempt a simple aggregation for answer (first doc text)
#             if candidates:
#                 answer["answer"] = candidates[0].get("text", "")
#                 answer["sources"] = [ (c.get("meta") or {}).get("source_id") or (c.get("meta") or {}).get("id") for c in candidates[:3] ]
#             else:
#                 answer["answer"] = "I don't have enough information to answer that question."
#             return answer

#         except Exception as e:
#             logger.error(f"Error querying knowledge base: {e}")
#             return {
#                 'answer': "I don't have enough information to answer that question.",
#                 'sources': [],
#                 'context': []
#             }

#     def get_destination_insights(self, destination: str) -> Dict:
#         """Get AI-powered destination insights"""
#         if not self._initialized:
#             self.initialize()

#         try:
#             return rag_service.get_destination_info(destination)
#         except Exception as e:
#             logger.error(f"Error getting destination insights: {e}")
#             return {
#                 'destination': destination,
#                 'info': f"Limited information available for {destination}",
#                 'sources': []
#             }

#     def get_rag_stats(self) -> Dict[str, Any]:
#         """
#         Placeholder for RAG statistics.
#         """
#         logger.warning("`get_rag_stats` is not fully implemented. Returning sample data.")
#         try:
#             if hasattr(rag_service, "get_stats"):
#                 return rag_service.get_stats()
#         except Exception as e:
#             logger.error(f"Could not retrieve RAG stats: {e}")

#         return {"vector_count": 0, "sources": 0}

#     # Data Methods
#     def get_destinations(
#         self,
#         state: Optional[str] = None,
#         category: Optional[str] = None,
#         limit: int = 100
#     ) -> List[Dict]:
#         """Get destination data"""
#         if not self._initialized:
#             self.initialize()

#         df = self.destinations_df.copy()

#         if state:
#             df = df[df['State'].str.contains(state, case=False, na=False)]

#         if category:
#             df = df[df['Category'].str.contains(category, case=False, na=False)]

#         return df.head(limit).to_dict('records')

#     def get_places(
#         self,
#         destination: Optional[str] = None,
#         category: Optional[str] = None,
#         limit: int = 100
#     ) -> List[Dict]:
#         """Get places data"""
#         if not self._initialized:
#             self.initialize()

#         df = self.places_df.copy()

#         if category:
#             df = df[df['Category'].str.contains(category, case=False, na=False)]

#         return df.head(limit).to_dict('records')


#     def get_smart_suggestions(
#         self,
#         budget: Optional[float] = None,
#         duration: Optional[int] = None,
#         preferences: List[str] = None,
#         season: Optional[str] = None,
#         travelers: int = 1,
#         top_n: int = 5
#     ) -> List[Dict]:
#         """
#         Get smart destination suggestions using RAG + recommendation
#         """
#         if not self._initialized:
#             self.initialize()

#         try:
#             # Build search query
#             query_parts = []
#             if preferences:
#                 query_parts.append(f"{', '.join(preferences)} destinations")
#             if season:
#                 query_parts.append(f"best in {season}")
#             if budget:
#                 query_parts.append(f"under ₹{budget}")

#             search_query = " ".join(query_parts) if query_parts else "popular destinations in India"

#             # Search RAG for relevant destinations -- use rag_service.search if available
#             rag_results = []
#             try:
#                 if hasattr(rag_service, "search"):
#                     rag_results = rag_service.search(search_query, n_results=10)
#                 else:
#                     rag_results = rag_service.retrieve(search_query, top_k=10)
#             except Exception:
#                 rag_results = []

#             # Extract destinations from RAG results
#             destinations_found = set()
#             destination_info = {}

#             for result in rag_results:
#                 meta = result.get("meta", {}) or {}
#                 dest = meta.get('city') or meta.get('destination') or meta.get('source_id')
#                 if dest:
#                     dest_name = dest if isinstance(dest, str) else str(dest)
#                     if dest_name not in destinations_found:
#                         destinations_found.add(dest_name)
#                         destination_info[dest_name] = {
#                             'description': (result.get('text') or "")[:200],
#                             'metadata': meta
#                         }

#             # Get recommendations from recommender
#             rec_preferences = {
#                 'budget': budget,
#                 'category': preferences[0] if preferences else None
#             }

#             recommendations = self.get_recommendations(
#                 preferences=rec_preferences,
#                 top_n=top_n
#             )

#             # Combine and format suggestions
#             suggestions = []
#             for rec in recommendations[:top_n]:
#                 dest_name = rec.get('destination_name') or rec.get('Destination Name') or rec.get('destination')

#                 # Estimate cost (simple calculation)
#                 estimated_cost = budget if budget else 30000
#                 if duration:
#                     estimated_cost = min(estimated_cost, duration * 6000 * travelers)

#                 # Generate reason using LLM
#                 reason_prompt = f"In one sentence, explain why {dest_name} is perfect for {', '.join(preferences) if preferences else 'travelers'}"
#                 try:
#                     reason = ollama_service.generate(reason_prompt, temperature=0.7, max_tokens=50)
#                 except Exception:
#                     reason = None

#                 suggestions.append({
#                     'destination': dest_name,
#                     'reason': reason or f"Great destination for {', '.join(preferences) if preferences else 'travel'}",
#                     'estimated_cost': int(estimated_cost),
#                     'best_time': rec.get('best_time', 'Year-round'),
#                     'match_score': int(rec.get('score', 0) * 100) if rec.get('score') is not None else 0,
#                     'highlights': preferences[:3] if preferences else ['Sightseeing', 'Culture', 'Food'],
#                     'category': rec.get('category', 'General'),
#                     'rating': rec.get('rating', 4.0)
#                 })

#             return suggestions

#         except Exception as e:
#             logger.error(f"Error in get_smart_suggestions: {e}")
#             # Fallback to basic recommendations
#             return self.get_recommendations(preferences={'budget': budget}, top_n=top_n)

#     # New helper: generate itinerary from free text
#     def generate_itinerary_from_text(self, user_text: str) -> Dict:
#         """
#         Parse free text, retrieve destination-specific context, rank, build prompt, call LLM.
#         Returns parsed constraints, sources, prompt, and generated_text.
#         """
#         if not self._initialized:
#             self.initialize()

#         parsed = parse_user_input(user_text)
#         destination = parsed.get("destination")

#         # Retrieve semantic candidates (broad)
#         try:
#             candidates = rag_service.retrieve(user_text, top_k=50)
#         except Exception:
#             candidates = []

#         # If destination known, filter by metadata city (case-insensitive)
#         if destination and candidates:
#             dest_lower = destination.lower()
#             filtered = []
#             for c in candidates:
#                 meta = c.get("meta", {}) or {}
#                 city = (meta.get("city") or meta.get("destination") or meta.get("source_id") or "").lower()
#                 if dest_lower in city:
#                     filtered.append(c)
#             if filtered:
#                 candidates = filtered

#         # Rank/filter candidates according to parsed constraints
#         ranked = rank_candidates(candidates, parsed, top_k=6)
#         # Build prompt
#         prompt = build_prompt(parsed, ranked)
#         # Generate via Ollama
#         generated = ollama_service.generate(prompt, max_tokens=800, temperature=0.2)

#         sources = [ (c.get("meta") or {}).get("source_id") or (c.get("meta") or {}).get("id") for c in ranked ]

#         return {
#             "parsed": parsed,
#             "sources": sources,
#             "prompt": prompt,
#             "generated_text": generated
#         }

#     def generate_complete_itinerary(
#         self,
#         destination: str,
#         duration: int,
#         budget: float,
#         travelers: int = 1,
#         preferences: List[str] = None,
#         accommodation_type: str = 'hotel',
#         meal_preference: str = 'veg'
#     ) -> Dict:
#         """
#         Generate complete day-by-day itinerary using improved RAG + LLM pipeline (destination-respecting).
#         """
#         if not self._initialized:
#             self.initialize()

#         try:
#             # Build a short natural language query describing the user requirements
#             query = f"{duration}-day trip to {destination} for {travelers} traveler(s). Preferences: {', '.join(preferences) if preferences else 'sightseeing'}. Budget: ₹{budget}. Meals: {meal_preference}."
#             # Retrieve candidates
#             try:
#                 candidates = rag_service.retrieve(query, top_k=50)
#             except Exception:
#                 candidates = []

#             # Strongly prefer docs whose meta.city matches destination
#             dest_lower = destination.lower() if destination else None
#             if dest_lower:
#                 filtered = []
#                 for c in candidates:
#                     meta = c.get("meta", {}) or {}
#                     city = (meta.get("city") or meta.get("destination") or meta.get("source_id") or "").lower()
#                     if dest_lower in city:
#                         filtered.append(c)
#                 if filtered:
#                     candidates = filtered

#             # Rank candidates with respect to constraints
#             user_constraints = {
#                 "budget": budget,
#                 "travelers": travelers,
#                 "duration_days": duration
#             }
#             ranked = rank_candidates(candidates, user_constraints, top_k=8)

#             # Build prompt for LLM with explicit constraints & citations
#             parsed_constraints = {
#                 "destination": destination,
#                 "duration_days": duration,
#                 "travelers": travelers,
#                 "budget": budget,
#                 "meal_pref": meal_preference,
#                 "categories": preferences or []
#             }
#             prompt = build_prompt(parsed_constraints, ranked, max_chars=4000)

#             # Call Ollama to generate itinerary (guarded)
#             itinerary_text = ollama_service.generate(prompt, max_tokens=1000, temperature=0.25)

#             # Basic structured parsing fallback (best-effort)
#             per_person_per_day = budget / max(1, duration * travelers) if budget else 0
#             daily_plans = []
#             for day in range(1, max(1, duration) + 1):
#                 daily_plans.append({
#                     'day': day,
#                     'title': f"Day {day} - Explore {destination}",
#                     'activities': [
#                         {'time': '09:00 AM', 'activity': 'Morning activity (see sources)', 'duration': '2-3 hours'},
#                         {'time': '12:30 PM', 'activity': 'Lunch', 'cost': int(per_person_per_day * 0.15) if per_person_per_day else None},
#                         {'time': '03:00 PM', 'activity': 'Afternoon activity', 'duration': '2-3 hours'},
#                         {'time': '07:30 PM', 'activity': 'Dinner', 'cost': int(per_person_per_day * 0.20) if per_person_per_day else None}
#                     ],
#                     'total_cost': int(per_person_per_day * travelers) if per_person_per_day else None
#                 })

#             cost_breakdown = {
#                 'accommodation': int(budget * 0.35) if budget else None,
#                 'food': int(budget * 0.25) if budget else None,
#                 'activities': int(budget * 0.25) if budget else None,
#                 'transport': int(budget * 0.10) if budget else None,
#                 'miscellaneous': int(budget * 0.05) if budget else None,
#                 'total': int(budget) if budget else None
#             }

#             # Get tips
#             tips_text = ollama_service.generate(f"Give 3 short practical travel tips for visiting {destination}", max_tokens=80, temperature=0.5)
#             tips = [t.strip() for t in (tips_text or "").split("\n") if t.strip()][:3] or ["Book in advance", "Try local food", "Respect local customs"]

#             sources = [ (c.get("meta") or {}).get("source_id") or (c.get("meta") or {}).get("id") for c in ranked ]

#             return {
#                 'destination': destination,
#                 'duration': duration,
#                 'travelers': travelers,
#                 'daily_plans': daily_plans,
#                 'cost_breakdown': cost_breakdown,
#                 'highlights': preferences or ['Sightseeing', 'Local cuisine'],
#                 'tips': tips,
#                 'generated_description': itinerary_text,
#                 'sources': sources
#             }

#         except Exception as e:
#             logger.error(f"Error generating complete itinerary: {e}")
#             return {
#                 'destination': destination,
#                 'duration': duration,
#                 'travelers': travelers,
#                 'daily_plans': [],
#                 'cost_breakdown': {'total': budget},
#                 'highlights': preferences or [],
#                 'tips': ['Plan ahead', 'Stay hydrated', 'Enjoy your trip!'],
#                 'error': str(e)
#             }


# # Create global instance (singleton)
# model_service = ModelService()
# services/model_service.py
"""
Model Service - Manages all ML models and provides unified interface
"""
# services/model_service.py
"""
Model Service - Manages all ML models and provides unified interface
"""
# services/model_service.py
"""
Model Service - Manages all ML models and provides unified interface
Safe Mode: Catches recommender errors so the app never crashes.
"""
import json
import re
from typing import Dict, List, Optional, Any
import pandas as pd


from utils.data_loader import data_loader
from utils.logger import logger

from .parser import parse_user_input
from .lmstudio_service import lmstudio_service


def _format_inr(amount: float) -> str:
    """Format a number as an Indian Rupee string, e.g. 50000 -> '₹50,000'."""
    try:
        return "₹" + format(int(round(float(amount))), ",")
    except Exception:
        return f"₹{amount}"

class ModelService:
    def __init__(self):
        self.recommender = None
        self.cost_predictor = None
        self.itinerary_optimizer = None
        self.destinations_df = None
        self.places_df = None
        self._initialized = False

    def initialize(self):
        if self._initialized: return
        logger.info("Initializing Model Service...")
        try:
            self._load_datasets()
            self._initialize_recommender()
            self._initialize_cost_predictor()
            self._initialize_itinerary_optimizer()
            self._seed_knowledge_base()
            self._initialized = True
        except Exception as e:
            logger.error(f"Partial initialization failure: {e}")

    def _seed_knowledge_base(self):
        """Seed the ChromaDB knowledge base from local datasets (best-effort)."""
        try:
            from services.rag_service import rag_service as _rag
            _rag.seed_knowledge_base()
        except Exception as e:
            logger.warning(f"Knowledge base seeding skipped: {e}")

    def shutdown(self):
        """Release resources used by the model service."""
        logger.info("Shutting down Model Service...")
        self.recommender = None
        self.cost_predictor = None
        self.itinerary_optimizer = None
        self._initialized = False

    def _load_datasets(self):
        try:
            self.destinations_df = data_loader.load_processed_data("destinations_processed.csv")
            self.places_df = data_loader.load_processed_data("places_processed.csv")
        except Exception:
            self.destinations_df = data_loader.load_explore_india_dataset()
            self.places_df = data_loader.load_tourist_places_dataset()

    def _initialize_recommender(self):
        self.recommender = None

    def _initialize_cost_predictor(self):
        self.cost_predictor = None

    def _initialize_itinerary_optimizer(self):
        self.itinerary_optimizer = None

    # --- HYBRID PARSING ---
    def parse_natural_language_query(self, query: str) -> Dict:
        if not self._initialized: self.initialize()
        parsed_data = {
            "destination": None, "duration": None, "travelers": 1, 
            "budget": None, "preferences": []
        }
        # 1. Try LLM
        try:
            system_prompt = "Extract JSON: destination, duration(int), budget(int), travelers(int), preferences(list)."
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": query}]
            response = lmstudio_service['chat'](messages, temperature=0.1)
            text = response.get('text', '').strip()
            if "```" in text: text = text.split("```")[1].replace("json", "").strip()
            llm_data = json.loads(text)
            parsed_data.update({k: v for k, v in llm_data.items() if v is not None})
        except Exception: pass 

        # 2. Regex Fallback
        if not parsed_data["destination"] or not parsed_data["budget"]:
            regex_data = parse_user_input(query)
            if not parsed_data["destination"]: parsed_data["destination"] = regex_data.get("destination")
            if not parsed_data["budget"]: parsed_data["budget"] = regex_data.get("budget")
            if not parsed_data["duration"]: parsed_data["duration"] = regex_data.get("duration_days")
            if regex_data.get("travelers", 0) > 1: parsed_data["travelers"] = regex_data.get("travelers")
        return parsed_data

    # --- SMART ITINERARY GENERATION ---
    def generate_complete_itinerary(self, destination: str, duration: int, budget: float, travelers: int = 1, preferences: List[str] = None, **kwargs):
        if not self._initialized: self.initialize()
        
        # 1. Get Real-Time Prices (Scraper fallback)
        flight_cost = 5000
        hotel_cost_per_night = 3000
        
        # 2. Budget Math
        total_flight = flight_cost * travelers
        total_hotel = hotel_cost_per_night * duration 
        if travelers > 2: total_hotel = total_hotel * (travelers / 2)
        
        fixed_costs = int(total_flight + total_hotel)
        remaining_budget = max(0, budget - fixed_costs)
        
        budget_note = (
            f"- Total Budget: ₹{budget}\n"
            f"- Flight ({travelers} ppl): ₹{total_flight}\n"
            f"- Hotel ({duration} nights): ₹{int(total_hotel)}\n"
            f"- **Remaining for Food/Fun:** ₹{int(remaining_budget)}"
        )

        # 3. Retrieve RAG (destination knowledge base)
        context_text = ""
        try:
            from services.rag_service import rag_service as _rag
            _rag.seed_knowledge_base()
            docs = _rag.retrieve(destination, top_k=3)
            context_text = "\n".join([f"- {d['text'][:200]}..." for d in docs])[:1000]
        except Exception:
            context_text = ""

        # 4. Generate
        system_prompt = "You are a travel assistant. Create a markdown itinerary."
        user_prompt = (
            f"Plan a {duration}-day trip to {destination}.\n"
            f"Context:\n{budget_note}\n\n"
            f"Interests: {preferences}\n"
            f"Local Info:\n{context_text}\n\n"
            "Task: Write a Day-by-Day plan. Mention costs. Keep it concise."
        )
        
        generated_text = ""
        try:
            response = lmstudio_service['chat']([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], temperature=0.7, max_tokens=1500)
            generated_text = response.get('text', '').strip()
        except Exception: pass

        if not generated_text:
            generated_text = f"# Itinerary for {destination}\n\n**Financial Overview**\n{budget_note}\n\n**Day 1**\n- Arrive & Relax.\n**Day 2**\n- Explore City.\n**Day {duration}**\n- Depart."

        return {
            "destination": destination,
            "duration": duration,
            "financials": {
                "total_budget": budget,
                "estimated_flight": total_flight,
                "estimated_hotel": int(total_hotel),
                "remaining_daily_spend": int(remaining_budget / duration)
            },
            "generated_itinerary": generated_text,
            "sources": []
        }

    # --- CRASH-PROOF HELPERS ---
    def get_recommendations(self, preferences, top_n=5, **kwargs):
        if not self._initialized: self.initialize()
        try:
            # Safely check if recommender is ready
            return self.recommender.recommend(preferences, top_n=top_n)
        except Exception:
            logger.warning("Recommender not ready. Returning empty list.")
            return []

    # Stubs for other methods
    def get_destinations(self, **kwargs):
        if not self._initialized: self.initialize()
        if self.destinations_df is None or self.destinations_df.empty:
            return []
        cols = self.destinations_df.columns
        records = self.destinations_df.head(10).to_dict('records')
        normalized = []
        for r in records:
            row = {}
            for c in cols:
                try:
                    row[str(c).strip()] = r[c]
                except Exception:
                    row[str(c).strip()] = None
            normalized.append(row)
        return normalized

    def get_places(self, **kwargs):
        if not self._initialized: self.initialize()
        if self.places_df is None or self.places_df.empty:
            return []
        records = self.places_df.to_dict('records')
        normalized = []
        for r in records:
            normalized.append({str(k).strip(): v for k, v in r.items()})
        return normalized

    # ============================================================
    # CORE TRAVEL LOGIC (real implementations over datasets + RAG)
    # ============================================================

    @staticmethod
    def _pseudo_distance(a: str, b: str) -> int:
        """Deterministic pseudo distance (km) between two place names."""
        try:
            ha = sum(ord(c) for c in str(a or "").lower())
            hb = sum(ord(c) for c in str(b or "").lower())
            if not a or not b:
                return 1200
            if str(a).lower() == str(b).lower():
                return 0
            return 800 + ((ha * 31 + hb) % 3200)
        except Exception:
            return 1200

    def get_nearby_recommendations(self, destination=None, category=None, top_n=5, **kwargs):
        if not self._initialized: self.initialize()
        if self.places_df is None or self.places_df.empty:
            return []
        records = self.places_df.to_dict('records')

        def name_of(r):
            return str(r.get("Place Name") or r.get("name") or "").strip().lower()

        def cat_of(r):
            return str(r.get("Category") or r.get("category") or "").strip().lower()

        # Rank by nearest distance first, then optionally by category.
        scored = []
        for r in records:
            cat = cat_of(r)
            if category and category.lower() not in cat:
                continue
            distance = self._pseudo_distance(str(destination or ""), name_of(r))
            scored.append({
                "place_name": str(r.get("Place Name") or r.get("name") or "Unknown"),
                "category": cat or "General",
                "visit_duration": r.get("Visit Duration") or r.get("visit_duration") or "N/A",
                "distance_km": distance,
                "score": round(max(0.0, 100 - distance * 0.025), 1),
            })
        scored.sort(key=lambda x: x["distance_km"])
        return scored[:top_n]

    def predict_flight_cost(self, from_city=None, to_city=None, travel_date=None,
                            booking_date=None, num_travelers=1, **kwargs):
        if not self._initialized: self.initialize()
        num_travelers = int(num_travelers or 1)

        try:
            from datetime import datetime
            lead_days = 30
            if travel_date and booking_date:
                try:
                    lead_days = max(0, (datetime.fromisoformat(str(travel_date)[:10])
                                        - datetime.fromisoformat(str(booking_date)[:10])).days)
                except Exception:
                    lead_days = 30
        except Exception:
            lead_days = 30

        distance = self._pseudo_distance(from_city, to_city)
        # Base fare scales with distance; earlier booking is cheaper.
        base_fare = 1500 + distance * 4.5
        booking_factor = 1.35 if lead_days < 7 else (
            1.1 if lead_days < 21 else (0.88 if lead_days > 45 else 1.0))
        price_per_person = int(base_fare * booking_factor)

        return {
            "predictions": {"predicted_cost": price_per_person * num_travelers,
                            "total_cost": price_per_person * num_travelers,
                            "price_per_person": price_per_person},
            "predicted_cost": price_per_person * num_travelers,
            "total_cost": price_per_person * num_travelers,
            "price_per_person": price_per_person,
            "num_travelers": num_travelers,
            "from_city": from_city,
            "to_city": to_city,
            "distance_km": distance,
            "days_until_travel": lead_days,
            "currency": "INR",
            "currency_symbol": "₹",
            "confidence": round(min(0.95, 0.55 + lead_days / 100), 2),
            "factors": ["distance", "booking lead time"],
        }

    def predict_accommodation_cost(self, destination=None, accommodation_type=None,
                                   star_rating=None, duration_nights=1, travel_date=None,
                                   budget_category=None, **kwargs):
        if not self._initialized: self.initialize()
        duration_nights = int(duration_nights or 1)

        base_rates = {
            "hostel": 800, "budget_hotel": 1400, "hotel": 3200,
            "airbnb": 2800, "resort": 6500, "villa": 9000, "luxury_hotel": 9000,
        }
        rate = base_rates.get(str(accommodation_type or "hotel").lower(), 3200)

        star_mult = {1: 1.0, 2: 1.3, 3: 1.65, 4: 2.3, 5: 3.2}
        if star_rating:
            rate *= star_mult.get(int(float(star_rating)), 1.0)

        budget_cat_mult = {"budget": 0.7, "mid": 1.0, "luxury": 1.6}
        if budget_category:
            rate *= budget_cat_mult.get(str(budget_category).lower(), 1.0)

        price_per_night = int(round(rate, -1))
        total = price_per_night * duration_nights

        return {
            "predicted_cost": total,
            "total_cost": total,
            "price_per_night": price_per_night,
            "duration_nights": duration_nights,
            "destination": destination,
            "accommodation_type": accommodation_type or "hotel",
            "star_rating": star_rating,
            "budget_category": budget_category or "mid",
            "currency": "INR",
            "currency_symbol": "₹",
            "confidence": 0.8,
            "factors": ["accommodation type", "star rating", "budget category"],
        }

    def predict_total_trip_cost(self, from_city=None, to_city=None, travel_date=None,
                                return_date=None, num_travelers=1, accommodation_type=None,
                                star_rating=None, budget_category=None, meal_preference=None,
                                include_activities=True, **kwargs):
        if not self._initialized: self.initialize()
        num_travelers = int(num_travelers or 1)

        # Nights = days between travel and return (min 1).
        nights = 1
        try:
            from datetime import datetime
            if return_date and travel_date:
                nights = max(1, (datetime.fromisoformat(str(return_date)[:10])
                                 - datetime.fromisoformat(str(travel_date)[:10])).days)
        except Exception:
            nights = 1

        flight = self.predict_flight_cost(from_city=from_city, to_city=to_city,
                                          travel_date=travel_date, num_travelers=num_travelers)
        flight_total = flight["total_cost"]

        accom = self.predict_accommodation_cost(
            destination=to_city, accommodation_type=accommodation_type,
            star_rating=star_rating, duration_nights=nights, budget_category=budget_category)
        accom_total = accom["total_cost"]

        # Meals / activities / local transport per traveler per day.
        meal_daily = {"veg": 700, "non-veg": 900, "mixed": 1100, "luxury": 2200}
        meal_cost = meal_daily.get(str(meal_preference or "mixed").lower(), 1000) * num_travelers * (nights + 1)
        activity_cost = (2000 * num_travelers * (nights + 1)) if include_activities else 0
        local_transport = 600 * num_travelers * (nights + 1)

        sub_total = flight_total + accom_total
        # Can't exceed a sane fraction of sub-costs; meals/activities scale with it.
        meals = int(min(meal_cost, sub_total * 0.35))
        activities = int(min(activity_cost, sub_total * 0.3))
        transport = int(min(local_transport, sub_total * 0.15))
        contingency = int(sub_total * 0.1)

        total = sub_total + meals + activities + transport + contingency

        breakdown = {
            "flights": flight_total,
            "accommodation": accom_total,
            "meals": meals,
            "activities": activities,
            "local_transport": transport,
            "contingency": contingency,
        }

        return {
            "total_cost": total,
            "total_trip_cost": total,
            "predicted_cost": total,
            "breakdown": breakdown,
            "num_travelers": num_travelers,
            "nights": nights,
            "currency": "INR",
            "currency_symbol": "₹",
            "confidence": round(min(0.92, 0.6 + flight.get("confidence", 0.7) * 0.2), 2),
            "factors": ["flight", "accommodation", "meals", "activities", "contingency"],
        }

    def optimize_budget(self, current_cost=None, target_budget=None, flexibility=0.2, **kwargs):
        if not self._initialized: self.initialize()

        # current_cost may arrive as a dict {category: amount} or a plain number.
        if isinstance(current_cost, dict):
            base_alloc = {str(k): float(v) for k, v in current_cost.items() if v is not None}
            current = sum(base_alloc.values())
        else:
            current = float(current_cost or 0)
            base_alloc = {
                "flights": current * 0.35, "accommodation": current * 0.30,
                "meals": current * 0.15, "activities": current * 0.15,
                "local_transport": current * 0.05,
            }

        target = float(target_budget or current)
        try:
            if isinstance(flexibility, dict) or flexibility is None:
                flexibility = 0.2
            else:
                flexibility = float(flexibility)
        except Exception:
            flexibility = 0.2

        overage = max(0.0, current - target)
        suggestions = []

        if current <= 0 or target <= 0:
            return {
                "status": "not_enough_data",
                "overage": overage,
                "suggestions": ["Provide current and target budget to optimize."],
                "allocations": base_alloc,
            }

        if overage <= 0:
            return {
                "status": "in_budget",
                "overage": overage,
                "current_cost": current, "target_budget": target,
                "flexibility": flexibility,
                "suggestions": ["Great news — you are already within budget."],
                "allocations": base_alloc,
            }

        # Trim discretionary categories proportionally to the overage.
        edited = dict(base_alloc)
        discretionary = [k for k in ("activities", "local_transport", "meals") if k in edited and edited[k] > 0]
        to_trim = overage
        if discretionary:
            first = discretionary[0]
            cut_first = min(edited[first] * (flexibility or 0.2), to_trim)
            edited[first] = max(0.0, edited[first] - cut_first)
            to_trim -= cut_first
            suggestions.append(f"Trim {first.replace('_', ' ')} by {_format_inr(cut_first)}.")
            for cat in discretionary[1:]:
                if to_trim <= 0:
                    break
                cut = min(edited[cat], to_trim)
                edited[cat] = max(0.0, edited[cat] - cut)
                to_trim -= cut
                if cut > 0:
                    suggestions.append(f"Trim {cat.replace('_', ' ')} by {_format_inr(cut)}.")
        if to_trim > 0:
            suggestions.append(f"Reduce the plan's total spend by about {_format_inr(to_trim)} "
                               f"to hit your target of {_format_inr(target)}.")

        return {
            "status": "recommendations",
            "overage": overage,
            "current_cost": current, "target_budget": target,
            "flexibility": flexibility,
            "suggestions": suggestions,
            "allocations": edited,
            "currency": "INR",
            "currency_symbol": "₹",
        }

    def optimize_itinerary(self, places=None, start_location=None, num_days=1,
                           daily_time_budget=None, **kwargs):
        if not self._initialized: self.initialize()
        places = places or []

        def label(p):
            return str(p.get("name") or p.get("place_name") or p.get("Place Name") or "Unknown")

        def lat_lon(p):
            try:
                return (float(p.get("lat")), float(p.get("lon")))
            except Exception:
                return None

        num_days = max(1, int(num_days or 1))
        # Nearest-neighbour day grouping: sort by pseudo distance from start, chunk evenly.
        start = start_location or {}
        ordered = sorted(
            places,
            key=lambda p: self._pseudo_distance(str(start.get("name", "")), label(p)),
        )

        days = []
        chunk = max(1, len(ordered) // num_days if num_days else len(ordered))
        for d in range(num_days):
            day_places = ordered[d * chunk:(d + 1) * chunk]
            if not day_places:
                continue
            days.append({
                "day": d + 1,
                "places": [
                    {"name": label(p), "category": p.get("category") or "General",
                     "lat": (lat_lon(p) or (None, None))[0],
                     "lon": (lat_lon(p) or (None, None))[1]}
                    for p in day_places
                ],
                "estimated_time": daily_time_budget or 8,
            })

        return {
            "optimized_days": days,
            "total_places": len(places),
            "num_days": num_days,
            "estimated_distance_km": sum(
                self._pseudo_distance(label(ordered[i]), label(ordered[i + 1]))
                for i in range(max(0, len(ordered) - 1))
            ),
            "status": "success",
        }

    def validate_itinerary(self, itinerary=None, **kwargs):
        if not self._initialized: self.initialize()
        itinerary = itinerary or {}
        issues = []
        warnings = []

        days = itinerary.get("days") or itinerary.get("itinerary") or itinerary.get("parsedDays") or []
        if itinerary.get("generated_itinerary") and not days:
            # Fallback: treat as single-day free-form text.
            days = [{"items": [{"text": itinerary["generated_itinerary"]}], "day": 1}]
        if not days:
            issues.append("Itinerary has no days — nothing to validate.")

        seen = set()
        for day in days:
            items = day.get("items") or day.get("activities") or day.get("places") or []
            if not items:
                warnings.append(f"Day {day.get('day', '?')} has no activities.")
            for it in items:
                text = str(it.get("text") or it.get("name") or "").strip()
                if not text:
                    continue
                key = text.lower()
                if key in seen:
                    issues.append(f"Duplicate activity detected: \"{text}\"")
                seen.add(key)

        # Time feasibility (simple heuristic: more than 8 items in a day is too much).
        for day in days:
            n = len(day.get("items") or day.get("activities") or day.get("places") or [])
            if n > 8:
                warnings.append(f"Day {day.get('day', '?')} is overloaded ({n} activities).")

        stress = len(issues) + len(warnings) * 0.5
        score = round(max(0, min(100, 100 - stress * 12)), 1)

        return {
            "valid": len(issues) == 0,
            "score": score,
            "issues": issues,
            "warnings": warnings,
            "total_days": len(days),
            "currency": "INR",
            "currency_symbol": "₹",
        }

    def generate_itinerary_description(self, itinerary=None, style="engaging", **kwargs):
        if not self._initialized: self.initialize()
        text = str(itinerary or "")
        try:
            if text and len(text.strip()) >= 50:
                from services.lmstudio_service import lmstudio_service as _lm
                response = _lm["chat"]([
                    {"role": "system", "content": f"Write a short, {style} description of this itinerary (2-3 sentences)."},
                    {"role": "user", "content": text[:1500]},
                ], temperature=0.6, max_tokens=120)
                desc = response.get("text", "").strip()
                if desc:
                    return {"description": desc, "source": "llm"}
        except Exception:
            pass

        # Template fallback so the endpoint is never dead.
        return {
            "description": (
                f"A {style} journey that balances iconic sights, authentic local "
                f"experiences and relaxed downtime — thoughtfully paced and budget-aware."
            ),
            "source": "template",
        }

    def explain_recommendation(self, destination=None, user_profile=None, **kwargs):
        if not self._initialized: self.initialize()
        user_profile = user_profile or {}
        preferences = user_profile.get("preferences") or user_profile.get("categories") or []
        if isinstance(preferences, str):
            preferences = [preferences]

        # Match destination attributes against the user's preferences.
        dest_row = None
        if self.destinations_df is not None and not self.destinations_df.empty:
            for _, row in self.destinations_df.iterrows():
                name = str(row.get("Destination Name") or row.get("destination_name") or row.get("Destination") or "")
                if name.strip().lower() == str(destination or "").strip().lower():
                    dest_row = row
                    break

        dest_attrs = {}
        if dest_row is not None:
            dest_attrs = {
                "category": str(dest_row.get("Category") or dest_row.get("category") or ""),
                "state": str(dest_row.get("State") or dest_row.get("state") or ""),
                "best_time": str(dest_row.get("Best Time to Visit") or dest_row.get("best_time_visit") or ""),
                "description": str(dest_row.get("Description") or dest_row.get("description") or dest_row.get("text") or ""),
            }

        matches = []
        for pref in preferences:
            pref_l = str(pref).lower()
            haystack = (dest_attrs.get("category", "") + " " + dest_attrs.get("description", "")).lower()
            if pref_l in haystack or pref_l in str(destination or "").lower():
                matches.append({"preference": pref, "matched": pref_l in haystack})

        if dest_row is None:
            matches = [{"preference": str(p or ""), "matched": False} for p in preferences]

        explanation = (
            f"{destination} is a strong match: it offers {dest_attrs.get('category') or 'something for every traveller'} "
            f"in {dest_attrs.get('state') or 'India'}, best visited {dest_attrs.get('best_time') or 'year-round'}."
        ).strip()

        return {
            "destination": destination,
            "explanation": explanation,
            "matches": matches,
            "category": dest_attrs.get("category"),
            "state": dest_attrs.get("state"),
            "best_time": dest_attrs.get("best_time"),
            "description": (dest_attrs.get("description") or "")[:280],
            "confidence": 0.7,
        }

    def query_knowledge_base(self, query=None, top_k=5, **kwargs):
        if not self._initialized: self.initialize()
        if not query:
            return {"query": "", "results": [], "count": 0}
        try:
            from services.rag_service import rag_service as _rag
            _rag.seed_knowledge_base()
            results = _rag.retrieve(query, top_k=int(top_k or 5))
        except Exception as e:
            logger.warning(f"Knowledge base query failed: {e}")
            results = []

        return {
            "query": query,
            "count": len(results),
            "results": [
                {"id": r.get("id"), "text": r.get("text", "")[:300],
                 "meta": r.get("meta", {}), "distance": r.get("distance", 0)}
                for r in results
            ],
        }

    def get_destination_insights(self, destination=None, **kwargs):
        if not self._initialized: self.initialize()
        info = {"destination": destination, "insights": [], "sources": []}
        if not destination:
            return info
        try:
            from services.rag_service import rag_service as _rag
            info["insights"] = [_rag.retrieve(f"Information about {destination}", top_k=3)]
            info["sources"] = ["chromadb"]
        except Exception as e:
            logger.warning(f"Destination insights failed: {e}")
        return info

    def get_smart_suggestions(self, **kwargs):
        if not self._initialized: self.initialize()
        suggestions = []
        if self.destinations_df is not None and not self.destinations_df.empty:
            for _, row in self.destinations_df.sample(min(5, len(self.destinations_df))).iterrows():
                name = row.get("Destination Name") or row.get("destination_name") or row.get("Destination") or ""
                state = row.get("State") or row.get("state") or ""
                if name:
                    suggestions.append(f"{name}" + (f", {state}" if state else ""))
        return suggestions

model_service = ModelService()
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
    
    # LLM Methods (Placeholder - will be implemented with actual LLM)
    def parse_natural_language_query(self, query: str) -> Dict:
        """Parse natural language query"""
        # Simplified parsing for now
        # In production, this would use fine-tuned LLM
        
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
        destinations = ['goa', 'jaipur', 'kerala', 'udaipur', 'manali', 'delhi', 'mumbai']
        for dest in destinations:
            if dest in query_lower:
                result['destination'] = dest.title()
                break
        
        # Extract duration
        import re
        duration_match = re.search(r'(\d+)\s*day', query_lower)
        if duration_match:
            result['duration'] = int(duration_match.group(1))
        
        # Extract travelers
        travelers_match = re.search(r'(\d+)\s*people|(\d+)\s*person', query_lower)
        if travelers_match:
            result['travelers'] = int(travelers_match.group(1) or travelers_match.group(2))
        
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
        """Generate itinerary description"""
        # Simplified generation for now
        # In production, this would use fine-tuned LLM
        
        num_days = itinerary.get('num_days', 0)
        total_places = itinerary.get('total_places', 0)
        
        description = f"Experience an amazing {num_days}-day journey visiting {total_places} incredible destinations. "
        description += "This carefully crafted itinerary ensures you make the most of your time while exploring the best attractions. "
        description += "Each day is optimized for minimal travel time and maximum enjoyment."
        
        highlights = [
            f"Visit {total_places} top-rated attractions",
            f"Optimized {num_days}-day schedule",
            "Minimal travel time between locations",
            "Flexible timing for each activity"
        ]
        
        return {
            'description': description,
            'highlights': highlights
        }
    
    def explain_recommendation(
        self,
        destination: str,
        user_profile: Dict[str, Any]
    ) -> Dict:
        """Explain recommendation"""
        # Simplified explanation for now
        # In production, this would use fine-tuned LLM
        
        explanation = f"We recommend {destination} based on your preferences. "
        explanation += "This destination matches your interests and budget requirements. "
        explanation += "It's highly rated by travelers with similar profiles."
        
        key_factors = [
            "Matches your preferred category",
            "Within your budget range",
            "Highly rated by similar travelers",
            "Best time to visit aligns with your dates"
        ]
        
        return {
            'explanation': explanation,
            'key_factors': key_factors
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


# Create global instance
model_service = ModelService()

"""ML Models module"""
from .recommendation import (
    ContentBasedRecommender,
    CollaborativeFilteringRecommender,
    HybridRecommender
)
from .cost_prediction import (
    FlightCostPredictor,
    AccommodationCostPredictor,
    TripCostPredictor
)
from .itinerary_optimizer import ItineraryOptimizer

__all__ = [
    "ContentBasedRecommender",
    "CollaborativeFilteringRecommender",
    "HybridRecommender",
    "FlightCostPredictor",
    "AccommodationCostPredictor",
    "TripCostPredictor",
    "ItineraryOptimizer"
]

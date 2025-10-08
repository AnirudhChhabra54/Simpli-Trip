"""
Script to train all ML models
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import data_loader
from models.recommendation import HybridRecommender
from models.cost_prediction import TripCostPredictor, FlightCostPredictor
from models.itinerary_optimizer import ItineraryOptimizer
from utils.logger import logger
from config.settings import settings


def train_recommendation_system():
    """Train and save recommendation system"""
    logger.info("=" * 50)
    logger.info("Training Recommendation System")
    logger.info("=" * 50)
    
    try:
        # Load data
        logger.info("Loading destination data...")
        destinations_df = data_loader.load_explore_india_dataset()
        
        # Save processed data
        data_loader.save_processed_data(destinations_df, "destinations_processed.csv")
        
        # Train model
        logger.info("Training hybrid recommender...")
        recommender = HybridRecommender()
        recommender.fit(destinations_df)
        
        # Save model
        model_path = Path(settings.MODEL_DIR) / "recommender"
        model_path.mkdir(parents=True, exist_ok=True)
        recommender.save(str(model_path))
        
        logger.info("✓ Recommendation system trained and saved successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to train recommendation system: {e}")
        return False


def train_cost_prediction_models():
    """Train and save cost prediction models"""
    logger.info("=" * 50)
    logger.info("Training Cost Prediction Models")
    logger.info("=" * 50)
    
    try:
        # Load airline data
        logger.info("Loading airline price data...")
        # Use sample for faster training
        flights_df = data_loader.load_airline_prices_dataset(sample_size=100000)
        
        # Train flight cost predictor
        logger.info("Training flight cost predictor...")
        flight_predictor = FlightCostPredictor()
        metrics = flight_predictor.fit(flights_df)
        
        logger.info(f"Flight predictor metrics: MAE={metrics['mae']:.2f}, "
                   f"RMSE={metrics['rmse']:.2f}, R²={metrics['r2']:.3f}")
        
        # Save model
        model_path = Path(settings.MODEL_DIR) / "cost_predictor"
        model_path.mkdir(parents=True, exist_ok=True)
        
        trip_predictor = TripCostPredictor()
        trip_predictor.flight_predictor = flight_predictor
        trip_predictor.save(str(model_path))
        
        logger.info("✓ Cost prediction models trained and saved successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to train cost prediction models: {e}")
        logger.info("Using default cost prediction models")
        return False


def setup_itinerary_optimizer():
    """Set up itinerary optimizer with data"""
    logger.info("=" * 50)
    logger.info("Setting up Itinerary Optimizer")
    logger.info("=" * 50)
    
    try:
        # Load places data
        logger.info("Loading tourist places data...")
        places_df = data_loader.load_tourist_places_dataset()
        
        # Save processed data
        data_loader.save_processed_data(places_df, "places_processed.csv")
        
        logger.info("✓ Itinerary optimizer data prepared successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to setup itinerary optimizer: {e}")
        return False


def download_llm_datasets():
    """Download datasets for LLM fine-tuning"""
    logger.info("=" * 50)
    logger.info("Downloading LLM Training Datasets")
    logger.info("=" * 50)
    
    try:
        # Download hotel reviews
        logger.info("Downloading hotel reviews dataset...")
        reviews_df = data_loader.load_hotel_reviews_dataset()
        data_loader.save_processed_data(reviews_df, "hotel_reviews_processed.csv")
        
        # Download travelogues
        logger.info("Downloading travelogues dataset...")
        travelogues_df = data_loader.load_travelogues_dataset()
        data_loader.save_processed_data(travelogues_df, "travelogues_processed.csv")
        
        logger.info("✓ LLM datasets downloaded successfully")
        logger.info("Note: LLM fine-tuning requires separate training script")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to download LLM datasets: {e}")
        return False


def main():
    """Main training function"""
    logger.info("=" * 50)
    logger.info("SimpliTrip Model Training")
    logger.info("=" * 50)
    
    results = {
        'recommendation': False,
        'cost_prediction': False,
        'itinerary': False,
        'llm_data': False
    }
    
    # Train recommendation system
    results['recommendation'] = train_recommendation_system()
    
    # Train cost prediction models
    results['cost_prediction'] = train_cost_prediction_models()
    
    # Setup itinerary optimizer
    results['itinerary'] = setup_itinerary_optimizer()
    
    # Download LLM datasets
    results['llm_data'] = download_llm_datasets()
    
    # Summary
    logger.info("=" * 50)
    logger.info("Training Summary")
    logger.info("=" * 50)
    logger.info(f"Recommendation System: {'✓' if results['recommendation'] else '✗'}")
    logger.info(f"Cost Prediction: {'✓' if results['cost_prediction'] else '✗'}")
    logger.info(f"Itinerary Optimizer: {'✓' if results['itinerary'] else '✗'}")
    logger.info(f"LLM Datasets: {'✓' if results['llm_data'] else '✗'}")
    logger.info("=" * 50)
    
    if all(results.values()):
        logger.info("✓ All models trained successfully!")
    else:
        logger.warning("⚠ Some models failed to train. Check logs for details.")


if __name__ == "__main__":
    main()

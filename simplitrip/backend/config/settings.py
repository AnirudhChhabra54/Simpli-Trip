"""
Configuration settings for SimpliTrip Backend
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS Settings
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/simplitrip"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Kaggle API
    KAGGLE_USERNAME: str = ""
    KAGGLE_KEY: str = ""
    
    # Google Maps API
    GOOGLE_MAPS_API_KEY: str = ""
    
    # Model Paths
    MODEL_DIR: str = "./models/saved_models"
    DATA_DIR: str = "./data"
    
    # LLM Configuration
    LLM_MODEL_NAME: str = "meta-llama/Llama-2-7b-chat-hf"
    LLM_MAX_LENGTH: int = 512
    LLM_TEMPERATURE: float = 0.7
    LLM_DEVICE: str = "cpu"  # or "cuda"
    
    # Cache Configuration
    CACHE_TTL: int = 3600  # 1 hour
    ENABLE_CACHE: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Dataset URLs (Kaggle)
    DATASET_EXPLORE_INDIA: str = "surajjha101/explore-india-a-tourist-destination-dataset"
    DATASET_TOURIST_PLACES: str = "rajuprasad23/famous-indian-tourist-places"
    DATASET_AIRLINE_PRICES: str = "sagnik1511/airline-ticket-price-in-india-makemytrip"
    DATASET_HOTEL_REVIEWS: str = "ashishguptaji/tripadvisor-indian-hotel-reviews"
    DATASET_TRAVELOGUES: str = "akshat59/traveltalesindia-travelogue-dataset"
    
    # Model Configuration
    RECOMMENDATION_TOP_N: int = 10
    COST_PREDICTION_CONFIDENCE: float = 0.85
    ITINERARY_MAX_PLACES_PER_DAY: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()


# Create necessary directories
def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        settings.MODEL_DIR,
        settings.DATA_DIR,
        os.path.join(settings.DATA_DIR, "raw"),
        os.path.join(settings.DATA_DIR, "processed"),
        os.path.join(settings.DATA_DIR, "downloads"),
        os.path.dirname(settings.LOG_FILE),
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# Initialize directories on import
create_directories()

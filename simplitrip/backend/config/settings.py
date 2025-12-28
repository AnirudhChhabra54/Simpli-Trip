# # """
# # Configuration settings for SimpliTrip Backend
# # """
# # from pydantic_settings import BaseSettings
# # from typing import List
# # import os


# # class Settings(BaseSettings):
# #     """Application settings"""
    
# #     # API Configuration
# #     API_HOST: str = "0.0.0.0"
# #     API_PORT: int = 8000
# #     API_RELOAD: bool = True
# #     ENVIRONMENT: str = "development"
# #     API_V1_PREFIX: str = "/api/v1"
    
# #     # CORS Settings
# #     CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
# #     @property
# #     def cors_origins_list(self) -> List[str]:
# #         """Parse CORS origins from comma-separated string"""
# #         return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
# #     # Database Configuration
# #     DATABASE_URL: str = "postgresql://user:password@localhost:5432/simplitrip"
# #     REDIS_URL: str = "redis://localhost:6379/0"
    
# #     # Kaggle API
# #     KAGGLE_USERNAME: str = ""
# #     KAGGLE_KEY: str = ""
    
# #     # Google Maps API
# #     GOOGLE_MAPS_API_KEY: str = ""
    
# #     # Model Paths
# #     MODEL_DIR: str = "./models/saved_models"
# #     DATA_DIR: str = "./data"
    
# #     # LLM Configuration
# #     LLM_MODEL_NAME: str = "meta-llama/Llama-2-7b-chat-hf"
# #     LLM_MAX_LENGTH: int = 512
# #     LLM_TEMPERATURE: float = 0.7
# #     LLM_DEVICE: str = "cpu"  # or "cuda"
    
# #     # Cache Configuration
# #     CACHE_TTL: int = 3600  # 1 hour
# #     ENABLE_CACHE: bool = True
    
# #     # Logging
# #     LOG_LEVEL: str = "INFO"
# #     LOG_FILE: str = "./logs/app.log"
    
# #     # Security
# #     SECRET_KEY: str = "your-secret-key-change-this-in-production"
# #     ALGORITHM: str = "HS256"
# #     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
# #     # Dataset URLs (Kaggle)
# #     DATASET_EXPLORE_INDIA: str = "surajjha101/explore-india-a-tourist-destination-dataset"
# #     DATASET_TOURIST_PLACES: str = "rajuprasad23/famous-indian-tourist-places"
# #     DATASET_AIRLINE_PRICES: str = "sagnik1511/airline-ticket-price-in-india-makemytrip"
# #     DATASET_HOTEL_REVIEWS: str = "ashishguptaji/tripadvisor-indian-hotel-reviews"
# #     DATASET_TRAVELOGUES: str = "akshat59/traveltalesindia-travelogue-dataset"
    
# #     # Model Configuration
# #     RECOMMENDATION_TOP_N: int = 10
# #     COST_PREDICTION_CONFIDENCE: float = 0.85
# #     ITINERARY_MAX_PLACES_PER_DAY: int = 5
    
# #     class Config:
# #         env_file = ".env"
# #         case_sensitive = True


# # # Create global settings instance
# # settings = Settings()


# # # Create necessary directories
# # def create_directories():
# #     """Create necessary directories if they don't exist"""
# #     directories = [
# #         settings.MODEL_DIR,
# #         settings.DATA_DIR,
# #         os.path.join(settings.DATA_DIR, "raw"),
# #         os.path.join(settings.DATA_DIR, "processed"),
# #         os.path.join(settings.DATA_DIR, "downloads"),
# #         os.path.dirname(settings.LOG_FILE),
# #     ]
    
# #     for directory in directories:
# #         os.makedirs(directory, exist_ok=True)


# # # Initialize directories on import
# # create_directories()


# # backend/config/settings.py
# """
# Complete settings.py for SimpliTrip (LM Studio-ready).
# - All LM Studio settings included.
# - Ollama settings are commented out for now.
# - Uses pydantic-settings BaseSettings and reads .env by default.
# """

# from pydantic_settings import BaseSettings
# from typing import List, Optional
# from pathlib import Path
# import os

# BASE_DIR = Path(__file__).resolve().parents[2]  # simplitrip/backend/..
# DEFAULT_LOG_DIR = BASE_DIR / "logs"
# DEFAULT_MODEL_DIR = BASE_DIR / "models" / "saved_models"
# DEFAULT_DATA_DIR = BASE_DIR / "data"

# class Settings(BaseSettings):
#     """Application settings for SimpliTrip"""

#     # ---------------------------
#     # API / Env
#     # ---------------------------
#     API_HOST: str = "0.0.0.0"
#     API_PORT: int = 8000
#     API_RELOAD: bool = True
#     ENVIRONMENT: str = "development"
#     API_V1_PREFIX: str = "/api/v1"

#     # ---------------------------
#     # CORS
#     # ---------------------------
#     CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
#     @property
#     def cors_origins_list(self) -> List[str]:
#         return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

#     # ---------------------------
#     # Database / Cache
#     # ---------------------------
#     DATABASE_URL: str = "postgresql://user:password@localhost:5432/simplitrip"
#     REDIS_URL: str = "redis://localhost:6379/0"

#     # ---------------------------
#     # Paths
#     # ---------------------------
#     MODEL_DIR: str = str(DEFAULT_MODEL_DIR)
#     DATA_DIR: str = str(DEFAULT_DATA_DIR)
#     LOG_FILE: str = str(DEFAULT_LOG_DIR / "app.log")

#     # ---------------------------
#     # LLM general defaults
#     # ---------------------------
#     # Provider selection: 'lmstudio' or 'ollama' (we set lmstudio by default)
#     LLM_PROVIDER: str = "lmstudio"

#     # Generic LLM settings used by code as fallback
#     LLM_MODEL_NAME: str = "meta-llama/Llama-2-7b-chat-hf"
#     LLM_MAX_LENGTH: int = 512
#     LLM_TEMPERATURE: float = 0.7
#     LLM_DEVICE: str = "cpu"  # 'cpu' or 'cuda' if GPU available

#     # ---------------------------
#     # LM Studio specific settings
#     # ---------------------------
#     LMSTUDIO_HOST: str = "http://localhost:8080"
#     LMSTUDIO_MODEL: str = "openai/gpt-oss-20b"   # match exact model name shown in LM Studio
#     LMSTUDIO_TIMEOUT: int = 30
#     LMSTUDIO_RETRIES: int = 2
#     LMSTUDIO_BACKOFF: float = 1.0
#     LMSTUDIO_API_KEY: Optional[str] = ""  # if LM Studio requires an API key, set it in .env

#     # ---------------------------
#     # (Commented) Ollama settings - kept here for reference / future swap
#     # ---------------------------
#     # OLLAMA_HOST: str = "http://localhost:11434"
#     # OLLAMA_MODEL: str = "llama2"
#     # OLLAMA_TIMEOUT: int = 25
#     # OLLAMA_RETRIES: int = 2

#     # ---------------------------
#     # Cache / App behavior
#     # ---------------------------
#     CACHE_TTL: int = 3600
#     ENABLE_CACHE: bool = True

#     # ---------------------------
#     # Recommendation / ML config
#     # ---------------------------
#     RECOMMENDATION_TOP_N: int = 10
#     COST_PREDICTION_CONFIDENCE: float = 0.85
#     ITINERARY_MAX_PLACES_PER_DAY: int = 5

#     # ---------------------------
#     # External API keys (placeholders)
#     # ---------------------------
#     GOOGLE_MAPS_API_KEY: Optional[str] = ""
#     KAGGLE_USERNAME: Optional[str] = ""
#     KAGGLE_KEY: Optional[str] = ""

#     # ---------------------------
#     # Logging / Security
#     # ---------------------------
#     LOG_LEVEL: str = "INFO"
#     SECRET_KEY: str = "your-secret-key-change-this-in-production"
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

#     # ---------------------------
#     # Dataset references (defaults)
#     # ---------------------------
#     DATASET_EXPLORE_INDIA: str = "surajjha101/explore-india-a-tourist-destination-dataset"
#     DATASET_TOURIST_PLACES: str = "rajuprasad23/famous-indian-tourist-places"

#     # ---------------------------
#     # Pydantic Settings config
#     # ---------------------------
#     class Config:
#         env_file = ".env"
#         case_sensitive = True

# # Instantiate global settings
# settings = Settings()

# # ---------------------------
# # Ensure directories exist (safe to run on import)
# # ---------------------------
# def create_directories():
#     dirs = [
#         Path(settings.MODEL_DIR),
#         Path(settings.DATA_DIR),
#         Path(settings.DATA_DIR) / "raw",
#         Path(settings.DATA_DIR) / "processed",
#         Path(settings.DATA_DIR) / "downloads",
#         Path(settings.LOG_FILE).parent,
#     ]
#     for d in dirs:
#         try:
#             d.mkdir(parents=True, exist_ok=True)
#         except Exception:
#             # best-effort: if this fails (permissions), app should still start but warn
#             pass

# create_directories()

# # ---------------------------
# # Helper: simple summary for debug / health endpoints
# # ---------------------------
# def llm_config_summary() -> dict:
#     """Return a small summary of LLM config used by the app."""
#     return {
#         "provider": settings.LLM_PROVIDER,
#         "lmstudio": {
#             "host": settings.LMSTUDIO_HOST,
#             "model": settings.LMSTUDIO_MODEL,
#             "timeout": settings.LMSTUDIO_TIMEOUT,
#         },
#         # "ollama": { "host": settings.OLLAMA_HOST, "model": settings.OLLAMA_MODEL },  # commented
#         "device": settings.LLM_DEVICE,
#     }

# backend/config/settings.py
import os
from typing import List, Optional, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "SimpliTrip AI Backend"
    
    # Server Config
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"  # <--- FIXED: Added this missing field
    ENVIRONMENT: str = "development"
    
    # CORS
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://localhost:8000"]

    @field_validator("CORS_ORIGINS")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return []

    # Directories
    MODEL_DIR: str = os.path.join("models", "saved_models")
    DATA_DIR: str = os.path.join("data")

    # Authentication / Security
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECRET_KEY: str = "your-super-secret-key-change-me"

    # Kaggle & External APIs
    KAGGLE_USERNAME: Optional[str] = None
    KAGGLE_KEY: Optional[str] = None
    GOOGLE_MAPS_API_KEY: Optional[str] = None

    # LLM / LM Studio Configuration
    LLM_PROVIDER: str = "lmstudio"
    LLM_MODEL_NAME: str = "openai/gpt-oss-20b"
    
    LMSTUDIO_HOST: str = "http://localhost:1234"  # Base URL without /v1
    LMSTUDIO_TIMEOUT: int = 30
    LMSTUDIO_RETRIES: int = 2
    LMSTUDIO_BACKOFF: float = 1.0
    LMSTUDIO_API_KEY: str = "lm-studio"

    # Pydantic Config: strictly allow .env file and ignore unknown fields
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
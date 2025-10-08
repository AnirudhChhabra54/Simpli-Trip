"""
Data loading utilities for Kaggle datasets
"""
import os
import pandas as pd
from pathlib import Path
from typing import Optional
from config.settings import settings
from utils.logger import logger


class DataLoader:
    """Handle downloading and loading datasets from Kaggle"""
    
    def __init__(self):
        self.api = None
        self.data_dir = Path(settings.DATA_DIR)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Create directories
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def authenticate_kaggle(self):
        """Authenticate with Kaggle API"""
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            self.api = KaggleApi()
            self.api.authenticate()
            logger.info("Successfully authenticated with Kaggle API")
        except Exception as e:
            logger.warning(f"Failed to authenticate with Kaggle: {e}")
            logger.info("Kaggle datasets will not be available. Using sample data instead.")
            raise
    
    def download_dataset(self, dataset_name: str, force: bool = False) -> Path:
        """
        Download dataset from Kaggle
        
        Args:
            dataset_name: Kaggle dataset identifier (e.g., 'username/dataset-name')
            force: Force re-download even if exists
            
        Returns:
            Path to downloaded dataset directory
        """
        if not self.api:
            self.authenticate_kaggle()
        
        dataset_dir = self.raw_dir / dataset_name.split('/')[-1]
        
        # Check if already downloaded
        if dataset_dir.exists() and not force:
            logger.info(f"Dataset {dataset_name} already exists at {dataset_dir}")
            return dataset_dir
        
        try:
            logger.info(f"Downloading dataset: {dataset_name}")
            self.api.dataset_download_files(
                dataset_name,
                path=dataset_dir,
                unzip=True
            )
            logger.info(f"Successfully downloaded {dataset_name} to {dataset_dir}")
            return dataset_dir
        except Exception as e:
            logger.error(f"Failed to download dataset {dataset_name}: {e}")
            raise
    
    def load_explore_india_dataset(self) -> pd.DataFrame:
        """Load Explore India tourist destinations dataset"""
        dataset_name = settings.DATASET_EXPLORE_INDIA
        dataset_dir = self.download_dataset(dataset_name)
        
        # Find CSV file in directory
        csv_files = list(dataset_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {dataset_dir}")
        
        df = pd.read_csv(csv_files[0])
        logger.info(f"Loaded Explore India dataset: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
    
    def load_tourist_places_dataset(self) -> pd.DataFrame:
        """Load Famous Indian Tourist Places dataset"""
        dataset_name = settings.DATASET_TOURIST_PLACES
        dataset_dir = self.download_dataset(dataset_name)
        
        csv_files = list(dataset_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {dataset_dir}")
        
        df = pd.read_csv(csv_files[0])
        logger.info(f"Loaded Tourist Places dataset: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
    
    def load_airline_prices_dataset(self, sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Load Airline Ticket Prices dataset
        
        Args:
            sample_size: Number of rows to sample (useful for large dataset)
        """
        dataset_name = settings.DATASET_AIRLINE_PRICES
        dataset_dir = self.download_dataset(dataset_name)
        
        csv_files = list(dataset_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {dataset_dir}")
        
        # Load with sampling if specified (dataset is 5M+ rows)
        if sample_size:
            df = pd.read_csv(csv_files[0], nrows=sample_size)
            logger.info(f"Loaded Airline Prices dataset (sampled): {df.shape[0]} rows")
        else:
            df = pd.read_csv(csv_files[0])
            logger.info(f"Loaded Airline Prices dataset: {df.shape[0]} rows, {df.shape[1]} columns")
        
        return df
    
    def load_hotel_reviews_dataset(self) -> pd.DataFrame:
        """Load TripAdvisor Indian Hotel Reviews dataset"""
        dataset_name = settings.DATASET_HOTEL_REVIEWS
        dataset_dir = self.download_dataset(dataset_name)
        
        csv_files = list(dataset_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {dataset_dir}")
        
        df = pd.read_csv(csv_files[0])
        logger.info(f"Loaded Hotel Reviews dataset: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
    
    def load_travelogues_dataset(self) -> pd.DataFrame:
        """Load TravelTalesIndia Travelogues dataset"""
        dataset_name = settings.DATASET_TRAVELOGUES
        dataset_dir = self.download_dataset(dataset_name)
        
        csv_files = list(dataset_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {dataset_dir}")
        
        df = pd.read_csv(csv_files[0])
        logger.info(f"Loaded Travelogues dataset: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
    
    def save_processed_data(self, df: pd.DataFrame, filename: str):
        """Save processed dataframe"""
        filepath = self.processed_dir / filename
        df.to_csv(filepath, index=False)
        logger.info(f"Saved processed data to {filepath}")
    
    def load_processed_data(self, filename: str) -> pd.DataFrame:
        """Load processed dataframe"""
        filepath = self.processed_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Processed file not found: {filepath}")
        
        df = pd.read_csv(filepath)
        logger.info(f"Loaded processed data from {filepath}")
        return df


# Create global instance
data_loader = DataLoader()

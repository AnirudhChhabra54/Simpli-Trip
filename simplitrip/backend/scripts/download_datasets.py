#!/usr/bin/env python3
"""
SimpliTrip - Dataset Download Script
Downloads all required datasets from Kaggle for training ML models
"""

import os
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger

logger = setup_logger()


def check_kaggle_setup():
    """Check if Kaggle API is properly configured"""
    kaggle_json = Path.home() / '.kaggle' / 'kaggle.json'
    
    if not kaggle_json.exists():
        logger.error("Kaggle API credentials not found!")
        logger.info("Please follow these steps:")
        logger.info("1. Go to https://www.kaggle.com/settings")
        logger.info("2. Scroll to 'API' section")
        logger.info("3. Click 'Create New API Token'")
        logger.info("4. Move kaggle.json to ~/.kaggle/")
        logger.info("5. Run: chmod 600 ~/.kaggle/kaggle.json")
        return False
    
    # Check permissions
    if oct(kaggle_json.stat().st_mode)[-3:] != '600':
        logger.warning("Kaggle credentials have incorrect permissions")
        logger.info("Run: chmod 600 ~/.kaggle/kaggle.json")
        return False
    
    logger.info("✅ Kaggle API credentials found and configured correctly")
    return True


def download_dataset(dataset_name, output_dir):
    """Download a dataset from Kaggle"""
    try:
        import kaggle
        
        logger.info(f"📥 Downloading: {dataset_name}")
        
        # Create output directory
        output_path = Path(output_dir) / dataset_name.replace('/', '_')
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Download dataset
        kaggle.api.dataset_download_files(
            dataset_name,
            path=str(output_path),
            unzip=True
        )
        
        logger.info(f"✅ Downloaded: {dataset_name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download {dataset_name}: {str(e)}")
        return False


def main():
    """Main function to download all datasets"""
    
    print("=" * 60)
    print("SimpliTrip - Dataset Download Script")
    print("=" * 60)
    print()
    
    # Check Kaggle setup
    if not check_kaggle_setup():
        print()
        print("❌ Kaggle API not configured. Please set it up first.")
        print("   See: DATASETS_AND_IMAGES_GUIDE.md for instructions")
        return 1
    
    # Define datasets to download
    datasets = [
        {
            'name': 'surajjha101/explore-india-a-tourist-destination-dataset',
            'description': 'Explore India Tourist Destinations (156 destinations)',
            'size': '~50KB'
        },
        {
            'name': 'rajuprasad23/famous-indian-tourist-places',
            'description': 'Famous Indian Tourist Places (325 places)',
            'size': '~100KB'
        },
        {
            'name': 'sagnik1511/airline-ticket-price-in-india-makemytrip',
            'description': 'Airline Ticket Prices India (5M+ records)',
            'size': '~500MB'
        },
        {
            'name': 'ashishguptaji/tripadvisor-indian-hotel-reviews',
            'description': 'TripAdvisor Indian Hotel Reviews (11,800 reviews)',
            'size': '~5MB'
        },
        {
            'name': 'akshat59/traveltalesindia-travelogue-dataset',
            'description': 'Travel Tales India Travelogues (3,300+ stories)',
            'size': '~10MB'
        }
    ]
    
    # Set download directory
    download_dir = Path(__file__).parent.parent / 'data' / 'downloads'
    download_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Download directory: {download_dir}")
    print()
    print(f"📊 Datasets to download: {len(datasets)}")
    print()
    
    # Show dataset info
    for i, dataset in enumerate(datasets, 1):
        print(f"{i}. {dataset['description']}")
        print(f"   Size: {dataset['size']}")
        print()
    
    # Ask for confirmation
    response = input("Do you want to proceed with download? (y/n): ")
    if response.lower() != 'y':
        print("Download cancelled.")
        return 0
    
    print()
    print("Starting downloads...")
    print()
    
    # Download each dataset
    success_count = 0
    failed_datasets = []
    
    for i, dataset in enumerate(datasets, 1):
        print(f"[{i}/{len(datasets)}] {dataset['description']}")
        
        if download_dataset(dataset['name'], download_dir):
            success_count += 1
        else:
            failed_datasets.append(dataset['name'])
        
        print()
    
    # Summary
    print("=" * 60)
    print("Download Summary")
    print("=" * 60)
    print(f"✅ Successful: {success_count}/{len(datasets)}")
    print(f"❌ Failed: {len(failed_datasets)}/{len(datasets)}")
    
    if failed_datasets:
        print()
        print("Failed datasets:")
        for dataset in failed_datasets:
            print(f"  - {dataset}")
        print()
        print("💡 Note: The app will work with mock data if datasets fail to download")
    
    print()
    print("📁 Downloaded files location:")
    print(f"   {download_dir}")
    print()
    
    if success_count > 0:
        print("✅ Next steps:")
        print("   1. Process the datasets:")
        print("      python -c \"from utils.data_loader import DataLoader; DataLoader().load_all_datasets()\"")
        print()
        print("   2. Train the models:")
        print("      python scripts/train_models.py")
        print()
        print("   3. Restart the backend:")
        print("      python main.py")
    
    return 0 if success_count > 0 else 1


if __name__ == '__main__':
    sys.exit(main())

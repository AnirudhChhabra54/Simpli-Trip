import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import logging
from typing import List, Dict, Any
import time
import re
from utils.logger import logger

class DataCollectionService:
    """
    Service to collect destination data from various sources
    and format into structured CSV for model training
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_wikipedia_destinations(self, state: str) -> List[Dict]:
        """
        Scrape popular destinations from Wikipedia for a state
        """
        try:
            # Wikipedia search for tourism in state
            search_query = f"Tourism in {state}"
            url = f"https://en.wikipedia.org/wiki/Tourism_in_{state.replace(' ', '_')}"
            
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            destinations = []
            
            # Extract destination information
            # This is a simplified example - you'd need to customize per state
            content = soup.find('div', {'class': 'mw-parser-output'})
            
            # Look for lists of destinations
            for ul in content.find_all('ul'):
                for li in ul.find_all('li'):
                    text = li.get_text().strip()
                    if self._is_destination_text(text):
                        destination = self._parse_destination_from_text(text, state)
                        if destination:
                            destinations.append(destination)
            
            logger.info(f"Scraped {len(destinations)} destinations for {state}")
            return destinations[:20]  # Limit for testing
            
        except Exception as e:
            logger.error(f"Error scraping Wikipedia for {state}: {e}")
            return []
    
    def scrape_tripadvisor_destinations(self, state: str) -> List[Dict]:
        """
        Scrape destination data from TripAdvisor
        Note: This is a conceptual example - actual implementation needs API or careful scraping
        """
        # This would require TripAdvisor API or careful web scraping
        # For now, return mock data
        return self._get_mock_destinations(state)
    
    def _is_destination_text(self, text: str) -> bool:
        """Check if text likely describes a destination"""
        destination_indicators = [
            'beach', 'fort', 'temple', 'palace', 'hill station', 'wildlife',
            'national park', 'lake', 'waterfall', 'heritage', 'museum'
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in destination_indicators)
    
    def _parse_destination_from_text(self, text: str, state: str) -> Dict:
        """Parse destination information from text"""
        # Simple parsing - in real implementation, use NLP or more sophisticated parsing
        return {
            'destination_name': text.split('–')[0].split('-')[0].strip(),
            'description': text,
            'state': state,
            'category': self._infer_category(text),
            'best_time_visit': 'October to March',  # Default
            'budget_level': 'Medium'
        }
    
    def _infer_category(self, text: str) -> str:
        """Infer category from destination description"""
        text_lower = text.lower()
        
        category_mapping = {
            'beach': 'Beach',
            'fort': 'Historical',
            'temple': 'Religious',
            'palace': 'Historical', 
            'hill station': 'Hill Station',
            'wildlife': 'Wildlife',
            'national park': 'Wildlife',
            'lake': 'Nature',
            'waterfall': 'Nature',
            'museum': 'Cultural'
        }
        
        for keyword, category in category_mapping.items():
            if keyword in text_lower:
                return category
        
        return 'General'
    
    def _get_mock_destinations(self, state: str) -> List[Dict]:
        """Get mock destination data for testing"""
        mock_data = {
            'Goa': [
                {
                    'destination_name': 'Calangute Beach',
                    'description': 'Largest beach in North Goa known for water sports and vibrant atmosphere',
                    'category': 'Beach',
                    'best_time_visit': 'November to February',
                    'budget_level': 'Medium',
                    'activities': 'Water Sports, Swimming, Beach Volleyball',
                    'ideal_duration': '1 day'
                }
            ],
            'Himachal Pradesh': [
                {
                    'destination_name': 'Manali',
                    'description': 'Popular hill station in the Himalayas known for adventure sports and scenic beauty',
                    'category': 'Hill Station', 
                    'best_time_visit': 'March to June',
                    'budget_level': 'Medium',
                    'activities': 'Trekking, Paragliding, Skiing',
                    'ideal_duration': '3-4 days'
                }
            ]
        }
        
        return mock_data.get(state, [])
    
    def save_to_csv(self, destinations: List[Dict], filename: str):
        """Save destinations to CSV file"""
        if not destinations:
            logger.warning(f"No destinations to save for {filename}")
            return
        
        df = pd.DataFrame(destinations)
        df.to_csv(filename, index=False)
        logger.info(f"Saved {len(destinations)} destinations to {filename}")

# Create global instance
data_collection_service = DataCollectionService()
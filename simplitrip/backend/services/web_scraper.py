"""
Web Scraper Service for Indian Tourist Destinations
Scrapes data from various travel websites to get real-time destination information
"""
import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Optional
from utils.logger import logger


class DestinationWebScraper:
    """Web scraper for Indian tourist destinations"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def scrape_destination_info(self, destination_name: str, query_params: Dict) -> Dict:
        """
        Scrape destination information based on user query
        
        Args:
            destination_name: Name of the destination
            query_params: Parsed query parameters (budget, duration, preferences, etc.)
            
        Returns:
            Dict with destination information
        """
        try:
            # Extract query parameters
            budget = query_params.get('budget', 50000)
            duration = query_params.get('duration', 5)
            travelers = query_params.get('travelers', 2)
            categories = query_params.get('categories', [])
            
            # Build destination data
            destination_data = {
                'name': destination_name,
                'description': self._get_destination_description(destination_name),
                'best_time': self._get_best_time_to_visit(destination_name),
                'attractions': self._get_top_attractions(destination_name, categories),
                'estimated_costs': self._estimate_costs(destination_name, budget, duration, travelers),
                'accommodation_options': self._get_accommodation_options(destination_name, budget),
                'food_recommendations': self._get_food_recommendations(destination_name),
                'travel_tips': self._get_travel_tips(destination_name),
                'images': self._get_destination_images(destination_name),
            }
            
            return destination_data
            
        except Exception as e:
            logger.error(f"Error scraping destination info: {e}")
            return self._get_fallback_data(destination_name)
    
    def _get_destination_description(self, destination: str) -> str:
        """Get destination description"""
        # In production, this would scrape from travel websites
        # For now, return structured data
        descriptions = {
            'Goa': 'Sun, sand, and Portuguese heritage. Perfect beaches and vibrant nightlife within your budget.',
            'Jaipur': 'The Pink City of Palaces. Rich culture, stunning forts, and excellent food scene.',
            'Kerala': "God's Own Country. Backwaters, beaches, and authentic South Indian cuisine.",
            'Ladakh': 'Adventure in the Himalayas. Trekking, camping, and breathtaking landscapes.',
            'Udaipur': 'The City of Lakes. Romantic palaces, stunning architecture, and rich history.',
            'Rishikesh': 'Yoga capital of the world. Spiritual retreats, adventure sports, and Ganges views.',
            'Manali': 'Hill station paradise. Snow-capped mountains, adventure activities, and scenic beauty.',
            'Varanasi': 'Spiritual heart of India. Ancient temples, Ganges ghats, and cultural immersion.',
        }
        return descriptions.get(destination, f'Explore the beauty and culture of {destination}')
    
    def _get_best_time_to_visit(self, destination: str) -> str:
        """Get best time to visit"""
        best_times = {
            'Goa': 'November - February',
            'Jaipur': 'October - March',
            'Kerala': 'September - March',
            'Ladakh': 'May - September',
            'Udaipur': 'October - March',
            'Rishikesh': 'September - November, March - May',
            'Manali': 'October - February (snow), March - June (pleasant)',
            'Varanasi': 'October - March',
        }
        return best_times.get(destination, 'October - March')
    
    def _get_top_attractions(self, destination: str, categories: List[str]) -> List[Dict]:
        """Get top attractions based on categories"""
        attractions_db = {
            'Goa': [
                {'name': 'Baga Beach', 'category': 'Beach', 'rating': 4.5},
                {'name': 'Fort Aguada', 'category': 'Historical', 'rating': 4.3},
                {'name': 'Dudhsagar Falls', 'category': 'Adventure', 'rating': 4.6},
                {'name': 'Basilica of Bom Jesus', 'category': 'Cultural', 'rating': 4.7},
            ],
            'Jaipur': [
                {'name': 'Amber Fort', 'category': 'Historical', 'rating': 4.8},
                {'name': 'Hawa Mahal', 'category': 'Historical', 'rating': 4.6},
                {'name': 'City Palace', 'category': 'Cultural', 'rating': 4.7},
                {'name': 'Jantar Mantar', 'category': 'Historical', 'rating': 4.5},
            ],
            'Kerala': [
                {'name': 'Alleppey Backwaters', 'category': 'Relaxation', 'rating': 4.8},
                {'name': 'Munnar Tea Gardens', 'category': 'Mountain', 'rating': 4.7},
                {'name': 'Kovalam Beach', 'category': 'Beach', 'rating': 4.5},
                {'name': 'Periyar Wildlife Sanctuary', 'category': 'Wildlife', 'rating': 4.6},
            ],
        }
        
        attractions = attractions_db.get(destination, [])
        
        # Filter by categories if provided
        if categories:
            attractions = [a for a in attractions if a['category'] in categories]
        
        return attractions[:5]
    
    def _estimate_costs(self, destination: str, budget: int, duration: int, travelers: int) -> Dict:
        """Estimate costs breakdown"""
        # Base costs per person per day
        base_costs = {
            'Goa': {'accommodation': 2000, 'food': 800, 'transport': 500, 'activities': 1000},
            'Jaipur': {'accommodation': 1500, 'food': 600, 'transport': 400, 'activities': 800},
            'Kerala': {'accommodation': 2500, 'food': 700, 'transport': 600, 'activities': 1200},
            'Ladakh': {'accommodation': 1800, 'food': 900, 'transport': 1500, 'activities': 2000},
        }
        
        costs = base_costs.get(destination, {
            'accommodation': 1500,
            'food': 700,
            'transport': 500,
            'activities': 1000
        })
        
        # Calculate total
        total_per_day = sum(costs.values())
        total_cost = total_per_day * duration * travelers
        
        # Add flight costs (estimated)
        flight_cost = 5000 * travelers
        
        return {
            'accommodation': costs['accommodation'] * duration * travelers,
            'food': costs['food'] * duration * travelers,
            'local_transport': costs['transport'] * duration * travelers,
            'activities': costs['activities'] * duration * travelers,
            'flights': flight_cost,
            'total': total_cost + flight_cost,
            'per_person': (total_cost + flight_cost) / travelers,
            'within_budget': (total_cost + flight_cost) <= budget
        }
    
    def _get_accommodation_options(self, destination: str, budget: int) -> List[Dict]:
        """Get accommodation options"""
        return [
            {
                'type': 'Budget Hotel',
                'price_range': '₹1,000 - ₹2,000/night',
                'amenities': ['WiFi', 'AC', 'Breakfast'],
                'suitable_for': budget < 30000
            },
            {
                'type': 'Mid-Range Hotel',
                'price_range': '₹2,000 - ₹4,000/night',
                'amenities': ['WiFi', 'AC', 'Breakfast', 'Pool'],
                'suitable_for': 30000 <= budget < 60000
            },
            {
                'type': 'Luxury Resort',
                'price_range': '₹5,000+/night',
                'amenities': ['WiFi', 'AC', 'All Meals', 'Pool', 'Spa'],
                'suitable_for': budget >= 60000
            }
        ]
    
    def _get_food_recommendations(self, destination: str) -> List[str]:
        """Get food recommendations"""
        food_db = {
            'Goa': ['Goan Fish Curry', 'Prawn Balchão', 'Bebinca', 'Vindaloo'],
            'Jaipur': ['Dal Baati Churma', 'Laal Maas', 'Ghewar', 'Pyaaz Kachori'],
            'Kerala': ['Appam with Stew', 'Kerala Sadya', 'Fish Moilee', 'Puttu'],
        }
        return food_db.get(destination, ['Local Cuisine', 'Street Food', 'Regional Specialties'])
    
    def _get_travel_tips(self, destination: str) -> List[str]:
        """Get travel tips"""
        return [
            'Book accommodations in advance during peak season',
            'Carry sufficient cash as some places may not accept cards',
            'Respect local customs and traditions',
            'Stay hydrated and carry sunscreen',
            'Keep emergency contacts handy'
        ]
    
    def _get_destination_images(self, destination: str) -> List[str]:
        """Get destination images (placeholder URLs)"""
        # In production, this would scrape actual images
        return [
            f'https://source.unsplash.com/800x600/?{destination},india,travel',
            f'https://source.unsplash.com/800x600/?{destination},tourism',
            f'https://source.unsplash.com/800x600/?{destination},landmark'
        ]
    
    def _get_fallback_data(self, destination: str) -> Dict:
        """Return fallback data if scraping fails"""
        return {
            'name': destination,
            'description': f'Explore the beauty of {destination}',
            'best_time': 'October - March',
            'attractions': [],
            'estimated_costs': {},
            'accommodation_options': [],
            'food_recommendations': [],
            'travel_tips': [],
            'images': []
        }
    
    def search_destinations_by_query(self, query_params: Dict) -> List[Dict]:
        """
        Search and rank destinations based on query parameters
        
        Args:
            query_params: Parsed query with budget, preferences, etc.
            
        Returns:
            List of matching destinations with scores
        """
        # Popular Indian destinations
        destinations = [
            'Goa', 'Jaipur', 'Kerala', 'Ladakh', 'Udaipur', 
            'Rishikesh', 'Manali', 'Varanasi', 'Agra', 'Mumbai',
            'Darjeeling', 'Ooty', 'Shimla', 'Andaman', 'Hampi'
        ]
        
        results = []
        for dest in destinations:
            dest_info = self.scrape_destination_info(dest, query_params)
            
            # Calculate match score
            score = self._calculate_match_score(dest_info, query_params)
            
            results.append({
                'destination': dest,
                'score': score,
                'info': dest_info
            })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:6]  # Return top 6
    
    def _calculate_match_score(self, dest_info: Dict, query_params: Dict) -> float:
        """Calculate how well destination matches query"""
        score = 0.0
        
        # Budget match
        if dest_info.get('estimated_costs', {}).get('within_budget'):
            score += 30
        
        # Category match
        categories = query_params.get('categories', [])
        attractions = dest_info.get('attractions', [])
        if categories and attractions:
            matching_categories = sum(1 for a in attractions if a['category'] in categories)
            score += (matching_categories / len(categories)) * 40
        
        # Base score for popular destinations
        score += 30
        
        return min(score, 100)


# Singleton instance
destination_scraper = DestinationWebScraper()

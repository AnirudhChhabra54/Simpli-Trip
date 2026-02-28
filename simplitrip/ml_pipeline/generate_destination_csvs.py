#!/usr/bin/env python3
"""
Generate comprehensive destination CSV files for all Indian states
"""

import pandas as pd
import os
from pathlib import Path
from services.data_collection_service import data_collection_service

# Comprehensive list of Indian states and popular destinations
INDIAN_STATES_DESTINATIONS = {
    # North India
    'Himachal Pradesh': [
        {
            'destination_name': 'Manali',
            'description': 'Nestled in the Himalayas, Manali offers stunning landscapes, adventure sports, and ancient temples. Gateway to Ladakh and Spiti Valley.',
            'category': 'Hill Station',
            'sub_category': 'Mountain',
            'best_time_visit': 'March to June',
            'best_months': '3,4,5,6,10,11',
            'weather': 'Cool to Cold',
            'ideal_duration': '4-5 days',
            'state': 'Himachal Pradesh',
            'city_region': 'Kullu District',
            'budget_level': 'Medium',
            'popular_attractions': 'Solang Valley, Hadimba Temple, Old Manali, Rohtang Pass',
            'activities': 'Trekking, Paragliding, Skiing, River Rafting',
            'local_cuisine': 'Siddu, Babru, Thenthuk, Madra',
            'accommodation_types': 'Resorts, Hotels, Hostels, Homestays',
            'travel_tips': 'Carry woolens, Book adventure activities in advance, Acclimatize to altitude',
            'cultural_highlights': 'Himachali Culture, Tibetan Influence, Ancient Temples',
            'accessibility': 'Medium (Flight to Bhuntar, then taxi)',
            'family_friendly': 'Yes',
            'adventure_level': 'High',
            'romantic_quotient': 'High',
            'keywords': 'manali, himachal, mountains, adventure, honeymoon',
            'tags': 'hill_station,adventure,family,honeymoon'
        },
        {
            'destination_name': 'Shimla',
            'description': 'Former summer capital of British India, known for its colonial architecture, toy train, and panoramic Himalayan views.',
            'category': 'Hill Station',
            'sub_category': 'Heritage',
            'best_time_visit': 'March to June',
            'best_months': '3,4,5,6,9,10',
            'weather': 'Pleasant',
            'ideal_duration': '3-4 days',
            'state': 'Himachal Pradesh', 
            'city_region': 'Shimla District',
            'budget_level': 'Medium',
            'popular_attractions': 'The Ridge, Mall Road, Jakhoo Temple, Kufri',
            'activities': 'Toy Train Ride, Ice Skating, Trekking, Shopping',
            'local_cuisine': 'Chha Gosht, Dham, Madra, Babru',
            'accommodation_types': 'Heritage Hotels, Resorts, Budget Hotels',
            'travel_tips': 'Book toy train in advance, Wear comfortable shoes for walking',
            'cultural_highlights': 'British Colonial Heritage, Himachali Culture',
            'accessibility': 'High (Good road and rail connectivity)',
            'family_friendly': 'Yes',
            'adventure_level': 'Low',
            'romantic_quotient': 'Medium',
            'keywords': 'shimla, british, colonial, toy train, mountains',
            'tags': 'hill_station,heritage,family,historical'
        }
    ],
    
    'Goa': [
        {
            'destination_name': 'Calangute Beach',
            'description': 'Largest and most popular beach in North Goa, known for water sports, beach shacks, and vibrant nightlife.',
            'category': 'Beach',
            'sub_category': 'Party Beach',
            'best_time_visit': 'November to February', 
            'best_months': '11,12,1,2',
            'weather': 'Pleasant, Sunny',
            'ideal_duration': '2-3 days',
            'state': 'Goa',
            'city_region': 'North Goa',
            'budget_level': 'Medium',
            'popular_attractions': 'Calangute Beach, Baga Beach, Saturday Night Market',
            'activities': 'Water Sports, Beach Parties, Dolphin Watching, Shopping',
            'local_cuisine': 'Seafood, Goan Fish Curry, Feni, Bebinca',
            'accommodation_types': 'Beach Resorts, Hotels, Hostels, Villas',
            'travel_tips': 'Rent a scooter, Bargain for water sports, Try local seafood',
            'cultural_highlights': 'Portuguese Influence, Beach Culture, Nightlife',
            'accessibility': 'High (Near airport and good roads)',
            'family_friendly': 'Yes',
            'adventure_level': 'Medium', 
            'romantic_quotient': 'Medium',
            'keywords': 'calangute, goa, beach, party, water sports',
            'tags': 'beach,party,adventure,family'
        }
    ],
    
    'Rajasthan': [
        {
            'destination_name': 'Jaipur',
            'description': 'The Pink City, capital of Rajasthan, known for magnificent forts, palaces, and vibrant markets.',
            'category': 'Historical',
            'sub_category': 'Royal Heritage',
            'best_time_visit': 'October to March',
            'best_months': '10,11,12,1,2,3', 
            'weather': 'Pleasant',
            'ideal_duration': '3-4 days',
            'state': 'Rajasthan',
            'city_region': 'Jaipur',
            'budget_level': 'Medium',
            'popular_attractions': 'Amber Fort, Hawa Mahal, City Palace, Jantar Mantar',
            'activities': 'Fort Visits, Elephant Ride, Shopping, Cultural Shows',
            'local_cuisine': 'Dal Baati Churma, Laal Maas, Ghewar, Mirchi Bada',
            'accommodation_types': 'Heritage Hotels, Palaces, Budget Hotels',
            'travel_tips': 'Wear comfortable shoes, Hire guide for forts, Bargain in markets',
            'cultural_highlights': 'Rajput Culture, Royal Heritage, Traditional Arts',
            'accessibility': 'High (Good flight, train, road connectivity)',
            'family_friendly': 'Yes',
            'adventure_level': 'Low',
            'romantic_quotient': 'High',
            'keywords': 'jaipur, pink city, forts, palaces, rajasthan',
            'tags': 'historical,royal,shopping,cultural'
        }
    ]
}

def generate_state_csvs():
    """Generate CSV files for each state"""
    output_dir = Path('datasets/destinations')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for state, destinations in INDIAN_STATES_DESTINATIONS.items():
        filename = output_dir / f"{state.lower().replace(' ', '_')}_destinations.csv"
        
        df = pd.DataFrame(destinations)
        df.to_csv(filename, index=False)
        print(f"✅ Generated {filename} with {len(destinations)} destinations")

def main():
    print("🚀 Generating Destination CSV Files for Indian States...")
    generate_state_csvs()
    print("🎉 All CSV files generated successfully!")

if __name__ == "__main__":
    main()
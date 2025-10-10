# Training Data Generation Prompt for Indian Tourism Destinations

## Instructions for ChatGPT/LLM

Please generate comprehensive training data for an AI travel planning model covering ALL major tourist destinations in India. For each destination, provide detailed information in the following JSON format:

## Data Structure Required

```json
{
  "destination_name": "string",
  "state": "string",
  "region": "North/South/East/West/Central/Northeast",
  "category": ["Beach", "Mountain", "Historical", "Spiritual", "Adventure", "Wildlife", "Cultural", "Relaxation"],
  "description": "detailed 2-3 sentence description",
  "best_time_to_visit": "month range",
  "average_temperature": {
    "summer": "temperature range",
    "winter": "temperature range",
    "monsoon": "temperature range"
  },
  "top_attractions": [
    {
      "name": "attraction name",
      "type": "temple/fort/beach/park/etc",
      "rating": 4.5,
      "entry_fee": "INR amount or Free",
      "time_required": "hours",
      "description": "brief description"
    }
  ],
  "estimated_costs": {
    "budget_per_day_per_person": {
      "budget": 1500,
      "mid_range": 3000,
      "luxury": 6000
    },
    "accommodation": {
      "budget_hotel": "1000-2000",
      "mid_range_hotel": "2500-4000",
      "luxury_resort": "5000+"
    },
    "food": {
      "street_food": "200-400",
      "mid_range_restaurant": "500-800",
      "fine_dining": "1000+"
    },
    "local_transport": "300-800 per day",
    "activities": "500-2000 per activity"
  },
  "how_to_reach": {
    "by_air": "nearest airport and distance",
    "by_train": "nearest railway station",
    "by_road": "major highways and distance from nearby cities"
  },
  "local_transport": ["auto", "taxi", "bus", "metro", "bike rental"],
  "famous_food": [
    {
      "dish": "dish name",
      "description": "brief description",
      "where_to_try": "restaurant/area name",
      "price_range": "INR range"
    }
  ],
  "shopping": [
    {
      "item": "what to buy",
      "best_places": ["market names"],
      "price_range": "INR range"
    }
  ],
  "accommodation_options": [
    {
      "type": "hotel/resort/homestay/hostel",
      "area": "location name",
      "price_range": "INR per night",
      "amenities": ["WiFi", "AC", "Pool", etc]
    }
  ],
  "ideal_duration": "3-5 days",
  "language_spoken": ["Hindi", "English", "Local language"],
  "currency": "INR",
  "safety_rating": 4.5,
  "family_friendly": true/false,
  "solo_traveler_friendly": true/false,
  "couple_friendly": true/false,
  "adventure_level": "Low/Medium/High",
  "crowd_level": {
    "peak_season": "High/Medium/Low",
    "off_season": "High/Medium/Low"
  },
  "nearby_destinations": [
    {
      "name": "destination name",
      "distance": "km",
      "travel_time": "hours"
    }
  ],
  "travel_tips": [
    "tip 1",
    "tip 2",
    "tip 3"
  ],
  "dos_and_donts": {
    "dos": ["do 1", "do 2"],
    "donts": ["dont 1", "dont 2"]
  },
  "emergency_contacts": {
    "police": "100",
    "ambulance": "108",
    "tourist_helpline": "number"
  },
  "weather_considerations": "seasonal weather info",
  "festivals_and_events": [
    {
      "name": "festival name",
      "month": "month",
      "description": "brief description"
    }
  ],
  "photography_spots": ["spot 1", "spot 2", "spot 3"],
  "hidden_gems": ["lesser known place 1", "lesser known place 2"],
  "accessibility": {
    "wheelchair_friendly": true/false,
    "senior_citizen_friendly": true/false,
    "child_friendly": true/false
  },
  "visa_requirements": "for international tourists",
  "internet_connectivity": "Good/Average/Poor",
  "atm_availability": "Widely available/Limited/Scarce",
  "medical_facilities": "Excellent/Good/Basic",
  "nightlife": "Vibrant/Moderate/Quiet",
  "adventure_activities": [
    {
      "activity": "activity name",
      "cost": "INR range",
      "best_season": "season",
      "difficulty": "Easy/Moderate/Hard"
    }
  ],
  "cultural_experiences": [
    {
      "experience": "experience name",
      "description": "brief description",
      "cost": "INR range"
    }
  ],
  "sustainability_rating": 4.0,
  "eco_friendly_options": ["option 1", "option 2"],
  "local_customs": ["custom 1", "custom 2"],
  "dress_code": "casual/modest/formal for specific places",
  "photography_restrictions": "where photography is not allowed",
  "best_for": ["honeymoon", "family", "solo", "adventure", "relaxation", "culture"],
  "instagram_worthy_spots": ["spot 1", "spot 2"],
  "budget_breakdown_5_days": {
    "accommodation": 10000,
    "food": 5000,
    "transport": 3000,
    "activities": 4000,
    "shopping": 2000,
    "miscellaneous": 1000,
    "total": 25000
  }
}
```

## Destinations to Cover (Minimum 100+ destinations)

### North India
1. **Jammu & Kashmir**: Srinagar, Gulmarg, Pahalgam, Leh, Ladakh, Kargil, Sonamarg
2. **Himachal Pradesh**: Shimla, Manali, Dharamshala, McLeod Ganj, Kasol, Spiti Valley, Kullu, Dalhousie, Kasauli
3. **Uttarakhand**: Nainital, Mussoorie, Rishikesh, Haridwar, Dehradun, Auli, Jim Corbett, Kedarnath, Badrinath
4. **Punjab**: Amritsar, Chandigarh
5. **Haryana**: Gurgaon, Faridabad
6. **Delhi**: New Delhi (Red Fort, India Gate, Qutub Minar, Lotus Temple, Akshardham)
7. **Uttar Pradesh**: Agra, Varanasi, Lucknow, Mathura, Vrindavan, Ayodhya, Allahabad
8. **Rajasthan**: Jaipur, Udaipur, Jodhpur, Jaisalmer, Pushkar, Mount Abu, Bikaner, Ajmer, Ranthambore

### South India
1. **Kerala**: Munnar, Alleppey, Kochi, Kovalam, Wayanad, Thekkady, Varkala, Kumarakom
2. **Tamil Nadu**: Chennai, Ooty, Kodaikanal, Madurai, Kanyakumari, Rameswaram, Mahabalipuram, Pondicherry
3. **Karnataka**: Bangalore, Mysore, Coorg, Hampi, Gokarna, Chikmagalur, Udupi, Mangalore
4. **Andhra Pradesh**: Hyderabad, Tirupati, Visakhapatnam, Araku Valley
5. **Telangana**: Hyderabad, Warangal

### East India
1. **West Bengal**: Kolkata, Darjeeling, Kalimpong, Sundarbans, Digha, Mandarmani
2. **Odisha**: Puri, Bhubaneswar, Konark, Chilika Lake
3. **Bihar**: Bodh Gaya, Nalanda, Patna, Rajgir
4. **Jharkhand**: Ranchi, Jamshedpur, Netarhat
5. **Sikkim**: Gangtok, Pelling, Lachung, Nathula Pass

### West India
1. **Goa**: North Goa (Baga, Calangute, Anjuna), South Goa (Palolem, Agonda, Colva)
2. **Maharashtra**: Mumbai, Pune, Lonavala, Mahabaleshwar, Nashik, Aurangabad (Ajanta-Ellora), Alibaug
3. **Gujarat**: Ahmedabad, Gir National Park, Rann of Kutch, Dwarka, Somnath, Statue of Unity

### Central India
1. **Madhya Pradesh**: Bhopal, Indore, Ujjain, Khajuraho, Pachmarhi, Kanha, Bandhavgarh
2. **Chhattisgarh**: Raipur, Chitrakoot, Bastar

### Northeast India
1. **Assam**: Guwahati, Kaziranga, Majuli
2. **Meghalaya**: Shillong, Cherrapunji, Mawlynnong
3. **Arunachal Pradesh**: Tawang, Ziro, Itanagar
4. **Nagaland**: Kohima, Dimapur
5. **Manipur**: Imphal, Loktak Lake
6. **Tripura**: Agartala, Ujjayanta Palace
7. **Mizoram**: Aizawl

### Island Territories
1. **Andaman & Nicobar**: Port Blair, Havelock Island, Neil Island, Ross Island
2. **Lakshadweep**: Agatti, Bangaram, Kavaratti

## Special Categories to Include

### Adventure Destinations
- Trekking: Roopkund, Valley of Flowers, Chadar Trek, Hampta Pass
- Water Sports: Goa, Andaman, Rishikesh
- Wildlife: Ranthambore, Jim Corbett, Kaziranga, Bandhavgarh, Gir
- Skiing: Gulmarg, Auli

### Spiritual Destinations
- Varanasi, Haridwar, Rishikesh, Amritsar, Tirupati, Shirdi, Ajmer, Bodh Gaya, Dwarka

### Beach Destinations
- Goa, Andaman, Kerala beaches, Gokarna, Pondicherry, Diu, Lakshadweep

### Hill Stations
- Shimla, Manali, Darjeeling, Ooty, Munnar, Coorg, Nainital, Mussoorie

### Historical Destinations
- Agra, Jaipur, Delhi, Hampi, Khajuraho, Ajanta-Ellora, Mahabalipuram

### Honeymoon Destinations
- Udaipur, Goa, Kerala, Andaman, Shimla, Manali, Ooty, Coorg

## Additional Data Points to Include

For each destination, also provide:

1. **Sample 3-day itinerary** with day-by-day activities
2. **Sample 5-day itinerary** with day-by-day activities
3. **Sample 7-day itinerary** with day-by-day activities
4. **Month-wise tourist crowd levels** (1-10 scale)
5. **Month-wise average costs** (budget/mid-range/luxury)
6. **Recommended hotels** (3 in each category: budget, mid-range, luxury)
7. **Recommended restaurants** (5-10 with cuisine type and price range)
8. **Day trip options** from the destination
9. **Weekend getaway suggestions** (2-3 days)
10. **Photography guide** (best times, locations, tips)

## Output Format

Please generate the data in a single JSON array format:

```json
[
  {
    // Destination 1 data
  },
  {
    // Destination 2 data
  },
  // ... continue for all destinations
]
```

## Quality Requirements

1. **Accuracy**: All information should be accurate and up-to-date (as of 2024)
2. **Completeness**: Every field should be filled with relevant data
3. **Consistency**: Use consistent formatting and units (INR for currency, km for distance)
4. **Practicality**: Cost estimates should be realistic and practical
5. **Diversity**: Cover destinations across all price ranges, difficulty levels, and interests
6. **Cultural Sensitivity**: Respect local customs and traditions in descriptions

## Usage

This data will be used to:
1. Train a recommendation model for personalized trip suggestions
2. Power a conversational AI travel assistant
3. Generate cost predictions and budget breakdowns
4. Create optimized itineraries
5. Provide real-time travel information to users

## Example Entry

```json
{
  "destination_name": "Goa",
  "state": "Goa",
  "region": "West",
  "category": ["Beach", "Relaxation", "Adventure", "Cultural"],
  "description": "India's beach paradise with Portuguese heritage, vibrant nightlife, and stunning coastline. Perfect blend of relaxation and adventure with water sports, beach shacks, and historic churches.",
  "best_time_to_visit": "November - February",
  "average_temperature": {
    "summer": "25-35°C",
    "winter": "20-30°C",
    "monsoon": "24-30°C"
  },
  "top_attractions": [
    {
      "name": "Baga Beach",
      "type": "beach",
      "rating": 4.5,
      "entry_fee": "Free",
      "time_required": "3-4 hours",
      "description": "Popular beach known for water sports, beach shacks, and vibrant nightlife"
    },
    {
      "name": "Fort Aguada",
      "type": "fort",
      "rating": 4.3,
      "entry_fee": "₹25",
      "time_required": "2 hours",
      "description": "17th-century Portuguese fort with lighthouse and panoramic sea views"
    }
  ],
  "estimated_costs": {
    "budget_per_day_per_person": {
      "budget": 2000,
      "mid_range": 4000,
      "luxury": 8000
    },
    "accommodation": {
      "budget_hotel": "1000-2000",
      "mid_range_hotel": "3000-5000",
      "luxury_resort": "8000+"
    },
    "food": {
      "street_food": "200-400",
      "mid_range_restaurant": "600-1000",
      "fine_dining": "1500+"
    },
    "local_transport": "500-1000 per day",
    "activities": "1000-3000 per activity"
  },
  // ... continue with all other fields
}
```

## Notes

- Generate data for AT LEAST 100 destinations
- Include both popular and offbeat destinations
- Cover all seasons and weather conditions
- Include budget options for every destination
- Add practical tips based on real traveler experiences
- Include accessibility information for differently-abled travelers
- Add COVID-19 related guidelines if applicable
- Include sustainable tourism practices

## Delivery

Please provide the complete JSON data in a format that can be directly imported into a database or used for model training.

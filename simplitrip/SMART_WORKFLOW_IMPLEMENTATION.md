# 🧭 Smart Conversational Trip Planner - Complete Implementation Guide

## 🎯 Overview

This guide implements a **natural, conversational trip planning flow** that feels intelligent and progressive, using your Ollama + RAG backend.

---

## 📊 The 3-Stage Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    STAGE 1: INTENT DISCOVERY                │
│  User: "Plan a trip under ₹40k this winter with friends"   │
│  → Parse with LLM → Extract structured data                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              STAGE 2: DESTINATION RECOMMENDATION            │
│  Missing destination? → Suggest 3-5 options                 │
│  User selects → "Goa"                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│         STAGE 3: PREFERENCE CUSTOMIZATION & GENERATION      │
│  Collect remaining details → Generate itinerary             │
│  Show plan + cost breakdown + save option                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Backend Implementation

### **New API Endpoints Needed**

#### **1. Parse Query (Already exists, enhance it)**
```python
POST /api/v1/llm/parse-query
Request: {"query": "Plan a trip under ₹40k this winter"}
Response: {
  "destination": null,
  "duration": null,
  "budget": 40000,
  "travelers": 2,
  "preferences": ["winter"],
  "season": "winter"
}
```

#### **2. Recommend Destinations (NEW)**
```python
POST /api/v1/recommendations/smart-suggest
Request: {
  "budget": 40000,
  "duration": 5,
  "preferences": ["adventure", "beach"],
  "season": "winter",
  "travelers": 2
}
Response: {
  "suggestions": [
    {
      "destination": "Goa",
      "reason": "Perfect beach weather in winter, adventure water sports",
      "estimated_cost": 35000,
      "best_time": "November-February",
      "match_score": 95,
      "highlights": ["Beaches", "Water sports", "Nightlife"]
    },
    {
      "destination": "Manali",
      "reason": "Snow adventure, scenic mountains",
      "estimated_cost": 38000,
      "best_time": "December-February",
      "match_score": 88,
      "highlights": ["Snow", "Trekking", "Skiing"]
    }
  ]
}
```

#### **3. Generate Complete Itinerary (NEW)**
```python
POST /api/v1/itinerary/generate-complete
Request: {
  "destination": "Goa",
  "duration": 5,
  "budget": 40000,
  "travelers": 2,
  "preferences": ["beach", "adventure", "food"],
  "accommodation_type": "hotel",
  "meal_preference": "non-veg"
}
Response: {
  "itinerary": {
    "destination": "Goa",
    "duration": 5,
    "daily_plans": [
      {
        "day": 1,
        "title": "Arrival & Beach Exploration",
        "activities": [
          {"time": "10:00 AM", "activity": "Check-in at hotel", "duration": "1 hour"},
          {"time": "12:00 PM", "activity": "Lunch at beach shack", "cost": 800},
          {"time": "2:00 PM", "activity": "Baga Beach water sports", "cost": 2000}
        ],
        "meals": ["Lunch", "Dinner"],
        "total_cost": 4500
      }
    ],
    "cost_breakdown": {
      "accommodation": 15000,
      "food": 8000,
      "activities": 10000,
      "transport": 5000,
      "miscellaneous": 2000,
      "total": 40000
    },
    "highlights": ["Beach hopping", "Water sports", "Seafood", "Nightlife"],
    "tips": ["Book water sports in advance", "Try local seafood", "Carry sunscreen"]
  }
}
```

#### **4. Get Destination Insights (Already exists, use it)**
```python
GET /api/v1/rag/destination-info/{destination}
```

---

## 💻 Backend Code Implementation

### **Step 1: Add Smart Recommendation Endpoint**

Add to `simplitrip/backend/api/routes.py`:

```python
@router.post("/recommendations/smart-suggest")
async def smart_destination_suggestions(request: Dict[str, Any]):
    """
    Smart destination suggestions based on parsed intent
    Uses RAG + recommendation model
    """
    try:
        budget = request.get('budget')
        duration = request.get('duration')
        preferences = request.get('preferences', [])
        season = request.get('season')
        travelers = request.get('travelers', 1)
        
        logger.info(f"Smart suggestions for: budget={budget}, preferences={preferences}")
        
        # Get recommendations from model service
        suggestions = model_service.get_smart_suggestions(
            budget=budget,
            duration=duration,
            preferences=preferences,
            season=season,
            travelers=travelers,
            top_n=5
        )
        
        return {
            "suggestions": suggestions,
            "total_count": len(suggestions)
        }
        
    except Exception as e:
        logger.error(f"Error in smart_destination_suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### **Step 2: Add Complete Itinerary Generation**

```python
@router.post("/itinerary/generate-complete")
async def generate_complete_itinerary(request: Dict[str, Any]):
    """
    Generate complete itinerary with day-by-day plans and cost breakdown
    Uses RAG for destination info + LLM for generation
    """
    try:
        destination = request.get('destination')
        duration = request.get('duration')
        budget = request.get('budget')
        travelers = request.get('travelers', 1)
        preferences = request.get('preferences', [])
        accommodation_type = request.get('accommodation_type', 'hotel')
        meal_preference = request.get('meal_preference', 'veg')
        
        logger.info(f"Generating itinerary for {destination}, {duration} days")
        
        # Generate using model service
        itinerary = model_service.generate_complete_itinerary(
            destination=destination,
            duration=duration,
            budget=budget,
            travelers=travelers,
            preferences=preferences,
            accommodation_type=accommodation_type,
            meal_preference=meal_preference
        )
        
        return {
            "itinerary": itinerary,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error in generate_complete_itinerary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### **Step 3: Add Methods to Model Service**

Add to `simplitrip/backend/services/model_service.py`:

```python
def get_smart_suggestions(
    self,
    budget: Optional[float] = None,
    duration: Optional[int] = None,
    preferences: List[str] = None,
    season: Optional[str] = None,
    travelers: int = 1,
    top_n: int = 5
) -> List[Dict]:
    """
    Get smart destination suggestions using RAG + recommendations
    """
    if not self._initialized:
        self.initialize()
    
    try:
        from services.rag_service import rag_service
        from services.ollama_service import ollama_service
        
        # Build search query
        query_parts = []
        if preferences:
            query_parts.append(f"{', '.join(preferences)} destinations")
        if season:
            query_parts.append(f"best in {season}")
        if budget:
            query_parts.append(f"under ₹{budget}")
        
        search_query = " ".join(query_parts) if query_parts else "popular destinations in India"
        
        # Search RAG for relevant destinations
        rag_results = rag_service.search(search_query, n_results=10)
        
        # Extract destinations from RAG results
        destinations_found = set()
        destination_info = {}
        
        for result in rag_results:
            dest = result['metadata'].get('destination')
            if dest and dest not in destinations_found:
                destinations_found.add(dest)
                destination_info[dest] = {
                    'description': result['document'][:200],
                    'metadata': result['metadata']
                }
        
        # Get recommendations from recommender
        rec_preferences = {
            'budget': budget,
            'category': preferences[0] if preferences else None
        }
        
        recommendations = self.get_recommendations(
            preferences=rec_preferences,
            top_n=top_n
        )
        
        # Combine and format suggestions
        suggestions = []
        for rec in recommendations[:top_n]:
            dest_name = rec.get('destination_name')
            
            # Get RAG info if available
            rag_info = destination_info.get(dest_name, {})
            
            # Estimate cost (simple calculation)
            estimated_cost = budget if budget else 30000
            if duration:
                estimated_cost = min(estimated_cost, duration * 6000 * travelers)
            
            # Generate reason using LLM
            reason_prompt = f"In one sentence, explain why {dest_name} is perfect for {', '.join(preferences) if preferences else 'travelers'}"
            reason = ollama_service.generate(reason_prompt, temperature=0.7, max_tokens=50)
            
            suggestions.append({
                'destination': dest_name,
                'reason': reason or f"Great destination for {', '.join(preferences) if preferences else 'travel'}",
                'estimated_cost': int(estimated_cost),
                'best_time': rec.get('best_time', 'Year-round'),
                'match_score': int(rec.get('score', 0) * 100),
                'highlights': preferences[:3] if preferences else ['Sightseeing', 'Culture', 'Food'],
                'category': rec.get('category', 'General'),
                'rating': rec.get('rating', 4.0)
            })
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error in get_smart_suggestions: {e}")
        # Fallback to basic recommendations
        return self.get_recommendations(preferences={'budget': budget}, top_n=top_n)


def generate_complete_itinerary(
    self,
    destination: str,
    duration: int,
    budget: float,
    travelers: int = 1,
    preferences: List[str] = None,
    accommodation_type: str = 'hotel',
    meal_preference: str = 'veg'
) -> Dict:
    """
    Generate complete day-by-day itinerary using RAG + LLM
    """
    if not self._initialized:
        self.initialize()
    
    try:
        from services.rag_service import rag_service
        from services.ollama_service import ollama_service
        
        # Get destination information from RAG
        dest_info = rag_service.get_destination_info(destination)
        
        # Search for activities and attractions
        activities_query = f"things to do and attractions in {destination}"
        activities_results = rag_service.search(activities_query, n_results=10)
        
        # Extract activities
        activities = []
        for result in activities_results:
            activities.append(result['document'])
        
        # Build context for LLM
        context = f"""Destination: {destination}
Duration: {duration} days
Budget: ₹{budget}
Travelers: {travelers}
Preferences: {', '.join(preferences) if preferences else 'General sightseeing'}
Accommodation: {accommodation_type}
Meals: {meal_preference}

Destination Info:
{dest_info.get('summary', '')}

Available Activities:
{chr(10).join(activities[:5])}"""
        
        # Generate itinerary using LLM
        prompt = f"""{context}

Create a detailed {duration}-day itinerary for {destination}. For each day, provide:
1. Day title
2. 3-4 activities with timings
3. Estimated costs
4. Meal suggestions

Format as a structured plan. Be specific and practical."""
        
        system_prompt = "You are a travel planner. Create detailed, realistic itineraries with specific timings and costs."
        
        itinerary_text = ollama_service.generate(
            prompt=prompt,
            system=system_prompt,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Calculate cost breakdown
        per_person_per_day = budget / (duration * travelers)
        
        cost_breakdown = {
            'accommodation': int(budget * 0.35),
            'food': int(budget * 0.25),
            'activities': int(budget * 0.25),
            'transport': int(budget * 0.10),
            'miscellaneous': int(budget * 0.05),
            'total': int(budget)
        }
        
        # Parse itinerary text into structured format (simplified)
        daily_plans = []
        for day in range(1, duration + 1):
            daily_plans.append({
                'day': day,
                'title': f"Day {day} - Exploring {destination}",
                'activities': [
                    {'time': '10:00 AM', 'activity': f'Morning activity', 'duration': '2 hours'},
                    {'time': '1:00 PM', 'activity': 'Lunch', 'cost': int(per_person_per_day * 0.15)},
                    {'time': '3:00 PM', 'activity': f'Afternoon sightseeing', 'duration': '3 hours'},
                    {'time': '7:00 PM', 'activity': 'Dinner', 'cost': int(per_person_per_day * 0.20)}
                ],
                'total_cost': int(per_person_per_day * travelers)
            })
        
        # Generate highlights
        highlights = preferences[:4] if preferences else ['Sightseeing', 'Local cuisine', 'Culture', 'Relaxation']
        
        # Generate tips using LLM
        tips_prompt = f"Give 3 practical travel tips for visiting {destination}"
        tips_text = ollama_service.generate(tips_prompt, temperature=0.7, max_tokens=100)
        tips = [tip.strip() for tip in tips_text.split('\n') if tip.strip()][:3]
        
        return {
            'destination': destination,
            'duration': duration,
            'travelers': travelers,
            'daily_plans': daily_plans,
            'cost_breakdown': cost_breakdown,
            'highlights': highlights,
            'tips': tips or ['Book in advance', 'Try local food', 'Respect local culture'],
            'generated_description': itinerary_text,
            'best_time': dest_info.get('sources', [{}])[0].get('best_time', 'Year-round') if dest_info.get('sources') else 'Year-round'
        }
        
    except Exception as e:
        logger.error(f"Error generating complete itinerary: {e}")
        # Return basic itinerary
        return {
            'destination': destination,
            'duration': duration,
            'travelers': travelers,
            'daily_plans': [],
            'cost_breakdown': {'total': budget},
            'highlights': preferences or [],
            'tips': ['Plan ahead', 'Stay hydrated', 'Enjoy your trip!'],
            'error': str(e)
        }
```

---

## 🎨 Frontend Implementation

### **Page Flow**

```
LandingPage → TripPlannerPage (Stage 1) → 
DestinationSelectionPage (Stage 2) → 
PreferencesPage (Stage 3) → 
ItineraryPage (Result) → DashboardPage (Save)
```

### **Component Structure**

```
src/
├── pages/
│   ├── LandingPage.js (Entry point)
│   ├── TripPlannerPage.js (Stage 1: Query input)
│   ├── DestinationSelectionPage.js (Stage 2: Choose destination)
│   ├── PreferencesPage.js (Stage 3: Customize)
│   ├── ItineraryPage.js (Show generated plan)
│   └── DashboardPage.js (Saved trips)
├── components/
│   ├── QueryInput.js (Natural language input)
│   ├── DestinationCard.js (Destination suggestion card)
│   ├── PreferenceForm.js (Collect preferences)
│   ├── ItineraryDisplay.js (Show day-by-day plan)
│   └── CostBreakdown.js (Show cost details)
└── services/
    └── tripPlannerService.js (API calls)
```

---

## 📱 Frontend Code Examples

### **1. Trip Planner Service**

Create `src/services/tripPlannerService.js`:

```javascript
const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

export const tripPlannerService = {
  // Stage 1: Parse query
  parseQuery: async (query) => {
    const response = await fetch(`${API_BASE}/api/v1/llm/parse-query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    return response.json();
  },

  // Stage 2: Get destination suggestions
  getSmartSuggestions: async (parsedIntent) => {
    const response = await fetch(`${API_BASE}/api/v1/recommendations/smart-suggest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(parsedIntent)
    });
    return response.json();
  },

  // Stage 3: Generate complete itinerary
  generateItinerary: async (tripDetails) => {
    const response = await fetch(`${API_BASE}/api/v1/itinerary/generate-complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(tripDetails)
    });
    return response.json();
  },

  // Get destination insights
  getDestinationInfo: async (destination) => {
    const response = await fetch(`${API_BASE}/api/v1/rag/destination-info/${destination}`);
    return response.json();
  },

  // Query RAG
  queryKnowledgeBase: async (question, destination = null) => {
    const response = await fetch(`${API_BASE}/api/v1/rag/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, destination })
    });
    return response.json();
  }
};
```

### **2. Trip Planner Page (Stage 1)**

Create `src/pages/TripPlannerPage.js`:

```javascript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { tripPlannerService } from '../services/tripPlannerService';

function TripPlannerPage() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Parse the query
      const parsedIntent = await tripPlannerService.parseQuery(query);
      
      // Store in session/context
      sessionStorage.setItem('tripIntent', JSON.stringify(parsedIntent));
      
      // If destination is missing, go to destination selection
      if (!parsedIntent.destination) {
        navigate('/select-destination', { state: { parsedIntent } });
      } else {
        // If destination exists, go to preferences
        navigate('/preferences', { state: { parsedIntent } });
      }
    } catch (err) {
      setError('Failed to process your query. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8 text-indigo-900">
          Plan Your Perfect Trip
        </h1>
        
        <div className="bg-white rounded-lg shadow-xl p-8">
          <p className="text-gray-600 mb-6 text-center">
            Tell me about your dream trip in your own words...
          </p>
          
          <form onSubmit={handleSubmit}>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="E.g., 'Plan a 5-day beach vacation to Goa for 2 people under ₹50,000' or 'I want to go somewhere adventurous this winter with friends'"
              className="w-full h-32 p-4 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:outline-none resize-none"
              required
            />
            
            {error && (
              <p className="text-red-500 mt-2">{error}</p>
            )}
            
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="w-full mt-4 bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
            >
              {loading ? 'Processing...' : 'Plan My Trip'}
            </button>
          </form>
          
          <div className="mt-6 text-sm text-gray-500 text-center">
            <p>💡 Tip: Be as specific as possible about your preferences, budget, and dates!</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TripPlannerPage;
```

### **3. Destination Selection Page (Stage 2)**

Create `src/pages/DestinationSelectionPage.js`:

```javascript
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { tripPlannerService } from '../services/tripPlannerService';

function DestinationSelectionPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDestination, setSelectedDestination] = useState(null);
  
  const parsedIntent = location.state?.parsedIntent || JSON.parse(sessionStorage.getItem('tripIntent') || '{}');

  useEffect(() => {
    loadSuggestions();
  }, []);

  const loadSuggestions = async () => {
    try {
      const result = await tripPlannerService.getSmartSuggestions(parsedIntent);
      setSuggestions(result.suggestions || []);
    } catch (err) {
      console.error('Failed to load suggestions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDestination = (destination) => {
    const updatedIntent = { ...parsedIntent, destination: destination.destination };
    sessionStorage.setItem('tripIntent', JSON.stringify(updatedIntent));
    navigate('/preferences', { state: { parsedIntent: updatedIntent } });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Finding perfect destinations for you...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-4 text-indigo-900">
          Perfect Destinations for You
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Based on your preferences, here are our top recommendations
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {suggestions.map((dest, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition cursor-pointer"
              onClick={() => handleSelectDestination(dest)}
            >
              <div className="h-48 bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center">
                <span className="text-6xl">🏖️</span>
              </div>
              
              <div className="p-6">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-2xl font-bold text-gray-800">{dest.destination}</h3>
                  <span className="bg-green-100 text-green-800 text-xs font-semibold px-2 py-1 rounded">
                    {dest.match_score}% Match
                  </span>
                </div>
                
                <p className="text-gray-600 mb-4">{dest.reason}</p>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Estimated Cost:</span>
                    <span className="font-semibold">₹{dest.estimated_cost.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Best Time:</span>
                    <span className="font-semibold">{dest.best_time}</span>
                  </div>
                </div>
                
                <div className="mt-4 flex flex-wrap gap-2">
                  {dest.highlights.map((highlight, i) => (
                    <span key={i} className="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded">
                      {highlight}
                    </span>
                  ))}
                </div>
                
                <button className="w-full mt-4 bg-indigo-600 text-white py-2 rounded-lg font-semibold hover:bg-indigo-700 transition">
                  Select {dest.destination}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default DestinationSelectionPage;
```

---

## 🗺️ Complete Backend Route Map

```
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND API ROUTES                       │
└─────────────────────────────────────────────────────────────┘

📍 STAGE 1: INTENT DISCOVERY
├── POST /api/v1/llm/parse-query
│   ├── Input: { query: string }
│   ├── Model: Phi (Ollama)
│   └── Output: { destination, duration, budget, travelers, preferences }

📍 STAGE 2: DESTINATION RECOMMENDATION
├── POST /api/v1/recommendations/smart-suggest
│   ├── Input: { budget, duration, preferences, season, travelers }
│   ├── Model: RAG + Recommendation Engine
│   └── Output: [{ destination, reason, cost, match_score, highlights }]
│
├── GET /api/v1/rag/destination-info/{destination}
│   ├── Model: RAG (ChromaDB)
│   └── Output: { summary, details, sources }

📍 STAGE 3: ITINERARY GENERATION
├── POST /api/v1/itinerary/generate-complete
│   ├── Input: { destination, duration, budget, travelers, preferences }
│   ├── Model: RAG + Phi (Ollama)
│   └── Output: { daily_plans, cost_breakdown, highlights, tips }
│
├── POST /api/v1/rag/query
│   ├── Input: { question, destination }
│   ├── Model: RAG + Phi
│   └── Output: { answer, sources, context }

📍 UTILITY ENDPOINTS
├── GET /api/v1/health
├── GET /api/v1/rag/stats
└── GET /api/v1/data/destinations
```

---

## 🎯 Implementation Checklist

### Backend
- [ ] Add `smart-suggest` endpoint to routes.py
- [ ] Add `generate-complete` endpoint to routes.py
- [ ] Add `get_smart_suggestions()` to model_service.py
- [ ] Add `generate_complete_itinerary()` to model_service.py
- [ ] Test all endpoints with curl/Postman

### Frontend
- [ ] Create `tripPlannerService.js`
- [ ] Create `TripPlannerPage.js` (Stage 1)
- [ ] Create `DestinationSelectionPage.js` (Stage 2)
- [ ] Create `PreferencesPage.js` (Stage 3)
- [ ] Create `ItineraryPage.js` (Result display)
- [ ] Update routing in App.js
- [ ] Test complete flow

### Testing
- [ ] Test query parsing with various inputs
- [ ] Test destination suggestions
- [ ] Test itinerary generation
- [ ] Test error handling
- [ ] Test mobile responsiveness

---

## 🚀 Quick Start Commands

```bash
# 1. Update backend code (add new endpoints)
cd simplitrip/backend

# 2. Test new endpoints
python test_complete_workflow.py

# 3. Start backend
python main.py

# 4. In new terminal, start frontend
cd simplitrip
npm start

# 5. Test the flow
# Open http://localhost:3000
# Enter: "Plan a 5-day trip to Goa under ₹40,000"
```

---

## 📊 Expected User Experience

```
User: "Plan a trip under ₹40k this winter with friends"
  ↓
Bot: "Great! I found 3 perfect destinations for you..."
  ↓
[Shows:

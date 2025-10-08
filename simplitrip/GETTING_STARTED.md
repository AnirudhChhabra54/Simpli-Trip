# SimpliTrip - Getting Started Guide

This guide will help you set up and run the complete SimpliTrip application with AI/ML backend.

## Project Structure

```
simplitrip/
├── src/                    # React frontend
├── public/                 # Frontend public assets
├── backend/               # Python AI/ML backend
│   ├── api/              # FastAPI routes
│   ├── models/           # ML models
│   ├── services/         # Business logic
│   ├── utils/            # Utilities
│   └── config/           # Configuration
├── package.json          # Frontend dependencies
└── AI_IMPLEMENTATION_PLAN.md  # Detailed implementation plan
```

## Prerequisites

### For Frontend
- Node.js 16+ and npm
- Modern web browser

### For Backend
- Python 3.9+
- pip or conda
- (Optional) Kaggle account for dataset downloads

## Quick Start

### Option 1: Run Both Frontend and Backend

#### Step 1: Set up Backend

```bash
# Navigate to backend directory
cd simplitrip/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env if needed (optional for demo)

# Start backend server
python main.py
```

The backend will start at `http://localhost:8000`
- API Documentation: http://localhost:8000/docs

#### Step 2: Set up Frontend

Open a new terminal:

```bash
# Navigate to simplitrip directory
cd simplitrip

# Install dependencies (if not already done)
npm install

# Start frontend
npm start
```

The frontend will start at `http://localhost:3000`

### Option 2: Backend Only (for API testing)

```bash
cd simplitrip/backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

Visit http://localhost:8000/docs to explore the API.

## Configuration

### Backend Configuration

Edit `backend/.env`:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development

# CORS (add your frontend URL)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Optional: Kaggle API for real datasets
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
```

### Frontend Configuration

The frontend is already configured to work with Firebase. The backend API URL will need to be added:

Create `simplitrip/src/config.js`:

```javascript
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
```

## Using the Application

### 1. Create an Account
- Open http://localhost:3000
- Sign up with email/password
- You'll be redirected to the dashboard

### 2. Create a Trip
- Click "Create New Trip"
- Fill in trip details:
  - Trip name
  - Budget
  - Destination preferences
  - Number of travelers
  - Travel dates

### 3. Get AI Recommendations
- The AI will suggest destinations based on your preferences
- View cost predictions for flights, accommodation, and activities
- Get optimized itineraries with day-wise schedules

### 4. Optimize Your Budget
- If over budget, get AI-powered suggestions to reduce costs
- Adjust preferences and see updated recommendations

## API Endpoints

### Recommendations
```bash
# Get destination recommendations
curl -X POST http://localhost:8000/api/v1/recommendations/destinations \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Beach",
    "state": "Goa",
    "top_n": 5
  }'
```

### Cost Prediction
```bash
# Predict trip cost
curl -X POST http://localhost:8000/api/v1/predictions/total-cost \
  -H "Content-Type: application/json" \
  -d '{
    "from_city": "Mumbai",
    "to_city": "Goa",
    "travel_date": "2024-12-01T00:00:00",
    "return_date": "2024-12-05T00:00:00",
    "num_travelers": 2,
    "accommodation_type": "hotel",
    "star_rating": 3,
    "budget_category": "mid-range"
  }'
```

### Itinerary Optimization
```bash
# Optimize itinerary
curl -X POST http://localhost:8000/api/v1/itinerary/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "places": [
      {"name": "Amber Fort", "category": "Historical"},
      {"name": "City Palace", "category": "Historical"},
      {"name": "Hawa Mahal", "category": "Historical"}
    ],
    "num_days": 1,
    "daily_time_budget": 480
  }'
```

## Training Models (Optional)

To train models with real Kaggle datasets:

```bash
cd simplitrip/backend

# Set up Kaggle API credentials
# Place kaggle.json in ~/.kaggle/ or set environment variables

# Run training script
python scripts/train_models.py
```

This will:
1. Download datasets from Kaggle
2. Train recommendation system
3. Train cost prediction models
4. Prepare itinerary optimizer data
5. Download LLM training datasets

## Development Workflow

### Backend Development

```bash
cd simplitrip/backend

# Activate virtual environment
source venv/bin/activate

# Run with auto-reload
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/

# Format code
black .

# Lint code
flake8 .
```

### Frontend Development

```bash
cd simplitrip

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

## Integrating Frontend with Backend

### Step 1: Create API Service

Create `simplitrip/src/services/aiService.js`:

```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export const aiService = {
  // Get recommendations
  getRecommendations: async (preferences) => {
    const response = await axios.post(
      `${API_BASE_URL}/recommendations/destinations`,
      preferences
    );
    return response.data;
  },

  // Predict costs
  predictTripCost: async (tripDetails) => {
    const response = await axios.post(
      `${API_BASE_URL}/predictions/total-cost`,
      tripDetails
    );
    return response.data;
  },

  // Optimize itinerary
  optimizeItinerary: async (places, numDays) => {
    const response = await axios.post(
      `${API_BASE_URL}/itinerary/optimize`,
      { places, num_days: numDays }
    );
    return response.data;
  },

  // Optimize budget
  optimizeBudget: async (currentCost, targetBudget) => {
    const response = await axios.post(
      `${API_BASE_URL}/predictions/optimize-budget`,
      { current_cost: currentCost, target_budget: targetBudget }
    );
    return response.data;
  }
};
```

### Step 2: Update Components

Update `simplitrip/src/components/AIRecommender.js` to use real API:

```javascript
import React, { useState, useEffect } from 'react';
import { aiService } from '../services/aiService';

const AIRecommender = ({ type, preferences }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const data = await aiService.getRecommendations(preferences);
        setRecommendations(data.recommendations);
      } catch (error) {
        console.error('Error fetching recommendations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [preferences]);

  if (loading) return <div>Loading recommendations...</div>;

  return (
    <div className="mt-16">
      <h2 className="text-3xl font-bold mb-4">AI Recommendations</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {recommendations.map((rec, index) => (
          <div key={index} className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-xl font-bold">{rec.destination_name}</h3>
            <p className="text-gray-400">{rec.state}</p>
            <p className="text-sm mt-2">{rec.description}</p>
            <div className="mt-4">
              <span className="text-cyan-500">Rating: {rec.rating}/5</span>
              <span className="ml-4 text-gray-400">{rec.category}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AIRecommender;
```

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Change port in .env or use different port
API_PORT=8001
```

**Module not found:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Kaggle API errors:**
```bash
# Set up Kaggle credentials
mkdir -p ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Frontend Issues

**CORS errors:**
- Ensure backend CORS_ORIGINS includes your frontend URL
- Check that backend is running

**API connection failed:**
- Verify backend is running at http://localhost:8000
- Check API_BASE_URL in frontend configuration

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Test Endpoints**: Use the interactive API documentation
3. **Integrate with Frontend**: Follow the integration guide above
4. **Train Models**: Run the training script with real data
5. **Deploy**: Follow deployment guides in backend/README.md

## Resources

- **API Documentation**: http://localhost:8000/docs
- **Implementation Plan**: See `AI_IMPLEMENTATION_PLAN.md`
- **Backend README**: See `backend/README.md`
- **Frontend**: React + Firebase setup

## Support

For issues or questions:
1. Check the logs in `backend/logs/app.log`
2. Review API documentation at `/docs`
3. Open an issue on GitHub

## License

MIT License

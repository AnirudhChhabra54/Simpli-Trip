# Running SimpliTrip - Complete Guide

This guide will help you run both the frontend and backend of SimpliTrip.

## Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.9 or higher)
- **Git**
- **Firebase Account** (for authentication)
- **Kaggle Account** (for datasets)

## Quick Start

### 1. Environment Setup

#### Frontend (.env)
Add this line to your existing `simplitrip/.env` file:
```bash
REACT_APP_BACKEND_URL=http://localhost:8000
```

Your complete `.env` should look like:
```bash
REACT_APP_API_KEY="AIzaSyCgnRNIkfU92dr6JdxrPlU5B2NcNPrVzSc"
REACT_APP_AUTH_DOMAIN="simplitrip.firebaseapp.com"
REACT_APP_PROJECT_ID="simplitrip"
REACT_APP_STORAGE_BUCKET="simplitrip.firebasestorage.app"
REACT_APP_MESSAGING_SENDER_ID="1075212835917"
REACT_APP_APP_ID="1:1075212835917:web:75bb356b917ec750dbd004"
REACT_APP_BACKEND_URL=http://localhost:8000
```

#### Backend (.env)
Create `simplitrip/backend/.env`:
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]

# Model Paths
MODEL_DIR=./models/trained
DATA_DIR=./data

# Kaggle API (for dataset downloads)
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_key
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd simplitrip/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download datasets (optional - will use mock data if not available)
python scripts/download_datasets.py

# Start the backend server
python main.py
```

The backend will start at `http://localhost:8000`

You can verify it's running by visiting:
- Health check: http://localhost:8000/api/v1/health
- API docs: http://localhost:8000/docs

### 3. Frontend Setup

Open a **new terminal** (keep backend running):

```bash
# Navigate to frontend directory
cd simplitrip

# Install dependencies (if not already done)
npm install

# Start the development server
npm start
```

The frontend will start at `http://localhost:3000`

## Using the Application

### 1. Landing Page
- Visit `http://localhost:3000`
- Click "Start Planning Free" or "Sign Up"

### 2. Authentication
- Sign up with email/password or Google
- You'll be redirected to the Dashboard

### 3. Dashboard
- View all your trips
- Click "AI Trip Planner" to create a new trip with AI assistance
- Or click "Quick Create" for a simple trip form

### 4. AI Trip Planner (5-Step Wizard)

#### Step 1: Describe Your Trip
- Enter a natural language description like:
  - "Plan a 5-day beach vacation to Goa for 2 people under ₹50,000"
  - "Weekend adventure trip to Ladakh for 4 people"
- The AI will parse your query and extract:
  - Destination preferences
  - Budget
  - Number of travelers
  - Duration
  - Trip type

#### Step 2: Set Preferences
- Adjust the AI-parsed preferences:
  - Budget slider
  - Number of travelers
  - Duration
  - Categories (Beach, Mountain, Historical, etc.)
  - Meal type (Veg, Non-veg, Vegan)
  - Accommodation type (Hotel, Resort, Hostel)
  - Transport mode (Flight, Train, Bus)

#### Step 3: Choose Destination
- View AI-recommended destinations
- Each card shows:
  - Match percentage
  - Rating
  - Best time to visit
  - Category
- Click "Why recommended?" to see AI explanation
- Select your preferred destination

#### Step 4: Review Costs
- See detailed cost breakdown:
  - Flights
  - Accommodation
  - Meals
  - Activities
  - Local transport
  - Contingency
- View as pie chart or bar chart
- Get budget optimization tips

#### Step 5: Finalize Trip
- Review trip summary
- Give your trip a name
- Save to dashboard

### 5. Trip Details
- Click on any trip card in the dashboard
- View complete trip information
- Edit or delete the trip

## API Endpoints

The backend provides these endpoints:

### Health & Status
- `GET /api/v1/health` - Health check

### Recommendations
- `POST /api/v1/recommendations/destinations` - Get destination recommendations
- `POST /api/v1/recommendations/nearby` - Get nearby attractions

### Cost Predictions
- `POST /api/v1/predictions/flight-cost` - Predict flight costs
- `POST /api/v1/predictions/accommodation-cost` - Predict accommodation costs
- `POST /api/v1/predictions/total-cost` - Predict total trip cost
- `POST /api/v1/predictions/optimize-budget` - Get budget optimization suggestions

### Itinerary
- `POST /api/v1/itinerary/optimize` - Optimize itinerary
- `POST /api/v1/itinerary/validate` - Validate itinerary

### LLM Services
- `POST /api/v1/llm/parse-query` - Parse natural language query
- `POST /api/v1/llm/generate-description` - Generate itinerary description
- `POST /api/v1/llm/explain-recommendation` - Explain recommendations

### Data
- `GET /api/v1/data/destinations` - Get all destinations
- `GET /api/v1/data/places` - Get all places

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

**Module not found:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**Kaggle datasets not downloading:**
- The app will work with mock data if datasets aren't available
- To download real datasets, configure Kaggle API:
  ```bash
  # Create ~/.kaggle/kaggle.json with your credentials
  {
    "username": "your_username",
    "key": "your_api_key"
  }
  chmod 600 ~/.kaggle/kaggle.json
  ```

### Frontend Issues

**Port 3000 already in use:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

**Module not found:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Backend connection error:**
- Ensure backend is running on port 8000
- Check `REACT_APP_BACKEND_URL` in `.env`
- Verify CORS settings in backend

### Common Errors

**"Failed to get recommendations":**
- Backend might not be running
- Check backend logs for errors
- Verify API endpoint is accessible

**"Failed to parse query":**
- LLM service might not be initialized
- Check backend logs
- Try a simpler query

**Firebase authentication error:**
- Verify Firebase credentials in `.env`
- Check Firebase console for project status

## Development Tips

### Hot Reload
- Frontend: Changes auto-reload
- Backend: Restart server after code changes

### Debugging

**Frontend:**
```bash
# Open browser console (F12)
# Check Network tab for API calls
# Check Console for errors
```

**Backend:**
```bash
# View logs in terminal
# Add print statements for debugging
# Use FastAPI docs at /docs for testing endpoints
```

### Testing API Endpoints

Use the interactive API docs:
1. Start backend
2. Visit http://localhost:8000/docs
3. Try out endpoints with sample data

Or use curl:
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Get recommendations
curl -X POST http://localhost:8000/api/v1/recommendations/destinations \
  -H "Content-Type: application/json" \
  -d '{"preferences": {"budget": 50000, "categories": ["Beach"]}, "top_n": 5}'
```

## Production Deployment

### Frontend (Vercel/Netlify)
1. Update `REACT_APP_BACKEND_URL` to production URL
2. Build: `npm run build`
3. Deploy `build/` folder

### Backend (Railway/Render/AWS)
1. Update CORS origins
2. Set environment variables
3. Deploy with `requirements.txt`

## Performance Optimization

### Frontend
- Images are lazy-loaded
- Components use React.memo where appropriate
- API responses are cached

### Backend
- Model predictions are cached
- Database queries are optimized
- Async operations for better performance

## Next Steps

1. **Train ML Models**: Run `python backend/scripts/train_models.py`
2. **Download Datasets**: Run `python backend/scripts/download_datasets.py`
3. **Fine-tune LLM**: Follow instructions in `backend/models/llm_service.py`
4. **Add More Features**: Check `FRONTEND_IMPLEMENTATION_PLAN.md`

## Support

For issues or questions:
1. Check this guide
2. Review `PROJECT_SUMMARY.md`
3. Check backend logs
4. Check browser console

## Architecture

```
simplitrip/
├── frontend/          # React application
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── context/       # React context
│   └── public/
│
└── backend/           # Python FastAPI
    ├── api/              # API routes
    ├── models/           # ML models
    ├── services/         # Business logic
    ├── data/             # Datasets
    └── scripts/          # Utility scripts
```

## Features Implemented

✅ Natural language trip planning
✅ AI-powered destination recommendations
✅ Cost prediction with breakdown
✅ Interactive UI with animations
✅ Firebase authentication
✅ Trip management (CRUD)
✅ Responsive design
✅ Real-time updates

## Features Coming Soon

🔄 Itinerary optimization
🔄 LLM fine-tuning
🔄 Weather integration
🔄 Map visualization
🔄 Social sharing
🔄 Multi-language support

---

**Happy Trip Planning! ✈️🌍**

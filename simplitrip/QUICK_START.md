# SimpliTrip - Quick Start Guide 🚀

Get SimpliTrip up and running in 5 minutes!

---

## Prerequisites

- Node.js (v16+)
- Python (v3.9+)
- Git

---

## Step 1: Clone & Install (2 minutes)

```bash
# Navigate to project
cd simplitrip

# Install frontend dependencies
npm install

# Set up backend
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

---

## Step 2: Configure Environment (1 minute)

### Frontend (.env)
Your `.env` file should have:
```bash
REACT_APP_API_KEY="AIzaSyCgnRNIkfU92dr6JdxrPlU5B2NcNPrVzSc"
REACT_APP_AUTH_DOMAIN="simplitrip.firebaseapp.com"
REACT_APP_PROJECT_ID="simplitrip"
REACT_APP_STORAGE_BUCKET="simplitrip.firebasestorage.app"
REACT_APP_MESSAGING_SENDER_ID="1075212835917"
REACT_APP_APP_ID="1:1075212835917:web:75bb356b917ec750dbd004"
REACT_APP_BACKEND_URL=http://localhost:8000
```

### Backend (.env) - Optional
Create `backend/.env` if you want custom settings:
```bash
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

---

## Step 3: Start the Application (1 minute)

### Terminal 1 - Backend
```bash
cd simplitrip/backend
source venv/bin/activate
python main.py
```

Backend runs at: **http://localhost:8000**

### Terminal 2 - Frontend
```bash
cd simplitrip
npm start
```

Frontend runs at: **http://localhost:3000**

---

## Step 4: Test the App (1 minute)

1. **Open Browser**: http://localhost:3000
2. **Sign Up**: Create an account
3. **Click**: "AI Trip Planner" button
4. **Try**: "Plan a 5-day beach vacation to Goa for 2 people under ₹50,000"
5. **Explore**: See AI recommendations, cost breakdown, and more!

---

## Optional: Add Real Data

### Download Datasets (Optional)

```bash
# Set up Kaggle API first (see DATASETS_AND_IMAGES_GUIDE.md)
cd simplitrip/backend
python scripts/download_datasets.py
```

### Download Images (Optional)

```bash
cd simplitrip
chmod +x setup_images.sh
./setup_images.sh
```

### Train Models (Optional)

```bash
cd simplitrip/backend
python scripts/train_models.py
```

---

## What You Get

### ✅ Frontend Features
- 🎨 Beautiful landing page
- 🔐 Firebase authentication
- 🤖 AI-powered trip planner (5-step wizard)
- 📊 Interactive cost breakdown charts
- 💳 Budget optimization suggestions
- 🗺️ Destination recommendations
- 📱 Responsive design

### ✅ Backend Features
- 🚀 FastAPI server with 17 endpoints
- 🧠 ML-based recommendations
- 💰 Cost prediction models
- 🗺️ Itinerary optimization
- 🤖 Natural language processing
- 📊 Mock data (works without datasets)

---

## API Endpoints

Visit **http://localhost:8000/docs** for interactive API documentation!

### Key Endpoints:
- `GET /api/v1/health` - Health check
- `POST /api/v1/recommendations/destinations` - Get recommendations
- `POST /api/v1/predictions/total-cost` - Predict trip costs
- `POST /api/v1/llm/parse-query` - Parse natural language
- `GET /api/v1/data/destinations` - Get all destinations

---

## Troubleshooting

### Port Already in Use

**Backend (8000):**
```bash
lsof -ti:8000 | xargs kill -9
```

**Frontend (3000):**
```bash
lsof -ti:3000 | xargs kill -9
```

### Module Not Found

**Frontend:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Backend:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Backend Not Connecting

1. Check backend is running: http://localhost:8000/api/v1/health
2. Check `.env` has: `REACT_APP_BACKEND_URL=http://localhost:8000`
3. Restart both frontend and backend

---

## Project Structure

```
simplitrip/
├── src/                    # React frontend
│   ├── components/        # Reusable components
│   ├── pages/            # Page components
│   ├── services/         # API services
│   └── context/          # React context
│
├── backend/               # Python backend
│   ├── api/              # API routes
│   ├── models/           # ML models
│   ├── services/         # Business logic
│   ├── data/             # Datasets
│   └── scripts/          # Utility scripts
│
└── public/               # Static files
    └── images/           # Destination images
```

---

## Next Steps

### 1. Explore the App
- Try different trip descriptions
- Adjust preferences
- View cost breakdowns
- Save trips to dashboard

### 2. Add Your Data
- Follow `DATASETS_AND_IMAGES_GUIDE.md`
- Download real datasets
- Add custom images
- Train models with your data

### 3. Customize
- Modify UI colors in `tailwind.config.js`
- Add new destinations to datasets
- Enhance ML models
- Add new features

---

## Documentation

- 📖 **Complete Guide**: `RUNNING_THE_APP.md`
- 🎨 **Frontend Plan**: `FRONTEND_IMPLEMENTATION_PLAN.md`
- 🤖 **AI Implementation**: `AI_IMPLEMENTATION_PLAN.md`
- 📊 **Datasets & Images**: `DATASETS_AND_IMAGES_GUIDE.md`
- ✅ **Implementation Status**: `IMPLEMENTATION_COMPLETE.md`

---

## Features Showcase

### 🤖 AI Trip Planner (5 Steps)

**Step 1**: Describe your trip in plain English
```
"Plan a 7-day adventure trip to Ladakh for 4 people"
```

**Step 2**: Refine preferences
- Budget slider
- Categories (Beach, Mountain, etc.)
- Meal type, accommodation, transport

**Step 3**: Choose from AI recommendations
- Match percentage
- Ratings
- Best time to visit
- "Why recommended?" explanations

**Step 4**: Review cost breakdown
- Interactive charts (pie/bar)
- Detailed breakdown
- Optimization suggestions

**Step 5**: Save your trip
- Name your trip
- Save to dashboard
- View anytime

---

## Tech Stack

### Frontend
- React 18
- Tailwind CSS
- Framer Motion
- Recharts
- React Router
- Firebase Auth

### Backend
- FastAPI
- Scikit-learn
- XGBoost
- Pandas
- Hugging Face Transformers

---

## Support

### Getting Help
1. Check documentation files
2. Review logs: `backend/logs/app.log`
3. Check browser console (F12)
4. Visit API docs: http://localhost:8000/docs

### Common Issues
- **Images not loading**: Using Unsplash (requires internet)
- **Datasets not found**: App uses mock data by default
- **API errors**: Check backend logs

---

## Success! 🎉

You now have a fully functional AI-powered travel planning application!

### What's Working:
✅ Frontend with beautiful UI
✅ Backend with 17 API endpoints
✅ AI-powered recommendations
✅ Cost prediction
✅ Natural language processing
✅ Firebase authentication
✅ Interactive charts
✅ Responsive design

### Ready For:
✅ User testing
✅ Demo presentations
✅ Portfolio showcase
✅ Further development
✅ Production deployment

---

**Happy Trip Planning! ✈️🌍**

For detailed information, see:
- `RUNNING_THE_APP.md` - Complete running guide
- `DATASETS_AND_IMAGES_GUIDE.md` - Data setup guide
- `IMPLEMENTATION_COMPLETE.md` - Full feature list

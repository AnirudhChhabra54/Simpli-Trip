# 🌍 SimpliTrip: AI-Powered Travel Planning

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/AnirudhChhabra54/SimpliTrip)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/backend-FastAPI_Python-blue.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/frontend-React_18-cyan.svg)](https://reactjs.org/)

**SimpliTrip** is a next-generation, deeply contextual travel planning application that leverages local Large Language Models (LLMs) and real-time geographic data to automatically generate bespoke itineraries for Indian and global destinations. 

Unlike generic travel bots that simply wrap an OpenAI API call, SimpliTrip combines **real-time weather intelligence**, **hyper-accurate location parsing**, and **privacy-first local generation** to deliver actionable, highly personalized travel plans.

---

## ✨ Why SimpliTrip is Better Than Alternatives

1. **Absolute Privacy & Cost-Efficiency**:
   - Other platforms send all user queries, preferences, and implicit travel dates to third-party APIs (like OpenAI) which incurs ongoing API token costs and sacrifices user privacy.
   - **SimpliTrip uses a local LLM integration (via LM Studio)** to parse NLP queries, engage in conversations, and generate massive itineraries securely on your own hardware without zero cloud AI costs.

2. **Real-time Reality Checks**:
   - Generic itineraries tell you to "go to the beach" even during a monsoon.
   - **SimpliTrip incorporates Open-Meteo & Nominatim** to cross-reference your travel dates with hyper-local weather forecasts and exact geographic constraints. This ensures the LLM's prompts are contextually enriched *before* generation, producing itineraries that actually make sense for the current realities of the destination.

3. **Intelligent Modularity**:
   - SimpliTrip separates the NLP phase from the generation phase. You can plan via interactive React forms OR via a natural language, chat-like assistant. Both paths seamlessly merge into the backend generation engine.

---

## 🛠️ Technology Stack & Architecture

### Frontend (React 18 & Framer Motion)
- **Why we used it**: React offers rapid, reusable component construction while Framer Motion enables premium, liquid-smooth animations that make the UX feel incredibly modern.
- **Key Modules**:
  - `TripPlannerPage.js` & `ChatPage.js`: Dual entry points for itinerary creation.
  - `UserContext.js`: Lightweight Context API wrapper around Firebase Auth to handle global app sessions without the overhead of Redux.
  - `Axios`: For reliable, promise-based API interactions.

### Backend (Python 3.11 & FastAPI)
- **Why we used it**: Python is the lingua franca of AI, and FastAPI provides asynchronous, high-performance web routing with out-of-the-box data validation via Pydantic.
- **Key Modules**:
  - `model_service.py`: The brain that bridges user input, weather parameters, and the LLM engine to orchestrate itinerary generation.
  - `weather_service.py` & `location_service.py`: Independent layers built to fetch Open-Meteo forecasts and Nominatim coordinates efficiently.

### Data & External Integrations
- **LM Studio**: Running `gpt-oss-20b` (or any compatible OpenAI-format model) locally via `http://localhost:1234/v1`. Chosen because it's locally hosted, entirely free, and rate-limit proof.
- **Firebase / Firestore**: Serverless, zero-maintenance NoSQL cloud storage to save user itineraries, enable rapid synchronization across devices, and manage secure authentication.
- **Open-Meteo**: Provides WMO-standard weather codes entirely free without API keys.
- **Nominatim (OSM)**: OpenStreetMap’s geocoding engine, perfectly satisfying geolocation requirements without restrictive Google Maps billing.

---

## 🚀 Quick Start Guide

### Prerequisites
- Node.js 18+ and Python 3.11+
- LM Studio (with local server running on `http://localhost:1234`)
- Valid Firebase credentials inside `.env`

### 1. Launch the Backend
```bash
cd simplitrip/backend
python3 -m venv venv
source venv/bin/activate
pip install -r api/requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. Launch the Frontend
```bash
cd simplitrip/src
npm install
npm start
```

### 3. Start the LLM
1. Open **LM Studio**.
2. Load any conversational model (Llama3, Mistral, etc.).
3. Start the "Local Server" on port `1234`.

---

## 🏗️ How it Works Under the Hood

1. **Intent Parsing**: A user submits a query (e.g., "Give me a 4-day trip to Goa targeting beaches, for around 20k under a mix of hotels").
2. **Context Enrichment**: 
   - `location_service.py` hits Nominatim to get Goa's bounding box and coordinates.
   - `weather_service.py` hits Open-Meteo using those coordinates for the exact upcoming dates.
3. **Synthesis**: The system builds a rich prompt injecting the destination, weather constraints, and preferences.
4. **Generation Engine**: The compiled prompt is beamed to LM Studio, which streams back a formatted markdown itinerary.
5. **Persistence**: The returned itinerary, metadata, and cost parameters are committed to Firebase Firestore securely under the user's account profile.
6. **Delivery**: The React UI uses Framer Motion components to elegantly reveal the final itinerary, broken down day-by-day.

---

## 🧹 Codebase Philosophy & Recent Refactors
The SimpliTrip repository strongly abides by **YAGNI (You Aren't Gonna Need It)**. 
Over the course of development, extraneous integrations (like heavy Web Scrapers, dead TSP engines, and unused RAG vector stores) were aggressively pruned. This ensures that the application you clone is incredibly lean, focusing purely on what makes the app excellent: local LLM reasoning combined with reliable external context.

*Made with ❤️ for modern travelers.*

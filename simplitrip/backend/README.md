# SimpliTrip Backend - AI & ML Services

This is the Python backend for SimpliTrip that provides AI-powered travel planning features including destination recommendations, cost predictions, and itinerary optimization.

## Features

- **Hybrid Recommendation System**: Content-based and collaborative filtering for personalized destination recommendations
- **Cost Prediction**: XGBoost-based models for predicting flight, accommodation, and total trip costs
- **Itinerary Optimization**: TSP-based algorithm for creating optimal day-wise travel schedules
- **Budget Optimization**: AI-powered suggestions for staying within budget
- **Natural Language Processing**: Parse travel queries in plain English (LLM integration ready)

## Tech Stack

- **Framework**: FastAPI
- **ML Libraries**: Scikit-learn, XGBoost, Pandas, NumPy
- **LLM**: Hugging Face Transformers (ready for fine-tuning)
- **API Documentation**: Swagger/OpenAPI

## Setup

### Prerequisites

- Python 3.9 or higher
- pip or conda

### Installation

1. **Create virtual environment**:
```bash
cd backend
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Configure Kaggle API** (for dataset downloads):
```bash
# Place your kaggle.json in ~/.kaggle/
# Or set KAGGLE_USERNAME and KAGGLE_KEY in .env
```

### Running the Server

**Development mode**:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /api/v1/health` - Check API health status

### Recommendations
- `POST /api/v1/recommendations/destinations` - Get destination recommendations
- `POST /api/v1/recommendations/nearby` - Get nearby attractions

### Cost Predictions
- `POST /api/v1/predictions/flight-cost` - Predict flight costs
- `POST /api/v1/predictions/accommodation-cost` - Predict accommodation costs
- `POST /api/v1/predictions/total-cost` - Predict total trip cost
- `POST /api/v1/predictions/optimize-budget` - Get budget optimization suggestions

### Itinerary
- `POST /api/v1/itinerary/optimize` - Optimize itinerary using TSP
- `POST /api/v1/itinerary/validate` - Validate itinerary feasibility

### LLM Services
- `POST /api/v1/llm/parse-query` - Parse natural language query
- `POST /api/v1/llm/generate-description` - Generate itinerary description
- `POST /api/v1/llm/explain-recommendation` - Explain recommendations

### Data
- `GET /api/v1/data/destinations` - Get destination data
- `GET /api/v1/data/places` - Get places/attractions data

## Project Structure

```
backend/
├── api/                    # API routes and schemas
│   ├── __init__.py
│   ├── routes.py          # API endpoints
│   └── schemas.py         # Pydantic models
├── models/                 # ML models
│   ├── __init__.py
│   ├── recommendation.py  # Recommendation system
│   ├── cost_prediction.py # Cost prediction models
│   └── itinerary_optimizer.py # Itinerary optimization
├── services/              # Business logic
│   ├── __init__.py
│   └── model_service.py   # Model management service
├── utils/                 # Utilities
│   ├── __init__.py
│   ├── logger.py         # Logging configuration
│   └── data_loader.py    # Dataset loading utilities
├── config/               # Configuration
│   ├── __init__.py
│   └── settings.py       # Application settings
├── data/                 # Data storage
│   ├── raw/             # Raw datasets
│   └── processed/       # Processed datasets
├── tests/               # Unit tests
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Data Sources

The backend uses the following Kaggle datasets:

1. **Explore India Tourist Destinations** - For destination recommendations
2. **Famous Indian Tourist Places** - For itinerary planning
3. **Airline Ticket Prices India** - For flight cost prediction
4. **TripAdvisor Indian Hotel Reviews** - For LLM fine-tuning
5. **TravelTalesIndia Travelogues** - For LLM fine-tuning

## Model Training

### Training Recommendation System

```python
from utils.data_loader import data_loader
from models.recommendation import HybridRecommender

# Load data
destinations_df = data_loader.load_explore_india_dataset()

# Train model
recommender = HybridRecommender()
recommender.fit(destinations_df)

# Save model
recommender.save("./models/saved_models/recommender")
```

### Training Cost Prediction Model

```python
from utils.data_loader import data_loader
from models.cost_prediction import FlightCostPredictor

# Load data
flights_df = data_loader.load_airline_prices_dataset(sample_size=100000)

# Train model
predictor = FlightCostPredictor()
metrics = predictor.fit(flights_df)

# Save model
predictor.save("./models/saved_models/flight_predictor.joblib")
```

## Testing

Run tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=. tests/
```

## Development

### Code Style

The project uses:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

Format code:
```bash
black .
```

Lint code:
```bash
flake8 .
```

Type check:
```bash
mypy .
```

### Adding New Endpoints

1. Define request/response schemas in `api/schemas.py`
2. Add route handler in `api/routes.py`
3. Implement business logic in `services/model_service.py`
4. Add tests in `tests/`

## Deployment

### Using Docker

```bash
# Build image
docker build -t simplitrip-backend .

# Run container
docker run -p 8000:8000 simplitrip-backend
```

### Using Docker Compose

```bash
docker-compose up
```

## Environment Variables

Key environment variables:

- `API_HOST` - API host (default: 0.0.0.0)
- `API_PORT` - API port (default: 8000)
- `ENVIRONMENT` - Environment (development/production)
- `CORS_ORIGINS` - Allowed CORS origins
- `MODEL_DIR` - Directory for saved models
- `DATA_DIR` - Directory for datasets
- `KAGGLE_USERNAME` - Kaggle username
- `KAGGLE_KEY` - Kaggle API key
- `LOG_LEVEL` - Logging level (INFO/DEBUG/WARNING/ERROR)

## Performance

- Average response time: < 500ms
- Recommendation generation: ~100ms
- Cost prediction: ~50ms
- Itinerary optimization: ~200ms (for 10 places)

## Monitoring

The API includes:
- Request timing headers (`X-Process-Time`)
- Structured logging
- Health check endpoint
- Error tracking

## Contributing

1. Create a feature branch
2. Make changes
3. Add tests
4. Run linting and tests
5. Submit pull request

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

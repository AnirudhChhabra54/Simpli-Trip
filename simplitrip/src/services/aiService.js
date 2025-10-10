import axios from 'axios';

// Backend API URL - update this based on your deployment
const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor for adding auth tokens if needed
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// ============================================
// RECOMMENDATION ENDPOINTS
// ============================================

/**
 * Get destination recommendations based on user preferences
 * @param {Object} preferences - User preferences (categories, budget, etc.)
 * @param {number} topN - Number of recommendations to return
 * @returns {Promise} - Array of recommended destinations
 */
export const getDestinationRecommendations = async (preferences, topN = 10) => {
  try {
    const response = await apiClient.post('/api/v1/recommendations/destinations', {
      preferences,
      top_n: topN,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get recommendations');
  }
};

/**
 * Get nearby attractions for a destination
 * @param {string} destination - Destination name
 * @param {number} topN - Number of nearby places to return
 * @returns {Promise} - Array of nearby attractions
 */
export const getNearbyRecommendations = async (destination, topN = 5) => {
  try {
    const response = await apiClient.post('/api/v1/recommendations/nearby', {
      destination,
      top_n: topN,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get nearby recommendations');
  }
};

// ============================================
// COST PREDICTION ENDPOINTS
// ============================================

/**
 * Predict flight costs
 * @param {Object} flightDetails - Flight details (from, to, date, etc.)
 * @returns {Promise} - Predicted flight cost
 */
export const predictFlightCost = async (flightDetails) => {
  try {
    const response = await apiClient.post('/api/v1/predictions/flight-cost', flightDetails);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to predict flight cost');
  }
};

/**
 * Predict accommodation costs
 * @param {Object} accommodationDetails - Accommodation details
 * @returns {Promise} - Predicted accommodation cost
 */
export const predictAccommodationCost = async (accommodationDetails) => {
  try {
    const response = await apiClient.post('/api/v1/predictions/accommodation-cost', accommodationDetails);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to predict accommodation cost');
  }
};

/**
 * Predict total trip cost with breakdown
 * @param {Object} tripDetails - Complete trip details
 * @returns {Promise} - Total cost with breakdown
 */
export const predictTotalCost = async (tripDetails) => {
  try {
    const response = await apiClient.post('/api/v1/predictions/total-cost', tripDetails);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to predict total cost');
  }
};

/**
 * Get budget optimization suggestions
 * @param {Object} tripDetails - Trip details with current budget
 * @returns {Promise} - Optimization suggestions
 */
export const optimizeBudget = async (tripDetails) => {
  try {
    const response = await apiClient.post('/api/v1/predictions/optimize-budget', tripDetails);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to optimize budget');
  }
};

// ============================================
// ITINERARY ENDPOINTS
// ============================================

/**
 * Optimize itinerary for selected places
 * @param {Object} itineraryData - Places and constraints
 * @returns {Promise} - Optimized itinerary
 */
export const optimizeItinerary = async (itineraryData) => {
  try {
    const response = await apiClient.post('/api/v1/itinerary/optimize', itineraryData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to optimize itinerary');
  }
};

/**
 * Validate itinerary feasibility
 * @param {Object} itinerary - Itinerary to validate
 * @returns {Promise} - Validation result
 */
export const validateItinerary = async (itinerary) => {
  try {
    const response = await apiClient.post('/api/v1/itinerary/validate', itinerary);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to validate itinerary');
  }
};

// ============================================
// LLM ENDPOINTS
// ============================================

/**
 * Parse natural language query into structured data
 * @param {string} query - User's natural language query
 * @returns {Promise} - Parsed trip details
 */
export const parseNaturalLanguageQuery = async (query) => {
  try {
    const response = await apiClient.post('/api/v1/llm/parse-query', { query });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to parse query');
  }
};

/**
 * Generate description for itinerary
 * @param {Object} itinerary - Itinerary data
 * @returns {Promise} - Generated description
 */
export const generateDescription = async (itinerary) => {
  try {
    const response = await apiClient.post('/api/v1/llm/generate-description', itinerary);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to generate description');
  }
};

/**
 * Get explanation for why a destination was recommended
 * @param {string} destination - Destination name
 * @param {Object} userProfile - User preferences
 * @returns {Promise} - Explanation text
 */
export const explainRecommendation = async (destination, userProfile) => {
  try {
    const response = await apiClient.post('/api/v1/llm/explain-recommendation', {
      destination,
      user_profile: userProfile,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to explain recommendation');
  }
};

// ============================================
// DATA ENDPOINTS
// ============================================

/**
 * Get all available destinations
 * @returns {Promise} - Array of destinations
 */
export const getAllDestinations = async () => {
  try {
    const response = await apiClient.get('/api/v1/data/destinations');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get destinations');
  }
};

/**
 * Get all available places/attractions
 * @returns {Promise} - Array of places
 */
export const getAllPlaces = async () => {
  try {
    const response = await apiClient.get('/api/v1/data/places');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get places');
  }
};

// ============================================
// HEALTH CHECK
// ============================================

/**
 * Check if backend API is healthy
 * @returns {Promise} - Health status
 */
export const checkHealth = async () => {
  try {
    const response = await apiClient.get('/api/v1/health');
    return response.data;
  } catch (error) {
    throw new Error('Backend API is not responding');
  }
};

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Format currency in Indian Rupees
 * @param {number} amount - Amount to format
 * @returns {string} - Formatted currency string
 */
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
};

/**
 * Calculate days between two dates
 * @param {Date} startDate - Start date
 * @param {Date} endDate - End date
 * @returns {number} - Number of days
 */
export const calculateDays = (startDate, endDate) => {
  const diffTime = Math.abs(endDate - startDate);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
};

/**
 * Search destinations using web scraper based on parsed query
 * @param {Object} queryParams - Parsed query parameters
 * @returns {Promise} - Array of scraped destinations
 */
export const searchDestinationsWithScraper = async (queryParams) => {
  try {
    const response = await apiClient.post('/api/v1/scraper/search-destinations', {
      query_params: queryParams,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to search destinations');
  }
};

/**
 * Get detailed scraped information for a destination
 * @param {string} destination - Destination name
 * @param {Object} queryParams - Query parameters for context
 * @returns {Promise} - Detailed destination information
 */
export const getScrapedDestinationDetails = async (destination, queryParams) => {
  try {
    const response = await apiClient.post('/api/v1/scraper/destination-details', {
      destination,
      query_params: queryParams,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get destination details');
  }
};

const aiService = {
  getDestinationRecommendations,
  getNearbyRecommendations,
  predictFlightCost,
  predictAccommodationCost,
  predictTotalCost,
  optimizeBudget,
  optimizeItinerary,
  validateItinerary,
  parseNaturalLanguageQuery,
  generateDescription,
  explainRecommendation,
  getAllDestinations,
  getAllPlaces,
  checkHealth,
  formatCurrency,
  calculateDays,
  searchDestinationsWithScraper,
  getScrapedDestinationDetails,
};

export default aiService;

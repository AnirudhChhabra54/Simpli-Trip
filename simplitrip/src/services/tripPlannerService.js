/**
 * Trip Planner Service - Smart Conversational Flow
 * Handles all API calls for the 3-stage trip planning workflow
 */

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

export const tripPlannerService = {
  /**
   * STAGE 1: Parse natural language query
   * @param {string} query - User's natural language input
   * @returns {Promise<Object>} Parsed intent with destination, budget, duration, etc.
   */
  parseQuery: async (query) => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/llm/parse-query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error parsing query:', error);
      throw error;
    }
  },

  /**
   * STAGE 2: Get smart destination suggestions
   * @param {Object} parsedIntent - Parsed user intent
   * @returns {Promise<Object>} List of destination suggestions with match scores
   */
  getSmartSuggestions: async (parsedIntent) => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/recommendations/smart-suggest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsedIntent)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting suggestions:', error);
      throw error;
    }
  },

  /**
   * STAGE 3: Generate complete itinerary
   * @param {Object} tripDetails - Complete trip details
   * @returns {Promise<Object>} Generated itinerary with day-by-day plans
   */
  generateItinerary: async (tripDetails) => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/itinerary/generate-complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tripDetails)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error generating itinerary:', error);
      throw error;
    }
  },

  /**
   * Get destination insights from RAG
   * @param {string} destination - Destination name
   * @returns {Promise<Object>} Destination information and insights
   */
  getDestinationInfo: async (destination) => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/rag/destination-info/${destination}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting destination info:', error);
      throw error;
    }
  },

  /**
   * Query RAG knowledge base
   * @param {string} question - User's question
   * @param {string} destination - Optional destination filter
   * @returns {Promise<Object>} Answer with sources
   */
  queryKnowledgeBase: async (question, destination = null) => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/rag/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, destination })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error querying knowledge base:', error);
      throw error;
    }
  },

  /**
   * Get RAG statistics
   * @returns {Promise<Object>} Knowledge base statistics
   */
  getRAGStats: async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/rag/stats`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting RAG stats:', error);
      throw error;
    }
  },

  /**
   * Health check
   * @returns {Promise<Object>} Backend health status
   */
  healthCheck: async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/health`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }
};

export default tripPlannerService;

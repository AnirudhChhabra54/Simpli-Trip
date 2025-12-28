import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';

/**
 * ContextEnrichmentPanel Component
 * 
 * This component:
 * - Fetches enriched context (location + weather + travel tips)
 * - Passes context to LLM for better itinerary generation
 * - Shows packing suggestions and activity recommendations
 * - Provides travel advisories and best season info
 */

const ContextEnrichmentPanel = ({ 
  destination, 
  tripDates = [],
  budget = null,
  preferences = [],
  onContextReady = null,
  showDetails = false
}) => {
  const [llmContext, setLlmContext] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (destination) {
      fetchEnrichedContext();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [destination, tripDates, budget, preferences]);

  const fetchEnrichedContext = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.post(
        'http://localhost:8000/api/v1/enrichment/llm-context',
        {
          destination: destination,
          travel_dates: tripDates,
          budget: budget,
          preferences: preferences
        }
      );

      const context = response.data.llm_context;
      setLlmContext(context);

      // Notify parent component that context is ready
      if (onContextReady) {
        onContextReady(context);
      }
    } catch (err) {
      console.error('Context enrichment error:', err);
      setError('Failed to load enriched context');
    } finally {
      setLoading(false);
    }
  };

  const copyContextToClipboard = () => {
    const contextJson = JSON.stringify(llmContext, null, 2);
    navigator.clipboard.writeText(contextJson);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Generate formatted context for LLM prompt
  const generateLlmPrompt = () => {
    if (!llmContext) return "";

    const dest = llmContext.destination || {};
    const weather = llmContext.weather || {};
    const trip = llmContext.trip_details || {};

    return `
# Trip Planning Context

## Destination: ${dest.name || destination}
- **Coordinates**: ${dest.coordinates?.lat?.toFixed(2) || 'N/A'}°, ${dest.coordinates?.lon?.toFixed(2) || 'N/A'}°
- **Description**: ${dest.description || 'Popular travel destination'}

## Trip Details
- **Duration**: ${trip.duration_days || 'Not specified'} days
- **Budget**: ₹${trip.budget?.toLocaleString() || 'Not specified'}
- **Dates**: ${trip.start_date || 'Not specified'} to ${trip.end_date || 'Not specified'}
- **Preferences**: ${trip.preferences?.join(', ') || 'None specified'}

## Current Weather
- **Temperature**: ${weather.current?.temperature || 'N/A'}°C (Feels like ${weather.current?.feels_like || 'N/A'}°C)
- **Condition**: ${weather.current?.condition || 'N/A'}
- **Humidity**: ${weather.current?.humidity || 'N/A'}%
- **UV Index**: ${weather.current?.uv_index || 'N/A'}

## Best Season
- **Best Months**: ${weather.best_season?.months?.join(', ') || 'Not available'}
- **Reason**: ${weather.best_season?.reason || 'N/A'}
- **Dry Season**: ${weather.best_season?.dry_season || 'N/A'}

## Packing Suggestions
${llmContext.packing || 'Standard travel essentials'}

## Activity Recommendations
${llmContext.activities || 'Popular local activities'}

## Travel Tips
${dest.travel_tips || 'Standard travel safety'}

---
Please generate a detailed, day-by-day itinerary based on the above context.
    `;
  };

  if (!showDetails) {
    return null;
  }

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-slate-800 to-slate-900 border-2 border-cyan-500/30 rounded-lg p-6"
      >
        <div className="flex justify-center items-center h-20">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full"
          />
        </div>
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-slate-800 to-slate-900 border-2 border-red-500/30 rounded-lg p-6"
      >
        <div className="text-red-400">{error}</div>
        <button
          onClick={fetchEnrichedContext}
          className="mt-4 px-4 py-2 bg-red-500/20 text-red-300 rounded hover:bg-red-500/30 transition-colors"
        >
          Retry
        </button>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Context Summary */}
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 border-2 border-cyan-500/30 rounded-lg p-6">
        <div className="flex justify-between items-center mb-4 pb-4 border-b border-cyan-500/20">
          <h3 className="text-lg font-bold text-cyan-300">📊 Enriched Trip Context</h3>
          <button
            onClick={copyContextToClipboard}
            className="text-xs px-3 py-1 bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30 rounded transition-colors"
          >
            {copied ? "✓ Copied" : "📋 Copy Context"}
          </button>
        </div>

        <div className="space-y-4">
          {/* Destination Info */}
          {llmContext?.destination && (
            <div className="bg-slate-700/30 rounded p-4 border border-slate-600">
              <h4 className="text-cyan-300 font-semibold mb-2">📍 Destination</h4>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <div className="text-gray-400">Name</div>
                  <div className="text-cyan-300">{llmContext.destination.name}</div>
                </div>
                <div>
                  <div className="text-gray-400">Coordinates</div>
                  <div className="text-cyan-300 text-xs">
                    {llmContext.destination.coordinates?.lat?.toFixed(2)}°,
                    {llmContext.destination.coordinates?.lon?.toFixed(2)}°
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Trip Details */}
          {llmContext?.trip_details && (
            <div className="bg-slate-700/30 rounded p-4 border border-slate-600">
              <h4 className="text-cyan-300 font-semibold mb-2">📅 Trip Details</h4>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <div className="text-gray-400">Duration</div>
                  <div className="text-cyan-300">{llmContext.trip_details.duration_days} days</div>
                </div>
                <div>
                  <div className="text-gray-400">Budget</div>
                  <div className="text-cyan-300">₹{llmContext.trip_details.budget?.toLocaleString() || 'N/A'}</div>
                </div>
                <div className="col-span-2">
                  <div className="text-gray-400">Dates</div>
                  <div className="text-cyan-300 text-sm">
                    {llmContext.trip_details.start_date} to {llmContext.trip_details.end_date}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Weather Summary */}
          {llmContext?.weather?.current && (
            <div className="bg-slate-700/30 rounded p-4 border border-slate-600">
              <h4 className="text-cyan-300 font-semibold mb-2">☀️ Weather</h4>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <div className="text-gray-400">Temperature</div>
                  <div className="text-cyan-300">{llmContext.weather.current.temperature}°C</div>
                </div>
                <div>
                  <div className="text-gray-400">Condition</div>
                  <div className="text-cyan-300">{llmContext.weather.current.condition}</div>
                </div>
                <div>
                  <div className="text-gray-400">Humidity</div>
                  <div className="text-cyan-300">{llmContext.weather.current.humidity}%</div>
                </div>
                <div>
                  <div className="text-gray-400">UV Index</div>
                  <div className="text-cyan-300">{llmContext.weather.current.uv_index}</div>
                </div>
              </div>
            </div>
          )}

          {/* Packing Suggestions */}
          {llmContext?.packing && (
            <div className="bg-slate-700/30 rounded p-4 border border-slate-600">
              <h4 className="text-cyan-300 font-semibold mb-2">🎒 Packing Suggestions</h4>
              <pre className="text-xs text-gray-300 whitespace-pre-wrap overflow-hidden max-h-32">
                {llmContext.packing}
              </pre>
            </div>
          )}

          {/* Activity Recommendations */}
          {llmContext?.activities && (
            <div className="bg-slate-700/30 rounded p-4 border border-slate-600">
              <h4 className="text-cyan-300 font-semibold mb-2">🎯 Activity Recommendations</h4>
              <pre className="text-xs text-gray-300 whitespace-pre-wrap overflow-hidden max-h-32">
                {llmContext.activities}
              </pre>
            </div>
          )}

          {/* LLM Prompt Preview */}
          <div className="bg-slate-700/20 rounded p-4 border border-slate-600">
            <h4 className="text-cyan-300 font-semibold mb-2">💡 LLM Prompt Preview</h4>
            <pre className="text-xs text-gray-300 bg-slate-900 p-3 rounded overflow-x-auto max-h-40 overflow-y-auto whitespace-pre-wrap">
              {generateLlmPrompt()}
            </pre>
          </div>

          {/* Refresh Button */}
          <button
            onClick={fetchEnrichedContext}
            className="w-full py-2 px-4 bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 rounded-lg transition-colors font-semibold"
          >
            🔄 Refresh Context
          </button>
        </div>
      </div>
    </motion.div>
  );
};

export default ContextEnrichmentPanel;

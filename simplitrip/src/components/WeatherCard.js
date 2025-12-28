import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';

/**
 * WeatherCard Component
 * 
 * Features:
 * - Displays current weather and 7-day forecast
 * - Shows temperature, humidity, wind speed, UV index
 * - Weather-based travel advisory
 * - Best season recommendations
 * - Packing suggestions based on weather
 */

const WeatherCard = ({ 
  destination, 
  lat, 
  lon,
  tripDates = null,
  onWeatherData = null
}) => {
  const [currentWeather, setCurrentWeather] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [bestSeason, setBestSeason] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("current"); // current, forecast, season

  useEffect(() => {
    if (destination && lat && lon) {
      fetchWeatherData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [destination, lat, lon]);

  const fetchWeatherData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch current weather
      const currentRes = await axios.post(
        'http://localhost:8000/api/v1/weather/current',
        {
          lat: lat,
          lon: lon,
          location_name: destination
        }
      );

      setCurrentWeather(currentRes.data.weather);

      // Fetch forecast
      const forecastRes = await axios.post(
        'http://localhost:8000/api/v1/weather/forecast',
        {
          lat: lat,
          lon: lon,
          location_name: destination,
          days: 7
        }
      );

      setForecast(forecastRes.data.daily);

      // Fetch best season
      const seasonRes = await axios.get(
        `http://localhost:8000/api/v1/weather/best-season?destination=${destination}`
      );

      setBestSeason(seasonRes.data);

      // Callback with all data
      if (onWeatherData) {
        onWeatherData({
          current: currentRes.data.weather,
          forecast: forecastRes.data.daily,
          season: seasonRes.data
        });
      }
    } catch (err) {
      console.error('Weather fetch error:', err);
      setError('Failed to fetch weather data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-slate-800 to-slate-900 border-2 border-cyan-500/30 rounded-lg p-6"
      >
        <div className="flex justify-center items-center h-40">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full"
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
        <div className="text-red-400 text-center">{error}</div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-slate-800 to-slate-900 border-2 border-cyan-500/30 rounded-lg p-6 space-y-4"
    >
      {/* Header */}
      <div className="flex justify-between items-center border-b border-cyan-500/20 pb-4">
        <h3 className="text-xl font-bold text-cyan-300">
          ☁️ Weather for {destination}
        </h3>
        <button
          onClick={fetchWeatherData}
          className="text-xs px-3 py-1 bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30 rounded transition-colors"
        >
          🔄 Refresh
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-slate-700">
        {["current", "forecast", "season"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab
                ? "text-cyan-300 border-b-2 border-cyan-400"
                : "text-gray-400 hover:text-cyan-300"
            }`}
          >
            {tab === "current" && "Current"}
            {tab === "forecast" && "7-Day Forecast"}
            {tab === "season" && "Best Season"}
          </button>
        ))}
      </div>

      {/* Current Weather Tab */}
      {activeTab === "current" && currentWeather && (
        <motion.div
          key="current"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-4"
        >
          {/* Main Weather Display */}
          <div className="grid grid-cols-2 gap-4">
            {/* Temperature */}
            <div className="bg-slate-700/50 rounded-lg p-4 border border-cyan-500/20">
              <div className="text-gray-400 text-sm">Temperature</div>
              <div className="text-3xl font-bold text-cyan-300 mt-2">
                {currentWeather.temperature}°C
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Feels like {currentWeather.feels_like}°C
              </div>
            </div>

            {/* Condition */}
            <div className="bg-slate-700/50 rounded-lg p-4 border border-cyan-500/20">
              <div className="text-gray-400 text-sm">Condition</div>
              <div className="text-xl font-bold text-cyan-300 mt-2">
                {currentWeather.condition}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Cloudiness: {currentWeather.cloudiness}%
              </div>
            </div>
          </div>

          {/* Weather Details Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
            <div className="bg-slate-700/30 rounded p-3 border border-slate-600">
              <div className="text-gray-400">💧 Humidity</div>
              <div className="text-cyan-300 font-bold mt-1">{currentWeather.humidity}%</div>
            </div>

            <div className="bg-slate-700/30 rounded p-3 border border-slate-600">
              <div className="text-gray-400">💨 Wind Speed</div>
              <div className="text-cyan-300 font-bold mt-1">{currentWeather.wind_speed || "N/A"} km/h</div>
            </div>

            <div className="bg-slate-700/30 rounded p-3 border border-slate-600">
              <div className="text-gray-400">☀️ UV Index</div>
              <div className="text-cyan-300 font-bold mt-1">{currentWeather.uv_index.toFixed(1)}</div>
            </div>

            <div className="bg-slate-700/30 rounded p-3 border border-slate-600">
              <div className="text-gray-400">🌧️ Precipitation</div>
              <div className="text-cyan-300 font-bold mt-1">{currentWeather.precipitation}mm</div>
            </div>

            <div className="bg-slate-700/30 rounded p-3 border border-slate-600">
              <div className="text-gray-400">👁️ Visibility</div>
              <div className="text-cyan-300 font-bold mt-1">{(currentWeather.visibility / 1000).toFixed(1)}km</div>
            </div>

            <div className="bg-slate-700/30 rounded p-3 border border-slate-600">
              <div className="text-gray-400">🕐 Updated</div>
              <div className="text-cyan-300 font-bold mt-1 text-xs">
                {new Date(currentWeather.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>

          {/* Weather Advisory */}
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-4">
            <div className="text-amber-300 font-semibold mb-2">⚠️ Travel Advisory</div>
            <div className="text-sm text-amber-100 space-y-1">
              {currentWeather.temperature > 35 && (
                <div>☀️ Very hot - Stay hydrated and use sunscreen</div>
              )}
              {currentWeather.temperature < 10 && (
                <div>❄️ Cold weather - Bring warm clothing</div>
              )}
              {currentWeather.precipitation > 5 && (
                <div>☔ Rain possible - Carry umbrella</div>
              )}
              {currentWeather.humidity > 80 && (
                <div>💧 High humidity - Light, breathable clothing recommended</div>
              )}
              {currentWeather.uv_index > 6 && (
                <div>☀️ High UV index - Apply sunscreen SPF 50+</div>
              )}
              {currentWeather.temperature >= 15 && currentWeather.temperature <= 30 && 
                currentWeather.precipitation < 5 && (
                <div>✅ Perfect weather for outdoor activities!</div>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* Forecast Tab */}
      {activeTab === "forecast" && forecast && (
        <motion.div
          key="forecast"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-3"
        >
          {forecast.map((day, index) => (
            <div key={index} className="bg-slate-700/30 rounded-lg p-3 border border-slate-600">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <div className="font-semibold text-cyan-300">
                    {new Date(day.date).toLocaleDateString('en-IN', { weekday: 'short', month: 'short', day: 'numeric' })}
                  </div>
                  <div className="text-sm text-gray-400">{day.condition}</div>
                </div>
                <div className="text-right text-sm">
                  <div className="text-cyan-300">🌡️ {day.max_temp}° / {day.min_temp}°</div>
                </div>
              </div>
              <div className="grid grid-cols-4 gap-2 text-xs">
                <div className="text-gray-400">💧 Precip</div>
                <div className="text-cyan-300">{day.precipitation}mm</div>
                <div className="text-gray-400">⛅ Prob</div>
                <div className="text-cyan-300">{day.precipitation_prob}%</div>
              </div>
              <div className="grid grid-cols-4 gap-2 text-xs mt-2">
                <div className="text-gray-400">🌅 Sunrise</div>
                <div className="text-cyan-300">{day.sunrise}</div>
                <div className="text-gray-400">🌇 Sunset</div>
                <div className="text-cyan-300">{day.sunset}</div>
              </div>
            </div>
          ))}
        </motion.div>
      )}

      {/* Best Season Tab */}
      {activeTab === "season" && bestSeason && (
        <motion.div
          key="season"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-4"
        >
          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
            <div className="text-green-300 font-semibold mb-3">✅ Best Months to Visit</div>
            <div className="flex flex-wrap gap-2 mb-4">
              {bestSeason.months.map((month, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-green-500/20 text-green-300 rounded-full text-sm"
                >
                  {month}
                </span>
              ))}
            </div>
            <div className="text-sm text-green-100 mb-3">
              {bestSeason.reason}
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="bg-green-500/5 rounded p-2">
                <div className="text-gray-400">Average Temp</div>
                <div className="text-green-300 font-bold">{bestSeason.avg_temp}°C</div>
              </div>
              <div className="bg-green-500/5 rounded p-2">
                <div className="text-gray-400">Dry Season</div>
                <div className="text-green-300 font-bold text-xs">{bestSeason.dry_season}</div>
              </div>
              <div className="col-span-2 bg-green-500/5 rounded p-2">
                <div className="text-gray-400">Monsoon Season</div>
                <div className="text-green-300 font-bold text-xs">{bestSeason.rainfall_season}</div>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default WeatherCard;

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * LocationSearch Component
 * 
 * Features:
 * - Real-time location autocomplete using Nominatim OSM
 * - Shows coordinates, state, and importance score
 * - Debounced API calls for performance
 * - Keyboard navigation support
 * - Click outside to close dropdown
 */

const LocationSearch = ({ 
  onLocationSelect, 
  placeholder = "Search destination...",
  required = false,
  initialValue = ""
}) => {
  const [query, setQuery] = useState(initialValue);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const debounceTimer = useRef(null);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);

  // Debounced search function
  useEffect(() => {
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    if (query.length < 2) {
      setSuggestions([]);
      return;
    }

    setLoading(true);
    debounceTimer.current = setTimeout(async () => {
      try {
        const response = await axios.post(
          'http://localhost:8000/api/v1/locations/search',
          {
            query: query,
            limit: 8,
            country: "India"
          }
        );

        if (response.data.results) {
          setSuggestions(response.data.results);
          setShowDropdown(true);
          setSelectedIndex(-1);
        }
      } catch (error) {
        console.error('Location search error:', error);
        setSuggestions([]);
      } finally {
        setLoading(false);
      }
    }, 300); // 300ms debounce

    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, [query]);

  // Handle clicks outside dropdown
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target) &&
        !inputRef.current?.contains(event.target)
      ) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Keyboard navigation
  const handleKeyDown = (e) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev =>
          prev > 0 ? prev - 1 : suggestions.length - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && suggestions[selectedIndex]) {
          handleSelectLocation(suggestions[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowDropdown(false);
        break;
      default:
        break;
    }
  };

  // Handle location selection
  const handleSelectLocation = (location) => {
    setQuery(location.name);
    setShowDropdown(false);
    setSuggestions([]);

    if (onLocationSelect) {
      onLocationSelect({
        name: location.name,
        lat: location.lat,
        lon: location.lon,
        state: location.state,
        country: location.country,
        importance: location.importance
      });
    }
  };

  return (
    <div className="relative w-full">
      {/* Input Field */}
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => query.length >= 2 && setShowDropdown(true)}
          placeholder={placeholder}
          required={required}
          className="w-full px-4 py-3 bg-slate-800 border-2 border-cyan-500/50 rounded-lg text-white placeholder-gray-400 focus:border-cyan-400 focus:outline-none transition-colors"
        />

        {/* Loading Indicator */}
        {loading && (
          <div className="absolute right-3 top-3">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              className="w-5 h-5 border-2 border-cyan-400 border-t-transparent rounded-full"
            />
          </div>
        )}

        {/* Clear Button */}
        {query && !loading && (
          <button
            onClick={() => {
              setQuery("");
              setSuggestions([]);
              onLocationSelect?.(null);
            }}
            className="absolute right-3 top-3 text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        )}
      </div>

      {/* Suggestions Dropdown */}
      <AnimatePresence>
        {showDropdown && suggestions.length > 0 && (
          <motion.div
            ref={dropdownRef}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="absolute top-full left-0 right-0 mt-1 bg-slate-900 border-2 border-cyan-500/30 rounded-lg shadow-xl z-50 max-h-64 overflow-y-auto"
          >
            {suggestions.map((location, index) => (
              <motion.div
                key={`${location.name}-${index}`}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                onClick={() => handleSelectLocation(location)}
                onMouseEnter={() => setSelectedIndex(index)}
                className={`px-4 py-3 cursor-pointer transition-colors border-b border-slate-700 last:border-b-0 ${
                  index === selectedIndex
                    ? "bg-cyan-500/20 text-cyan-300"
                    : "hover:bg-slate-800 text-gray-300"
                }`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-semibold">{location.name}</div>
                    {location.state && (
                      <div className="text-xs text-gray-400">
                        📍 {location.state}, {location.country}
                      </div>
                    )}
                  </div>
                  {location.importance && (
                    <div className="text-xs bg-cyan-500/20 text-cyan-300 px-2 py-1 rounded">
                      Score: {(location.importance * 100).toFixed(0)}%
                    </div>
                  )}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {location.lat.toFixed(2)}°, {location.lon.toFixed(2)}°
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* No Results */}
      {showDropdown && query.length >= 2 && suggestions.length === 0 && !loading && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute top-full left-0 right-0 mt-1 bg-slate-900 border-2 border-cyan-500/30 rounded-lg p-4 text-center text-gray-400"
        >
          No destinations found. Try another search.
        </motion.div>
      )}
    </div>
  );
};

export default LocationSearch;

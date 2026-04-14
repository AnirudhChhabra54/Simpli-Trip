import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { parseItinerary } from '../utils/itineraryParser';
import { formatCurrency } from '../services/aiService';

/**
 * ItineraryView - Renders a structured, day-by-day view of a generated
 * itinerary (parsed from the backend's markdown output) alongside the map.
 */
const ItineraryView = ({ markdown, destination = '', budget = null }) => {
  const [parsed, setParsed] = useState({ summary: '', days: [] });
  const [openDay, setOpenDay] = useState(null);

  useEffect(() => {
    const result = parseItinerary(markdown);
    setParsed(result);
    if (result.days.length && openDay === null) {
      setOpenDay(result.days[0].dayNumber);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [markdown]);

  const { days, summary } = parsed;
  if (!days.length) return null;

  const totalCost = days.reduce((sum, d) => sum + d.totalCost, 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      <div className="bg-gradient-to-br from-cyan-600/20 to-purple-600/20 border border-cyan-500/30 rounded-2xl p-6">
        <h3 className="text-2xl font-bold text-white mb-2">
          📅 {destination ? `${destination} Itinerary` : 'Day-by-Day Itinerary'}
        </h3>
        <div className="flex flex-wrap gap-3 text-sm">
          <span className="px-3 py-1 bg-cyan-500/20 text-cyan-200 rounded-full">{days.length} Days</span>
          {totalCost > 0 && (
            <span className="px-3 py-1 bg-green-500/20 text-green-200 rounded-full">
              Est. {formatCurrency(totalCost)}
            </span>
          )}
          {budget && (
            <span className="px-3 py-1 bg-amber-500/20 text-amber-200 rounded-full">
              Budget {formatCurrency(budget)}
            </span>
          )}
        </div>
        {summary && <p className="mt-4 text-gray-300 text-sm whitespace-pre-wrap">{summary}</p>}
      </div>

      <div className="space-y-3">
        {days.map((day, idx) => {
          const isOpen = openDay === day.dayNumber;
          return (
            <motion.div
              key={day.dayNumber}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="bg-gray-800/70 border border-gray-700/50 rounded-xl overflow-hidden"
            >
              <button
                onClick={() => setOpenDay(isOpen ? null : day.dayNumber)}
                className="w-full flex items-center justify-between px-5 py-4 hover:bg-gray-800 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="flex items-center justify-center w-9 h-9 rounded-lg bg-cyan-600/30 text-cyan-300 font-bold">
                    {day.dayNumber}
                  </span>
                  <span className="text-white font-semibold">{day.title || `Day ${day.dayNumber}`}</span>
                </div>
                <div className="flex items-center gap-3">
                  {day.totalCost > 0 && (
                    <span className="text-sm text-gray-300">{formatCurrency(day.totalCost)}</span>
                  )}
                  <span className="text-gray-400">{isOpen ? '−' : '+'}</span>
                </div>
              </button>
              {isOpen && (
                <div className="px-5 pb-4 space-y-2">
                  {day.items.filter((it) => it.text).map((item, i) => (
                    <div key={i} className="flex items-start justify-between gap-3 text-sm">
                      <div className="text-gray-300 flex-1">{item.text}</div>
                      {item.cost && (
                        <div className="text-cyan-300 font-semibold whitespace-nowrap">
                          {formatCurrency(parseInt(item.cost, 10))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};

export default ItineraryView;
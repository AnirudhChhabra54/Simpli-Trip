import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getTripsByUserId, deleteTrip } from '../services/firestore';
import { useUser } from '../context/UserContext';
import Layout from '../components/Layout';

const MyTripsPage = () => {
  const { user } = useUser();
  const location = useLocation();
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tripsToDisplay, setTripsToDisplay] = useState(12);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('recent');

  // Filter and validate trips - remove duplicates and invalid entries
  const validTrips = useMemo(() => {
    let filtered = trips.filter(trip => {
      if (!trip || !trip.id) return false;
      if (!trip.name || trip.name.trim() === '') return false;
      // Only filter out AI Generated Trips that have no budget (incomplete)
      if (trip.destination === 'AI Generated Trip' && (!trip.budget || trip.budget === 0)) {
        return false;
      }
      return true;
    });

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(trip => 
        trip.name.toLowerCase().includes(query) ||
        (trip.destination && trip.destination.toLowerCase().includes(query))
      );
    }

    // Apply sorting
    const sorted = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'recent':
          return new Date(b.createdAt?.toDate?.() || b.createdAt || 0) - 
                 new Date(a.createdAt?.toDate?.() || a.createdAt || 0);
        case 'oldest':
          return new Date(a.createdAt?.toDate?.() || a.createdAt || 0) - 
                 new Date(b.createdAt?.toDate?.() || b.createdAt || 0);
        case 'name':
          return a.name.localeCompare(b.name);
        case 'budget':
          return (b.budget || 0) - (a.budget || 0);
        default:
          return 0;
      }
    });

    // Remove duplicates
    return sorted.reduce((unique, trip) => {
      const exists = unique.some(t => t.id === trip.id);
      return exists ? unique : [...unique, trip];
    }, []);
  }, [trips, searchQuery, sortBy]);

  const loadTrips = useCallback(async () => {
    try {
      setLoading(true);
      const userTrips = await getTripsByUserId(user.uid);
      console.log('Loaded trips for user:', user.uid, userTrips);
      setTrips(userTrips || []);
      setError('');
    } catch (error) {
      setError('Failed to load trips');
      console.error('Error loading trips:', error);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (user) {
      loadTrips();
    }
  }, [user, loadTrips, location]);

  const handleDeleteTrip = async (tripId) => {
    if (deleteConfirm !== tripId) {
      setDeleteConfirm(tripId);
      return;
    }

    setDeleting(true);
    try {
      await deleteTrip(tripId);
      setTrips(trips.filter(t => t.id !== tripId));
      setDeleteConfirm(null);
      setError('');
    } catch (err) {
      setError('Failed to delete trip');
      console.error('Error deleting trip:', err);
    } finally {
      setDeleting(false);
    }
  };

  const loadMore = () => {
    setTripsToDisplay(prev => prev + 12);
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="inline-block">
              <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-cyan-500 mb-4"></div>
              <p className="text-xl font-semibold text-white">Loading your trips...</p>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">
                ✈️ My Trips
              </h1>
              <p className="text-gray-400">
                {validTrips.length === 0 
                  ? 'No trips yet. Start planning your next adventure!' 
                  : `You have ${validTrips.length} trip${validTrips.length !== 1 ? 's' : ''}`}
              </p>
            </div>
            <Link
              to="/plan-trip"
              className="inline-flex items-center justify-center bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white font-bold py-3 px-6 rounded-xl transition-all shadow-lg hover:shadow-cyan-500/30 whitespace-nowrap"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
              </svg>
              Plan New Trip
            </Link>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-900/30 border-l-4 border-red-500 rounded-r-lg animate-fadeIn">
              <div className="flex items-start justify-between">
                <div className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-red-400 mr-2 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <p className="text-red-300">{error}</p>
                </div>
                <button
                  onClick={() => setError('')}
                  className="text-red-400 hover:text-red-300"
                >
                  ×
                </button>
              </div>
            </div>
          )}
        </motion.div>

        {/* Search and Sort Controls */}
        {validTrips.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8 p-6 bg-gradient-to-r from-gray-800/50 to-gray-900/50 rounded-2xl border border-gray-700"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Search */}
              <div className="relative">
                <svg className="absolute left-3 top-3.5 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                </svg>
                <input
                  type="text"
                  placeholder="Search trips by name or destination..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setTripsToDisplay(12);
                  }}
                  className="w-full pl-10 pr-4 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500"
                />
              </div>

              {/* Sort */}
              <select
                value={sortBy}
                onChange={(e) => {
                  setSortBy(e.target.value);
                  setTripsToDisplay(12);
                }}
                className="px-4 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-cyan-500 cursor-pointer"
              >
                <option value="recent">Most Recent</option>
                <option value="oldest">Oldest First</option>
                <option value="name">Name (A-Z)</option>
                <option value="budget">Highest Budget</option>
              </select>
            </div>
          </motion.div>
        )}

        {/* Trips Grid */}
        {validTrips.length > 0 ? (
          <>
            {/* Debug Info */}
            <div className="mb-4 p-3 bg-gray-800/50 rounded-lg border border-gray-700">
              <p className="text-gray-400 text-sm">
                Total trips: {trips.length} | Valid trips: {validTrips.length} | Displaying: {Math.min(tripsToDisplay, validTrips.length)}
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8">
              {validTrips.slice(0, tripsToDisplay).map((trip) => (
                <motion.div
                  key={trip.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="group relative"
                >
                  <Link 
                    to={`/trip/${trip.id}`}
                    className="block h-full"
                  >
                    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl overflow-hidden border border-gray-700 hover:border-cyan-500/50 transition-all duration-300 transform hover:-translate-y-1 hover:shadow-xl hover:shadow-cyan-500/10 h-full">
                      <div className="p-6">
                        <div className="flex justify-between items-start mb-4">
                          <h2 className="text-xl font-bold text-white group-hover:text-cyan-300 transition-colors flex-1 pr-2 line-clamp-2">
                            {trip.name}
                          </h2>
                          <div className="text-2xl flex-shrink-0">
                            {trip.source === 'AI Chat' ? '🤖' : '✈️'}
                          </div>
                        </div>

                        <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                          📍 {trip.destination || 'Not specified'}
                        </p>

                        <div className="space-y-2 mb-4">
                          {trip.budget > 0 && (
                            <div className="flex justify-between items-center">
                              <span className="text-gray-400 text-sm">Budget</span>
                              <span className="text-cyan-300 font-semibold">₹{trip.budget?.toLocaleString() || 'N/A'}</span>
                            </div>
                          )}
                          {trip.days > 0 && (
                            <div className="flex justify-between items-center">
                              <span className="text-gray-400 text-sm">Duration</span>
                              <span className="text-purple-300 font-semibold">{trip.days} days</span>
                            </div>
                          )}
                          {trip.travelers > 0 && (
                            <div className="flex justify-between items-center">
                              <span className="text-gray-400 text-sm">Travelers</span>
                              <span className="text-green-300 font-semibold">{trip.travelers} person{trip.travelers !== 1 ? 's' : ''}</span>
                            </div>
                          )}
                        </div>

                        <div className="flex justify-between items-center pt-4 border-t border-gray-700">
                          <span className="text-gray-500 text-xs">
                            {trip.createdAt ? new Date(trip.createdAt.toDate?.() || trip.createdAt).toLocaleDateString() : 'New'}
                          </span>
                          <span className="text-xs px-2 py-1 bg-cyan-900/30 text-cyan-300 rounded-full">
                            {trip.status || 'planned'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </Link>

                  {/* Delete Button */}
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleDeleteTrip(trip.id)}
                    disabled={deleting}
                    className={`absolute top-4 right-4 z-10 p-2 rounded-full transition-all ${
                      deleteConfirm === trip.id
                        ? 'bg-red-600 text-white shadow-lg shadow-red-600/50'
                        : 'bg-gray-700/80 text-gray-300 hover:bg-red-600 hover:text-white'
                    }`}
                    title={deleteConfirm === trip.id ? 'Click again to confirm delete' : 'Delete trip'}
                  >
                    {deleting ? (
                      <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    )}
                  </motion.button>
                </motion.div>
              ))}
            </div>

            {/* Load More Button */}
            {tripsToDisplay < validTrips.length && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center mb-8"
              >
                <button
                  onClick={loadMore}
                  className="bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white font-bold py-3 px-8 rounded-xl transition-all shadow-lg hover:shadow-cyan-500/30"
                >
                  Load More ({validTrips.length - tripsToDisplay} remaining)
                </button>
              </motion.div>
            )}
          </>
        ) : (
          <div className="text-center py-16 bg-gradient-to-br from-gray-800/30 to-gray-900/50 rounded-2xl border border-gray-700/50">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-cyan-900/30 to-purple-900/30 mb-6">
              <span className="text-4xl">✈️</span>
            </div>
            <h3 className="text-2xl font-bold text-white mb-3">No trips yet!</h3>
            <p className="text-gray-400 max-w-2xl mx-auto mb-6 px-4">
              Start planning your dream vacation with our AI-powered trip planner.
            </p>
            <Link
              to="/plan-trip"
              className="inline-flex items-center justify-center bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white font-bold py-3 px-8 rounded-xl transition-all shadow-lg hover:shadow-cyan-500/30"
            >
              <span className="mr-2">✨</span>
              Start Planning
            </Link>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default MyTripsPage;

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getTripsByUserId, deleteTrip } from '../services/firestore';
import { useUser } from '../context/UserContext';
import Layout from '../components/Layout';
import { FaPlaneDeparture, FaRobot, FaTrash, FaPlus, FaSearch, FaMapMarkerAlt } from 'react-icons/fa';

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
    let filtered = trips.filter((trip) => {
      if (!trip || !trip.id) return false;
      if (!trip.name || trip.name.trim() === '') return false;
      return true;
    });

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (trip) =>
          trip.name?.toLowerCase().includes(query) ||
          (trip.destination && trip.destination.toLowerCase().includes(query))
      );
    }

    // Apply sorting
    const sorted = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'recent':
          return (
            new Date(b.createdAt?.toDate?.() || b.createdAt || 0) -
            new Date(a.createdAt?.toDate?.() || a.createdAt || 0)
          );
        case 'oldest':
          return (
            new Date(a.createdAt?.toDate?.() || a.createdAt || 0) -
            new Date(b.createdAt?.toDate?.() || b.createdAt || 0)
          );
        case 'name':
          return (a.name || '').localeCompare(b.name || '');
        case 'budget':
          return (Number(b.budget) || 0) - (Number(a.budget) || 0);
        default:
          return 0;
      }
    });

    // Deduplicate
    return sorted.reduce((unique, trip) => {
      const exists = unique.some((t) => t.id === trip.id);
      return exists ? unique : [...unique, trip];
    }, []);
  }, [trips, searchQuery, sortBy]);

  const loadTrips = useCallback(async () => {
    try {
      setLoading(true);
      const userTrips = await getTripsByUserId(user?.uid);
      setTrips(userTrips || []);
      setError('');
    } catch (err) {
      setError('Failed to load saved trips');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadTrips();
  }, [loadTrips, location]);

  const handleDeleteTrip = async (e, tripId) => {
    e.preventDefault();
    e.stopPropagation();

    if (deleteConfirm !== tripId) {
      setDeleteConfirm(tripId);
      return;
    }

    setDeleting(true);
    try {
      await deleteTrip(tripId);
      setTrips((prev) => prev.filter((t) => t.id !== tripId));
      setDeleteConfirm(null);
    } catch (err) {
      setError('Failed to delete trip');
    } finally {
      setDeleting(false);
    }
  };

  const loadMore = () => {
    setTripsToDisplay((prev) => prev + 12);
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500 mb-4 mx-auto" />
            <p className="text-sm font-semibold text-slate-300">Retrieving your travel blueprints...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header Section */}
        <motion.div initial={{ opacity: 0, y: -15 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-pill text-xs font-semibold text-cyan-400 mb-2 border border-cyan-500/30">
                <span>ITINERARY VAULT</span>
              </div>
              <h1 className="text-3xl sm:text-4xl font-black text-white font-display">
                My Saved Journeys
              </h1>
              <p className="text-slate-400 text-sm font-light">
                {validTrips.length === 0
                  ? 'No trips saved yet. Generate your first custom blueprint in seconds.'
                  : `Managing ${validTrips.length} custom travel itinerary blueprint${validTrips.length > 1 ? 's' : ''}.`}
              </p>
            </div>

            <Link
              to="/plan-trip"
              className="btn-cinema-primary px-6 py-3 text-xs sm:text-sm font-bold flex items-center gap-2 self-start md:self-auto shadow-lg shadow-cyan-500/20"
            >
              <FaPlus className="text-xs" />
              <span>Plan New Trip</span>
            </Link>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-rose-500/10 border border-rose-500/30 rounded-2xl text-rose-300 text-xs flex justify-between items-center">
              <span>{error}</span>
              <button onClick={() => setError('')} className="text-rose-400 hover:text-white text-sm">
                ✕
              </button>
            </div>
          )}
        </motion.div>

        {/* Search and Filter Bar */}
        {trips.length > 0 && (
          <div className="glass-cinema rounded-2xl p-4 border border-white/10 flex flex-col sm:flex-row items-center gap-3">
            <div className="relative flex-1 w-full">
              <FaSearch className="absolute left-3.5 top-3.5 text-slate-400 text-xs" />
              <input
                type="text"
                placeholder="Search journeys by name or destination..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setTripsToDisplay(12);
                }}
                className="w-full pl-10 pr-4 py-2.5 glass-input rounded-xl text-xs sm:text-sm placeholder:text-slate-500"
              />
            </div>

            <select
              value={sortBy}
              onChange={(e) => {
                setSortBy(e.target.value);
                setTripsToDisplay(12);
              }}
              className="glass-input rounded-xl px-4 py-2.5 text-xs text-slate-200 cursor-pointer w-full sm:w-auto"
            >
              <option value="recent" className="bg-[#080f24] text-white">Most Recent</option>
              <option value="oldest" className="bg-[#080f24] text-white">Oldest First</option>
              <option value="name" className="bg-[#080f24] text-white">Destination (A-Z)</option>
              <option value="budget" className="bg-[#080f24] text-white">Highest Budget</option>
            </select>
          </div>
        )}

        {/* Trips Grid */}
        {validTrips.length > 0 ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {validTrips.slice(0, tripsToDisplay).map((trip) => (
                <motion.div
                  key={trip.id}
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  whileHover={{ y: -5 }}
                  className="glass-cinema-card rounded-3xl p-6 border border-white/10 relative group flex flex-col justify-between"
                >
                  <Link to={`/trip/${trip.id}`} className="block">
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div>
                        <div className="flex items-center gap-1.5 text-cyan-400 text-xs font-semibold mb-1">
                          <FaMapMarkerAlt className="text-[10px]" />
                          <span>{trip.destination || 'Custom Journey'}</span>
                        </div>
                        <h2 className="text-xl font-bold text-white font-display line-clamp-1 group-hover:text-cyan-300 transition-colors">
                          {trip.name}
                        </h2>
                      </div>
                      <div className="w-9 h-9 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center shrink-0">
                        {trip.source === 'AI Chat' ? <FaRobot /> : <FaPlaneDeparture />}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-2 p-3 rounded-2xl bg-white/[0.03] border border-white/5 my-4 text-xs">
                      {trip.budget > 0 && (
                        <div>
                          <p className="text-[10px] text-slate-400 uppercase font-semibold">Budget</p>
                          <p className="font-bold text-white">₹{Number(trip.budget).toLocaleString('en-IN')}</p>
                        </div>
                      )}
                      {trip.days > 0 && (
                        <div>
                          <p className="text-[10px] text-slate-400 uppercase font-semibold">Duration</p>
                          <p className="font-bold text-cyan-400">{trip.days} Days</p>
                        </div>
                      )}
                      {trip.travelers > 0 && (
                        <div>
                          <p className="text-[10px] text-slate-400 uppercase font-semibold">Party</p>
                          <p className="font-bold text-slate-200">{trip.travelers} Guests</p>
                        </div>
                      )}
                      <div>
                        <p className="text-[10px] text-slate-400 uppercase font-semibold">Status</p>
                        <p className="font-bold text-emerald-400">Ready</p>
                      </div>
                    </div>
                  </Link>

                  <div className="flex items-center justify-between pt-3 border-t border-white/5 text-xs">
                    <span className="text-slate-500 text-[11px]">
                      {trip.createdAt ? new Date(trip.createdAt.toDate?.() || trip.createdAt).toLocaleDateString() : 'Active'}
                    </span>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={(e) => handleDeleteTrip(e, trip.id)}
                        disabled={deleting}
                        className={`p-2 rounded-lg text-xs transition-all ${
                          deleteConfirm === trip.id
                            ? 'bg-rose-600 text-white shadow-lg'
                            : 'text-slate-400 hover:text-rose-400 hover:bg-rose-500/10'
                        }`}
                        title={deleteConfirm === trip.id ? 'Click again to confirm' : 'Delete'}
                      >
                        <FaTrash />
                      </button>

                      <Link
                        to={`/trip/${trip.id}`}
                        className="px-3.5 py-1.5 rounded-lg btn-cinema-outline text-xs font-semibold"
                      >
                        View Plan
                      </Link>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {tripsToDisplay < validTrips.length && (
              <div className="text-center pt-4">
                <button
                  onClick={loadMore}
                  className="btn-cinema-outline px-8 py-3 text-xs font-bold"
                >
                  Load More ({validTrips.length - tripsToDisplay} remaining)
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-20 glass-cinema rounded-3xl border border-white/10 max-w-2xl mx-auto">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-cyan-500/20 to-purple-500/20 flex items-center justify-center text-2xl text-cyan-400 mx-auto mb-4 border border-cyan-500/30">
              <FaPlaneDeparture />
            </div>
            <h3 className="text-2xl font-bold text-white font-display mb-2">No saved trips yet</h3>
            <p className="text-slate-400 text-sm max-w-md mx-auto mb-6">
              Use our AI studio to design your first flight, stay, and day-by-day travel itinerary.
            </p>
            <Link
              to="/plan-trip"
              className="btn-cinema-primary px-7 py-3.5 text-xs font-bold inline-flex items-center gap-2"
            >
              <FaPlus className="text-xs" />
              <span>Create Your First Itinerary</span>
            </Link>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default MyTripsPage;

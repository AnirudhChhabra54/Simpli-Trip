import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getTripById, toggleTripSharing, updateTrip } from '../services/firestore';
import Layout from '../components/Layout';
import TripForm from '../components/TripForm';
import ContextEnrichmentPanel from '../components/ContextEnrichmentPanel';
import ItineraryView from '../components/ItineraryView';
import { FaArrowLeft, FaEdit, FaTimes, FaMapMarkerAlt, FaLock, FaGlobe } from 'react-icons/fa';

const TripDetailPage = () => {
  const { id } = useParams();
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const loadTrip = useCallback(async () => {
    try {
      const tripData = await getTripById(id);
      if (tripData) {
        setTrip(tripData);
      } else {
        setError('Trip not found or access denied');
      }
    } catch (err) {
      setError('Failed to load trip details');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadTrip();
  }, [loadTrip]);

  const handleToggleSharing = async () => {
    try {
      const nextShared = !trip.shared;
      await toggleTripSharing(id, nextShared);
      setTrip({ ...trip, shared: nextShared });
      if (nextShared) {
        navigator.clipboard?.writeText(window.location.href);
        setCopied(true);
        setTimeout(() => setCopied(false), 3000);
      }
    } catch (err) {
      setError('Failed to update sharing settings');
    }
  };

  const handleUpdateTrip = async (tripData) => {
    try {
      await updateTrip(id, tripData);
      setTrip({ ...trip, ...tripData });
      setIsEditing(false);
    } catch (err) {
      setError('Failed to update trip');
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500 mb-4 mx-auto" />
            <p className="text-sm text-slate-300 font-semibold">Loading itinerary blueprint...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error || !trip) {
    return (
      <Layout>
        <div className="max-w-2xl mx-auto py-20 text-center glass-cinema rounded-3xl p-8 border border-white/10">
          <h2 className="text-2xl font-bold text-white mb-2 font-display">Itinerary Not Found</h2>
          <p className="text-slate-400 text-sm mb-6">{error || 'This journey could not be located.'}</p>
          <Link to="/my-trips" className="btn-cinema-primary px-6 py-3 text-xs font-bold inline-flex items-center gap-2">
            <FaArrowLeft className="text-xs" />
            <span>Return to My Trips</span>
          </Link>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Navigation & Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <Link
            to="/my-trips"
            className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-cyan-400 transition-colors"
          >
            <FaArrowLeft className="text-xs" />
            <span>Back to All Journeys</span>
          </Link>

          <div className="flex items-center gap-3">
            <button
              onClick={handleToggleSharing}
              className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${
                trip.shared
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/10'
                  : 'glass-pill text-slate-300 hover:text-white'
              }`}
            >
              {trip.shared ? <FaGlobe className="text-cyan-400" /> : <FaLock className="text-slate-400" />}
              <span>{trip.shared ? (copied ? '✓ Link Copied!' : 'Publicly Shared') : 'Share Trip'}</span>
            </button>

            <button
              onClick={() => setIsEditing(!isEditing)}
              className="btn-cinema-outline px-4 py-2 text-xs font-bold flex items-center gap-2"
            >
              {isEditing ? <FaTimes className="text-xs" /> : <FaEdit className="text-xs" />}
              <span>{isEditing ? 'Cancel Edit' : 'Edit Blueprint'}</span>
            </button>
          </div>
        </div>

        {/* Title Header Card */}
        <div className="glass-cinema rounded-3xl p-8 border border-white/10 relative overflow-hidden">
          <div className="flex items-center gap-2 text-cyan-400 text-xs font-bold uppercase tracking-wider mb-2">
            <FaMapMarkerAlt />
            <span>{trip.destination || trip.destinations?.[0] || 'Custom Destination'}</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white font-display leading-tight">
            {trip.name}
          </h1>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-6 border-t border-white/10 text-xs">
            <div>
              <p className="text-slate-400 uppercase tracking-wider font-semibold text-[10px]">Estimated Budget</p>
              <p className="text-lg font-bold text-white mt-0.5">
                {trip.budget ? `₹${Number(trip.budget).toLocaleString('en-IN')}` : 'Flexible'}
              </p>
            </div>
            <div>
              <p className="text-slate-400 uppercase tracking-wider font-semibold text-[10px]">Duration</p>
              <p className="text-lg font-bold text-cyan-400 mt-0.5">{trip.days || 3} Days</p>
            </div>
            <div>
              <p className="text-slate-400 uppercase tracking-wider font-semibold text-[10px]">Travelers</p>
              <p className="text-lg font-bold text-slate-200 mt-0.5">{trip.travelers || 2} People</p>
            </div>
            <div>
              <p className="text-slate-400 uppercase tracking-wider font-semibold text-[10px]">Privacy</p>
              <p className="text-lg font-bold text-emerald-400 mt-0.5">{trip.shared ? 'Public' : 'Private'}</p>
            </div>
          </div>
        </div>

        {/* Edit Form or Itinerary Display */}
        {isEditing ? (
          <div className="glass-cinema rounded-3xl p-8 border border-white/10">
            <TripForm onSubmit={handleUpdateTrip} initialData={trip} onCancel={() => setIsEditing(false)} />
          </div>
        ) : (
          <>
            {/* Context Enrichment Panel */}
            <ContextEnrichmentPanel
              showDetails
              destination={trip.destination || trip.destinations?.[0] || ''}
              tripDates={[trip.startDate, trip.endDate].filter(Boolean)}
              budget={trip.budget || null}
              preferences={trip.preferences || []}
            />

            {/* Itinerary Markdown View */}
            {(trip.itinerary?.markdown || trip.itinerary) && (
              <div className="glass-cinema rounded-3xl p-8 border border-white/10">
                <ItineraryView
                  markdown={trip.itinerary?.markdown || (typeof trip.itinerary === 'string' ? trip.itinerary : '')}
                  destination={trip.destination}
                  budget={trip.budget || null}
                />
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  );
};

export default TripDetailPage;
import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { getTripById, toggleTripSharing, updateTrip } from '../services/firestore';
import { useUser } from '../context/UserContext';
import Layout from '../components/Layout';
import TripForm from '../components/TripForm';
import AIRecommender from '../components/AIRecommender';

const TripDetailPage = () => {
  const { id } = useParams();
  const { user } = useUser();
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [error, setError] = useState('');

  const loadTrip = useCallback(async () => {
    try {
      const tripData = await getTripById(id);
      if (tripData && tripData.userId === user.uid) {
        setTrip(tripData);
      } else {
        setError('Trip not found or access denied');
      }
    } catch (error) {
      setError('Failed to load trip details');
      console.error('Error loading trip:', error);
    } finally {
      setLoading(false);
    }
  }, [id, user]);

  useEffect(() => {
    if (user) {
      loadTrip();
    }
  }, [user, loadTrip]);

  const handleToggleSharing = async () => {
    try {
      await toggleTripSharing(id, !trip.shared);
      setTrip({ ...trip, shared: !trip.shared });
    } catch (error) {
      setError('Failed to update sharing settings');
      console.error('Error toggling sharing:', error);
    }
  };

  const handleUpdateTrip = async (tripData) => {
    try {
      await updateTrip(id, tripData);
      setTrip({ ...trip, ...tripData });
      setIsEditing(false);
    } catch (error) {
      setError('Failed to update trip');
      console.error('Error updating trip:', error);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-screen bg-gray-900 text-white">Loading trip details...</div>;
  }

  if (error || !trip) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-screen bg-gray-900 text-white">
          {error || 'Trip not found'}
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold">{trip.name}</h1>
          <button 
            onClick={() => setIsEditing(!isEditing)} 
            className="bg-gray-700 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded-lg"
          >
            {isEditing ? 'Cancel' : 'Edit Trip'}
          </button>
        </div>

        {error && <p className="text-red-500 mb-4">{error}</p>}

        {isEditing ? (
          <TripForm onSubmit={handleUpdateTrip} initialData={trip} onCancel={() => setIsEditing(false)} />
        ) : (
          <div className="bg-gray-800 p-6 rounded-lg mb-8">
            <p><strong>Budget:</strong> ${trip.budget}</p>
            <p><strong>Destinations:</strong> {trip.destinations?.join(', ') || 'Not set'}</p>
            <p><strong>Status:</strong> {trip.shared ? 'Shared' : 'Private'}</p>
          </div>
        )}

        <div className="mb-8">
          <button 
            onClick={handleToggleSharing} 
            className={`font-bold py-2 px-4 rounded-lg ${trip.shared ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'}`}
          >
            {trip.shared ? 'Disable Sharing' : 'Enable Sharing'}
          </button>
          {trip.shared && <p className="text-sm mt-2">Sharing is enabled. Anyone with the link can view this trip.</p>}
        </div>

        <AIRecommender type="trip" />
      </div>
    </Layout>
  );
};

export default TripDetailPage;
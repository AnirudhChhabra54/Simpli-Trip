import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { getTripsByUserId, addTrip } from '../services/firestore';
import { useUser } from '../context/UserContext';
import Layout from '../components/Layout';
import TripForm from '../components/TripForm';
import AIRecommender from '../components/AIRecommender';

const DashboardPage = () => {
  const { user } = useUser();
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [error, setError] = useState('');

  const loadTrips = useCallback(async () => {
    try {
      const userTrips = await getTripsByUserId(user.uid);
      setTrips(userTrips);
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
  }, [user, loadTrips]);

  const handleCreateTrip = async (tripData) => {
    try {
      const newTrip = {
        ...tripData,
        userId: user.uid,
        destinations: [],
        shared: false,
        createdAt: new Date(),
      };
      
      const docRef = await addTrip(newTrip);
      setTrips([...trips, { ...newTrip, id: docRef.id }]);
      setIsModalOpen(false);
    } catch (error) {
      setError('Failed to create trip');
      console.error('Error creating trip:', error);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-screen bg-gray-900 text-white">Loading trips...</div>;
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">My Trips</h1>
        {error && <p className="text-red-500 mb-4">{error}</p>}
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-2 px-4 rounded-lg mb-8"
        >
          Create New Trip
        </button>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {trips.map((trip) => (
            <Link to={`/trip/${trip.id}`} key={trip.id}>
              <div className="bg-gray-800 p-6 rounded-lg hover:bg-gray-700 transition-colors">
                <h2 className="text-2xl font-bold">{trip.name}</h2>
                <p className="text-gray-400">Budget: ${trip.budget}</p>
              </div>
            </Link>
          ))}
        </div>

        <AIRecommender type="dashboard" />
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <TripForm onSubmit={handleCreateTrip} onCancel={() => setIsModalOpen(false)} />
        </div>
      )}
    </Layout>
  );
};

export default DashboardPage;
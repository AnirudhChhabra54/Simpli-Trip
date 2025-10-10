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
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold">My Trips</h1>
          <div className="flex gap-4">
            <Link
              to="/plan-trip"
              className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white font-bold py-3 px-6 rounded-lg transition-all shadow-lg hover:shadow-xl flex items-center gap-2"
            >
              <span>🤖</span>
              <span>AI Trip Planner</span>
            </Link>
            <button
              onClick={() => setIsModalOpen(true)}
              className="bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg transition-colors"
            >
              Quick Create
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/20 border border-red-500 rounded-lg">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {trips.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {trips.map((trip) => (
              <Link to={`/trip/${trip.id}`} key={trip.id}>
                <div className="bg-gray-800 p-6 rounded-lg hover:bg-gray-700 transition-all hover:shadow-lg hover:shadow-cyan-500/20 border border-gray-700 hover:border-cyan-500">
                  <h2 className="text-2xl font-bold mb-2">{trip.name}</h2>
                  {trip.destination && (
                    <p className="text-cyan-400 mb-2">📍 {trip.destination}</p>
                  )}
                  <div className="flex justify-between items-center text-gray-400 text-sm">
                    <span>Budget: ₹{trip.budget?.toLocaleString('en-IN')}</span>
                    {trip.days && <span>{trip.days} days</span>}
                  </div>
                  {trip.estimatedCost && (
                    <div className="mt-3 pt-3 border-t border-gray-700">
                      <p className="text-sm text-gray-400">
                        Estimated: <span className="text-white font-semibold">₹{trip.estimatedCost.toLocaleString('en-IN')}</span>
                      </p>
                    </div>
                  )}
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-16 bg-gray-800 rounded-xl">
            <div className="text-6xl mb-4">✈️</div>
            <h3 className="text-2xl font-bold text-white mb-2">No trips yet</h3>
            <p className="text-gray-400 mb-6">Start planning your dream vacation with our AI-powered trip planner!</p>
            <Link
              to="/plan-trip"
              className="inline-block bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white font-bold py-3 px-8 rounded-lg transition-all shadow-lg"
            >
              Plan Your First Trip
            </Link>
          </div>
        )}

        <AIRecommender type="dashboard" />
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <TripForm onSubmit={handleCreateTrip} onCancel={() => setIsModalOpen(false)} />
        </div>
      )}
    </Layout>
  );
};

export default DashboardPage;
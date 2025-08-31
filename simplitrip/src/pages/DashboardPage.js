import React, { useState, useEffect } from 'react';
import { useUser } from '../context/UserContext';
import { getTripsByUserId, toggleTripSharing } from '../services/firestore';
import { useNavigate } from 'react-router-dom';
import { logoutUser } from '../services/auth';

const DashboardPage = () => {
  const { user } = useUser();
  const [trips, setTrips] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTrips = async () => {
      if (user) {
        const userTrips = await getTripsByUserId(user.uid);
        setTrips(userTrips);
      }
    };
    fetchTrips();
  }, [user]);

  const handleToggleSharing = async (id, isShared) => {
    await toggleTripSharing(id, !isShared);
    setTrips(trips.map(trip => 
      trip.id === id ? { ...trip, isShared: !isShared } : trip
    ));
  };

  const handleLogout = async () => {
    try {
      await logoutUser();
      navigate('/');
    } catch (error) {
      alert('Logout failed: ' + error.message);
    }
  };

  return (
    <div>
      <h2 className="text-3xl font-bold mb-4">Your Trips</h2>
      <button onClick={handleLogout} className="bg-red-500 text-white px-4 py-2 rounded">
        Logout
      </button>
      <ul className="mt-4">
        {trips.map((trip) => (
          <li key={trip.id} className="p-4 border-b">
            <h3>{trip.title}</h3>
            <p>{trip.description}</p>
            <button 
              onClick={() => handleToggleSharing(trip.id, trip.isShared)}
              className="bg-blue-500 text-white px-2 py-1 rounded"
            >
              {trip.isShared ? 'Unshare' : 'Share'}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default DashboardPage;
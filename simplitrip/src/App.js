import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import TripDetailPage from './pages/TripDetailPage';
import { useUser } from './context/UserContext';
import Layout from './components/Layout';


//Landing page imported 
import LandingPage from './pages/LandingPage';
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useUser();

  if (loading) {
    return <div>Loading...</div>; // Or a spinner component
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  return children;
};

const App = () => {
  const { user, loading } = useUser();

  if (loading) {
    return <div>Loading...</div>; // Or a global spinner
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/" element={user ? <Navigate to="/dashboard" /> : <Navigate to="/login" />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/trip/:id" element={<ProtectedRoute><TripDetailPage /></ProtectedRoute>} />
      </Routes>
    </Layout>
  );
};

export default App;
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useUser } from '../context/UserContext';
import Layout from '../components/Layout';
import AIRecommender from '../components/AIRecommender';

const DashboardPage = () => {
  const { user } = useUser();
  const [error, setError] = useState('');

  const quickActions = [
    {
      icon: '✈️',
      title: 'Plan a Trip',
      description: 'Create a personalized itinerary',
      link: '/plan-trip',
      bgGradient: 'from-blue-600/20 to-cyan-600/20',
      accentColor: 'text-blue-300'
    },
    {
      icon: '🤖',
      title: 'AI Chat',
      description: 'Get travel recommendations',
      link: '/chat',
      bgGradient: 'from-purple-600/20 to-pink-600/20',
      accentColor: 'text-purple-300'
    },
    {
      icon: '🗺️',
      title: 'My Trips',
      description: 'View and manage your trips',
      link: '/my-trips',
      bgGradient: 'from-cyan-600/20 to-blue-600/20',
      accentColor: 'text-cyan-300'
    },
  ];

  const features = [
    {
      icon: '🌍',
      title: 'Global Destinations',
      description: 'Explore thousands of destinations worldwide'
    },
    {
      icon: '💰',
      title: 'Budget Planning',
      description: 'Smart budget allocation for your trips'
    },
    {
      icon: '📅',
      title: 'Itinerary Builder',
      description: 'AI-powered day-by-day planning'
    },
    {
      icon: '☀️',
      title: 'Weather Insights',
      description: 'Know the weather before you go'
    },
    {
      icon: '👥',
      title: 'Group Travel',
      description: 'Plan trips for multiple travelers'
    },
    {
      icon: '🎯',
      title: 'Smart Recommendations',
      description: 'Get personalized activity suggestions'
    },
  ];

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center"
        >
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
            Welcome back, <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">{user?.displayName?.split(' ')[0] || 'Traveler'}!</span>
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Ready to plan your next adventure? Use SimpliTrip's AI-powered tools to create the perfect itinerary.
          </p>
        </motion.div>

        {/* Error Message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-8"
          >
            <div className="p-4 bg-red-900/30 border-l-4 border-red-500 rounded-r-lg">
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
          </motion.div>
        )}

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-16"
        >
          <h2 className="text-3xl font-bold text-white mb-8">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {quickActions.map((action, idx) => (
              <motion.div
                key={idx}
                whileHover={{ y: -5 }}
                transition={{ duration: 0.3 }}
              >
                <Link to={action.link} className="group block">
                  <div className={`relative h-full bg-gradient-to-br ${action.bgGradient} border border-gray-700 rounded-2xl p-8 hover:border-cyan-500/50 transition-all duration-300 overflow-hidden cursor-pointer`}>
                    <div className="absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-300"></div>
                    <div className="relative z-10">
                      <div className="flex items-center justify-between mb-6">
                        <span className="text-5xl">{action.icon}</span>
                        <span className="text-gray-400 group-hover:translate-x-2 transition-transform">→</span>
                      </div>
                      <h3 className="text-2xl font-bold text-white mb-2">{action.title}</h3>
                      <p className="text-gray-300">{action.description}</p>
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Features Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-16"
        >
          <h2 className="text-3xl font-bold text-white mb-8">Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * idx }}
                className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-6 border border-gray-700 hover:border-cyan-500/30 transition-all"
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* AI Recommender Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-16"
        >
          <AIRecommender />
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 bg-gradient-to-r from-cyan-600/20 to-purple-600/20 rounded-2xl border border-cyan-500/30 text-center mb-16"
        >
          <h2 className="text-3xl font-bold text-white mb-4">Ready to explore?</h2>
          <p className="text-gray-300 mb-8">Start planning your next adventure with our AI-powered trip planner</p>
          <Link
            to="/plan-trip"
            className="inline-flex items-center justify-center bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white font-bold py-3 px-8 rounded-xl transition-all shadow-lg hover:shadow-cyan-500/30"
          >
            <span className="mr-2">✨</span>
            Start Planning Now
          </Link>
        </motion.div>
      </div>
    </Layout>
  );
};

export default DashboardPage;

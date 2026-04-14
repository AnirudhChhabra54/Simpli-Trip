import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useUser } from '../context/UserContext';
import Layout from '../components/Layout';
import { getTripsByUserId } from '../services/firestore';
import {
  FaPlaneDeparture,
  FaRobot,
  FaMapMarkedAlt,
  FaArrowRight,
  FaMoneyBillWave,
  FaPlus,
} from 'react-icons/fa';

const DashboardPage = () => {
  const { user } = useUser();
  const navigate = useNavigate();
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    if (user?.uid) {
      getTripsByUserId(user.uid)
        .then((data) => {
          if (mounted) setTrips(data || []);
        })
        .catch(() => {})
        .finally(() => {
          if (mounted) setLoading(false);
        });
    } else {
      setLoading(false);
    }
    return () => {
      mounted = false;
    };
  }, [user?.uid]);

  const totalBudget = trips.reduce((sum, t) => sum + (Number(t.budget) || 0), 0);
  const uniquePlaces = new Set((trips || []).map((t) => t.destination).filter(Boolean));

  const stats = [
    { label: 'Journeys Planned', value: trips.length, icon: FaPlaneDeparture, color: 'text-cyan-400', bg: 'bg-cyan-500/10' },
    { label: 'Destinations Visited', value: uniquePlaces.size, icon: FaMapMarkedAlt, color: 'text-indigo-400', bg: 'bg-indigo-500/10' },
    { label: 'Tracked Budget', value: totalBudget ? `₹${totalBudget.toLocaleString('en-IN')}` : '₹0', icon: FaMoneyBillWave, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    { label: 'AI Intelligence', value: 'Active', icon: FaRobot, color: 'text-purple-400', bg: 'bg-purple-500/10' },
  ];

  const quickActions = [
    {
      title: 'Plan a New Journey',
      desc: 'Use AI to generate day-by-day itineraries with live flights, stays, and routes.',
      link: '/plan-trip',
      btnText: 'Start Planning',
      icon: FaPlaneDeparture,
      gradient: 'from-cyan-500/20 via-sky-500/10 to-transparent',
      borderColor: 'border-cyan-500/30',
      badge: 'Autonomous AI',
    },
    {
      title: 'AI Travel Concierge',
      desc: 'Chat with our smart LLM about hidden cafes, packing advice, and local gems.',
      link: '/chat',
      btnText: 'Open Chat Studio',
      icon: FaRobot,
      gradient: 'from-purple-500/20 via-indigo-500/10 to-transparent',
      borderColor: 'border-purple-500/30',
      badge: '24/7 Companion',
    },
    {
      title: 'My Saved Itineraries',
      desc: 'Review, edit, export to PDF, and share your generated travel blueprints.',
      link: '/my-trips',
      btnText: 'View Saved Trips',
      icon: FaMapMarkedAlt,
      gradient: 'from-blue-500/20 via-teal-500/10 to-transparent',
      borderColor: 'border-blue-500/30',
      badge: `${trips.length} Saved`,
    },
  ];

  const trendingDestinations = [
    {
      name: 'Goa',
      tag: 'Sun & Surf',
      price: '₹14,500',
      image: 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?q=80&w=600&auto=format&fit=crop',
    },
    {
      name: 'Ladakh',
      tag: 'Himalayan Pass',
      price: '₹28,900',
      image: 'https://images.unsplash.com/photo-1581793745862-99fde7fa73d2?q=80&w=600&auto=format&fit=crop',
    },
    {
      name: 'Kerala',
      tag: 'Houseboat Bliss',
      price: '₹18,200',
      image: 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?q=80&w=600&auto=format&fit=crop',
    },
    {
      name: 'Jaipur',
      tag: 'Royal Heritage',
      price: '₹16,400',
      image: 'https://images.unsplash.com/photo-1599661046289-e31897846e41?q=80&w=600&auto=format&fit=crop',
    },
  ];

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500 mb-4 mx-auto" />
            <p className="text-sm font-semibold text-slate-300">Loading your travel studio...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-10">
        {/* Welcome Banner */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative rounded-3xl p-8 sm:p-10 glass-cinema border border-white/10 overflow-hidden"
        >
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-pill text-xs font-semibold text-cyan-400 mb-3 border border-cyan-500/30">
                <span>✨ TRAVELER DASHBOARD</span>
              </div>
              <h1 className="text-3xl sm:text-4xl font-extrabold text-white font-display">
                Welcome back,{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-400">
                  {user?.displayName || 'Travel Explorer'}
                </span>
              </h1>
              <p className="text-slate-400 text-sm mt-1 max-w-xl font-light">
                Your personal travel command center. Launch AI planning sessions, review saved itineraries, or explore trending escapes.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <Link
                to="/plan-trip"
                className="btn-cinema-primary px-6 py-3 text-xs sm:text-sm font-bold flex items-center gap-2 shrink-0 shadow-lg shadow-cyan-500/20"
              >
                <FaPlus className="text-xs" />
                <span>New Trip</span>
              </Link>
            </div>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((item, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="glass-cinema-card rounded-2xl p-5 border border-white/5 flex items-center justify-between"
            >
              <div>
                <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">{item.label}</p>
                <p className="text-2xl font-extrabold text-white font-display mt-1">{item.value}</p>
              </div>
              <div className={`w-11 h-11 rounded-xl ${item.bg} ${item.color} flex items-center justify-center text-lg`}>
                <item.icon />
              </div>
            </motion.div>
          ))}
        </div>

        {/* Quick Launch Studios */}
        <div>
          <h2 className="text-2xl font-bold text-white font-display mb-4">Quick Studio Access</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {quickActions.map((action, idx) => (
              <motion.div
                key={idx}
                whileHover={{ y: -6 }}
                className={`glass-cinema-card rounded-3xl p-7 border ${action.borderColor} flex flex-col justify-between group cursor-pointer`}
                onClick={() => navigate(action.link)}
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center text-xl text-cyan-400 shadow-md">
                      <action.icon />
                    </div>
                    <span className="text-[11px] font-bold px-3 py-1 rounded-full glass-pill text-slate-300">
                      {action.badge}
                    </span>
                  </div>

                  <h3 className="text-xl font-bold text-white font-display mb-2 group-hover:text-cyan-400 transition-colors">
                    {action.title}
                  </h3>
                  <p className="text-slate-400 text-xs sm:text-sm leading-relaxed">
                    {action.desc}
                  </p>
                </div>

                <div className="mt-6 pt-4 border-t border-white/5 flex items-center justify-between text-xs font-bold text-cyan-400">
                  <span>{action.btnText}</span>
                  <FaArrowRight className="text-[10px] group-hover:translate-x-1 transition-transform" />
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Trending Escapes */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-white font-display">Trending Destinations</h2>
              <p className="text-xs text-slate-400">1-click automated AI itinerary generators</p>
            </div>
            <Link to="/plan-trip" className="text-xs font-bold text-cyan-400 hover:text-cyan-300 flex items-center gap-1">
              <span>View All</span>
              <FaArrowRight className="text-[10px]" />
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {trendingDestinations.map((dest, i) => (
              <motion.div
                key={i}
                whileHover={{ y: -5 }}
                className="glass-cinema-card rounded-2xl overflow-hidden border border-white/10 group cursor-pointer flex flex-col"
                onClick={() => navigate(`/plan-trip?prompt=${encodeURIComponent(`Trip to ${dest.name}`)}`)}
              >
                <div className="relative h-40 overflow-hidden">
                  <img
                    src={dest.image}
                    alt={dest.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#080f24] via-transparent to-transparent" />
                  <span className="absolute top-3 left-3 px-2.5 py-0.5 rounded-full glass-pill text-[10px] font-bold text-white">
                    {dest.tag}
                  </span>
                </div>
                <div className="p-4 flex items-center justify-between">
                  <div>
                    <h3 className="font-bold text-white font-display text-lg">{dest.name}</h3>
                    <p className="text-xs text-slate-400">Avg. 4-day budget</p>
                  </div>
                  <span className="text-sm font-bold text-cyan-400">{dest.price}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default DashboardPage;

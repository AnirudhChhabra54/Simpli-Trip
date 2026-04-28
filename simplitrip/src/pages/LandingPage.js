import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  FaMagic,
  FaArrowRight,
  FaMoneyBillWave,
  FaRoute,
  FaBrain,
  FaCloudSun,
  FaShieldAlt,
  FaCompass,
  FaPlaneDeparture,
  FaHotel,
  FaCheckCircle,
} from 'react-icons/fa';
import CinematicHeroCanvas from '../components/CinematicHeroCanvas';

const LandingPage = () => {
  const navigate = useNavigate();
  const [promptInput, setPromptInput] = useState('');

  const suggestedPrompts = [
    { text: '5 days in snowy Gulmarg with cozy fireside stays', tag: '❄️ Winter Escape' },
    { text: 'Romantic Goa beach villa getaway under ₹40,000', tag: '🏖️ Coastal' },
    { text: 'Heritage royal tour of Jaipur & Udaipur palaces', tag: '🏰 Heritage' },
    { text: 'Kerala backwaters houseboat & Munnar tea hills', tag: '🌴 Nature' },
  ];

  const handlePromptSubmit = (e) => {
    e.preventDefault();
    if (promptInput.trim()) {
      navigate(`/login?prompt=${encodeURIComponent(promptInput.trim())}`);
    } else {
      navigate('/login?signup=true');
    }
  };

  const handlePromptClick = (text) => {
    setPromptInput(text);
  };

  const destinations = [
    {
      id: 'goa',
      name: 'Goa',
      region: 'Coastal Paradise',
      image: 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?q=80&w=1000&auto=format&fit=crop',
      match: '98%',
      flight: '₹4,200',
      stay: '₹3,500/nt',
      weather: '28°C Sunny',
    },
    {
      id: 'ladakh',
      name: 'Ladakh',
      region: 'Himalayan Frontier',
      image: 'https://images.unsplash.com/photo-1581793745862-99fde7fa73d2?q=80&w=1000&auto=format&fit=crop',
      match: '96%',
      flight: '₹6,800',
      stay: '₹4,200/nt',
      weather: '12°C Crisp',
    },
    {
      id: 'kerala',
      name: 'Kerala',
      region: 'God’s Own Country',
      image: 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?q=80&w=1000&auto=format&fit=crop',
      match: '99%',
      flight: '₹5,100',
      stay: '₹3,800/nt',
      weather: '26°C Lush',
    },
    {
      id: 'jaipur',
      name: 'Jaipur & Udaipur',
      region: 'Royal Rajasthan',
      image: 'https://images.unsplash.com/photo-1599661046289-e31897846e41?q=80&w=1000&auto=format&fit=crop',
      match: '95%',
      flight: '₹3,900',
      stay: '₹4,500/nt',
      weather: '25°C Pleasant',
    },
    {
      id: 'kashmir',
      name: 'Kashmir',
      region: 'Paradise on Earth',
      image: 'https://images.unsplash.com/photo-1566837945700-30057527ade0?q=80&w=1000&auto=format&fit=crop',
      match: '97%',
      flight: '₹5,600',
      stay: '₹4,900/nt',
      weather: '14°C Alpine',
    },
    {
      id: 'manali',
      name: 'Manali & Spiti',
      region: 'Pine Valleys',
      image: 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?q=80&w=1000&auto=format&fit=crop',
      match: '94%',
      flight: '₹4,800',
      stay: '₹2,900/nt',
      weather: '16°C Breezy',
    },
  ];

  const features = [
    {
      icon: FaBrain,
      title: 'Neural Prompt Studio',
      desc: 'Type natural human thoughts. Our LLM understands constraints, vibes, and budgets effortlessly.',
      tag: 'Generative AI',
      color: 'text-cyan-400',
      bgGlow: 'rgba(6, 182, 212, 0.15)',
    },
    {
      icon: FaMoneyBillWave,
      title: 'Real-Time Price Intelligence',
      desc: 'Predictive budget modeling for flights, boutique hotels, and dining with dynamic savings tips.',
      tag: 'Live Arbitrage',
      color: 'text-emerald-400',
      bgGlow: 'rgba(16, 185, 129, 0.15)',
    },
    {
      icon: FaRoute,
      title: 'Geospatial Route Weaver',
      desc: 'Graph-optimized day-by-day itineraries that minimize transit fatigue and maximize experience time.',
      tag: 'TSP Optimization',
      color: 'text-indigo-400',
      bgGlow: 'rgba(99, 102, 241, 0.15)',
    },
    {
      icon: FaCompass,
      title: 'RAG Knowledge Graph',
      desc: 'Curated by local travel experts, historical insights, and real-time hidden gem discoveries.',
      tag: 'Verified Data',
      color: 'text-violet-400',
      bgGlow: 'rgba(139, 92, 246, 0.15)',
    },
    {
      icon: FaCloudSun,
      title: 'Microclimate Predictor',
      desc: 'Smart activity scheduling based on live seasonal trends, golden hours, and crowd densities.',
      tag: 'Real-Time',
      color: 'text-amber-400',
      bgGlow: 'rgba(245, 158, 11, 0.15)',
    },
    {
      icon: FaShieldAlt,
      title: 'Instant Offline Passport',
      desc: 'Export high-definition PDF travel guides, interactive GPS links, and offline mobile itineraries.',
      tag: '1-Click PDF',
      color: 'text-pink-400',
      bgGlow: 'rgba(236, 72, 153, 0.15)',
    },
  ];

  return (
    <div className="relative min-h-screen bg-[#040714] text-slate-100 overflow-x-hidden selection:bg-cyan-500 selection:text-black">
      {/* Dynamic Ambient Aurora Background Orbs */}
      <div className="aurora-mesh w-[650px] h-[650px] bg-cyan-600/15 top-[-10%] left-[-10%] pointer-events-none" />
      <div className="aurora-mesh w-[700px] h-[700px] bg-purple-600/15 top-[20%] right-[-15%] pointer-events-none" />
      <div className="aurora-mesh w-[600px] h-[600px] bg-indigo-600/10 bottom-[10%] left-[20%] pointer-events-none" />

      {/* Floating Glassmorphic Header */}
      <header className="fixed top-0 left-0 right-0 z-50 px-4 py-4 transition-all duration-300">
        <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-3.5 rounded-full glass-cinema border border-white/10 shadow-2xl backdrop-blur-2xl">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/30 group-hover:scale-105 transition-transform">
              <FaCompass className="text-white text-lg animate-spin" style={{ animationDuration: '20s' }} />
            </div>
            <div className="text-xl font-bold tracking-tight font-display">
              <span className="text-white">Simpli</span>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-400">Trip</span>
              <span className="inline-block ml-1.5 px-1.5 py-0.5 text-[9px] font-semibold bg-cyan-500/20 text-cyan-300 rounded border border-cyan-500/30">AI</span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
            <a href="#explore" className="hover:text-cyan-400 transition-colors">Destinations</a>
            <a href="#features" className="hover:text-cyan-400 transition-colors">AI Studio</a>
            <a href="#preview" className="hover:text-cyan-400 transition-colors">Live Preview</a>
          </nav>

          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="px-5 py-2 text-sm font-semibold text-slate-300 hover:text-white transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/login?signup=true"
              className="btn-cinema-primary px-5 py-2 text-sm flex items-center gap-2"
            >
              <span>Get Started</span>
              <FaArrowRight className="text-xs" />
            </Link>
          </div>
        </div>
      </header>

      {/* HERO SECTION WITH THREE.JS 3D CANVAS */}
      <section className="relative min-h-screen flex items-center justify-center pt-32 pb-20 px-4 overflow-hidden">
        {/* 3D WebGL Background Canvas */}
        <CinematicHeroCanvas />

        {/* Hero Content Overlay */}
        <div className="relative z-10 max-w-5xl mx-auto text-center mt-6">
          {/* Glowing Top Pill */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-pill text-xs font-semibold text-cyan-300 mb-6 border border-cyan-500/30 shadow-lg shadow-cyan-500/10"
          >
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span>Autonomous AI Travel Studio • 2026 Engine</span>
          </motion.div>

          {/* Majestic Hero Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 25 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1 }}
            className="text-5xl sm:text-7xl lg:text-8xl font-extrabold tracking-tight leading-[1.08] mb-6 font-display"
          >
            Where Dream Journeys <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400 glow-text-cyan">
              Come to Life.
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="max-w-2xl mx-auto text-lg sm:text-xl text-slate-300 font-light leading-relaxed mb-10"
          >
            Speak your wanderlust in plain English. Our neural engine balances flights, boutique stays, secret sunset spots, and budgets in seconds.
          </motion.p>

          {/* Interactive Cinematic Prompt Console */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="max-w-3xl mx-auto"
          >
            <form
              onSubmit={handlePromptSubmit}
              className="relative glass-cinema p-2 sm:p-2.5 rounded-3xl border border-white/15 shadow-2xl backdrop-blur-2xl flex flex-col sm:flex-row items-center gap-2 group focus-within:border-cyan-500/50 transition-all"
            >
              <div className="flex items-center gap-3 w-full px-4 py-2">
                <FaMagic className="text-cyan-400 text-lg shrink-0" />
                <input
                  type="text"
                  value={promptInput}
                  onChange={(e) => setPromptInput(e.target.value)}
                  placeholder="Where do you want to wander? (e.g. 5 days in serene Kerala with beachside cafes)"
                  className="w-full bg-transparent text-slate-100 placeholder:text-slate-400 text-sm sm:text-base focus:outline-none"
                />
              </div>
              <button
                type="submit"
                className="w-full sm:w-auto btn-cinema-primary px-7 py-3.5 text-sm sm:text-base flex items-center justify-center gap-2 whitespace-nowrap shrink-0"
              >
                <span>Plan My Trip</span>
                <FaArrowRight className="text-xs" />
              </button>
            </form>

            {/* Suggested Prompt Chips */}
            <div className="mt-4 flex flex-wrap items-center justify-center gap-2 text-xs">
              <span className="text-slate-400 font-medium mr-1">Inspire me:</span>
              {suggestedPrompts.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => handlePromptClick(p.text)}
                  className="px-3 py-1.5 rounded-full glass-pill text-slate-300 hover:text-white hover:border-cyan-500/50 hover:bg-white/10 transition-all flex items-center gap-1.5"
                >
                  <span>{p.tag}</span>
                </button>
              ))}
            </div>
          </motion.div>

          {/* Quick Metrics Bar */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.5 }}
            className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto"
          >
            {[
              { label: 'Instant Itineraries', val: '< 3.2s', sub: 'Neural Engine' },
              { label: 'Live Destinations', val: '10,000+', sub: 'Globally Synced' },
              { label: 'Budget Precision', val: '98.4%', sub: 'Real-Time Pricing' },
              { label: 'Route Optimization', val: '100%', sub: 'Multi-Stop TSP' },
            ].map((stat, i) => (
              <div key={i} className="glass-cinema p-4 rounded-2xl border border-white/5 text-center">
                <p className="text-2xl font-black text-white font-display">{stat.val}</p>
                <p className="text-xs text-slate-300 font-medium mt-0.5">{stat.label}</p>
                <p className="text-[10px] text-cyan-400/80 mt-0.5">{stat.sub}</p>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CURATED CINEMATIC DESTINATIONS SHOWCASE */}
      <section id="explore" className="py-24 px-4 relative z-10 max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-pill text-xs font-semibold text-cyan-400 mb-3 border border-cyan-500/30">
              <span>EXPLORE THE WORLD</span>
            </div>
            <h2 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight font-display">
              Curated Wonderlands
            </h2>
          </div>
          <p className="text-slate-400 max-w-md text-sm mt-3 md:mt-0">
            Real-time live prices, climate forecasts, and AI-optimized stays for the world's most breathtaking escapes.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-7">
          {destinations.map((dest, idx) => (
            <motion.div
              key={dest.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: idx * 0.1 }}
              whileHover={{ y: -8 }}
              className="group relative rounded-3xl overflow-hidden glass-cinema-card border border-white/10 cursor-pointer flex flex-col"
              onClick={() => navigate(`/login?prompt=${encodeURIComponent(`Trip to ${dest.name}`)}`)}
            >
              {/* Destination Image with Zoom on Hover */}
              <div className="relative h-64 overflow-hidden">
                <img
                  src={dest.image}
                  alt={dest.name}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ease-out"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#080f24] via-[#080f24]/30 to-transparent" />

                {/* Match Score Badge */}
                <div className="absolute top-4 left-4 px-3 py-1 rounded-full glass-pill text-xs font-bold text-white flex items-center gap-1.5 border border-cyan-500/30">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
                  <span>{dest.match} Match</span>
                </div>

                {/* Weather Pill */}
                <div className="absolute top-4 right-4 px-3 py-1 rounded-full glass-pill text-xs font-semibold text-slate-200 backdrop-blur-md">
                  {dest.weather}
                </div>

                {/* Tag */}
                <div className="absolute bottom-4 left-4">
                  <span className="text-[11px] uppercase tracking-widest font-bold text-cyan-400">
                    {dest.region}
                  </span>
                  <h3 className="text-2xl font-black text-white font-display leading-none mt-1">
                    {dest.name}
                  </h3>
                </div>
              </div>

              {/* Card Meta Footer */}
              <div className="p-5 flex-1 flex flex-col justify-between">
                <div className="grid grid-cols-2 gap-3 mb-4 p-3 rounded-2xl bg-white/[0.03] border border-white/5">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
                      <FaPlaneDeparture className="text-sm" />
                    </div>
                    <div>
                      <p className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Flights from</p>
                      <p className="text-sm font-bold text-white">{dest.flight}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
                      <FaHotel className="text-sm" />
                    </div>
                    <div>
                      <p className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Stays from</p>
                      <p className="text-sm font-bold text-white">{dest.stay}</p>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-1">
                  <span className="text-xs text-slate-400 font-medium">Auto-builds 3-7 day plans</span>
                  <span className="text-xs font-bold text-cyan-400 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                    Explore <FaArrowRight className="text-[10px]" />
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* INTERACTIVE TRIP SIMULATOR PREVIEW */}
      <section id="preview" className="py-20 px-4 relative z-10 max-w-6xl mx-auto">
        <div className="text-center mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-pill text-xs font-semibold text-indigo-400 mb-3 border border-indigo-500/30">
            <span>LIVE EXPERIENCE</span>
          </div>
          <h2 className="text-4xl sm:text-5xl font-extrabold text-white font-display">
            Dynamic Itinerary Architecture
          </h2>
          <p className="text-slate-400 text-sm max-w-xl mx-auto mt-2">
            See how SimpliTrip harmonizes transportation, luxury stays, and curated activities into a cinematic schedule.
          </p>
        </div>

        <div className="glass-cinema rounded-3xl p-6 sm:p-10 border border-white/10 shadow-2xl relative overflow-hidden">
          {/* Inner Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-white/10 gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  AI Generated Itinerary
                </span>
                <span className="text-xs text-slate-400">4 Days • 2 Travelers</span>
              </div>
              <h3 className="text-2xl sm:text-3xl font-extrabold text-white font-display mt-1">
                South Goa: Hidden Coves & Sunset Villas
              </h3>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Total Estimated Cost</p>
                <p className="text-2xl font-black text-cyan-400 font-display">₹28,450</p>
              </div>
            </div>
          </div>

          {/* Timeline Days */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            {/* Day 1 */}
            <div className="glass-cinema-card rounded-2xl p-5 border border-white/5 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-cyan-400 px-2.5 py-1 rounded-lg bg-cyan-500/10">Day 01</span>
                  <span className="text-xs text-slate-400">Arrival & Sunset</span>
                </div>
                <h4 className="text-lg font-bold text-white mb-2">Oceanfront Check-in</h4>
                <ul className="space-y-2.5 text-xs text-slate-300">
                  <li className="flex items-start gap-2">
                    <FaCheckCircle className="text-cyan-400 mt-0.5 shrink-0" />
                    <span>Flight landed at Dabolim Airport (GOI)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <FaCheckCircle className="text-cyan-400 mt-0.5 shrink-0" />
                    <span>Private cab to Palolem Eco-Resort</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <FaCheckCircle className="text-cyan-400 mt-0.5 shrink-0" />
                    <span>Sunset dinner at Sundowner Lounge</span>
                  </li>
                </ul>
              </div>
              <div className="mt-4 pt-3 border-t border-white/5 text-[11px] text-slate-400 flex justify-between">
                <span>Budget: ₹6,500</span>
                <span className="text-emerald-400">On Track</span>
              </div>
            </div>

            {/* Day 2 */}
            <div className="glass-cinema-card rounded-2xl p-5 border border-cyan-500/30 shadow-lg shadow-cyan-500/10 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-indigo-400 px-2.5 py-1 rounded-lg bg-indigo-500/10">Day 02</span>
                  <span className="text-xs text-cyan-300">Highlight Day</span>
                </div>
                <h4 className="text-lg font-bold text-white mb-2">Secret Coves & Kayaking</h4>
                <ul className="space-y-2.5 text-xs text-slate-300">
                  <li className="flex items-start gap-2">
                    <FaCheckCircle className="text-indigo-400 mt-0.5 shrink-0" />
                    <span>Morning Kayak through Cola Lagoon</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <FaCheckCircle className="text-indigo-400 mt-0.5 shrink-0" />
                    <span>Seafood feast at Fisherman's Cove</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <FaCheckCircle className="text-indigo-400 mt-0.5 shrink-0" />
                    <span>Cabo de Rama Fort cliffside sunset</span>
                  </li>
                </ul>
              </div>
              <div className="mt-4 pt-3 border-t border-white/5 text-[11px] text-slate-400 flex justify-between">
                <span>Budget: ₹4,800</span>
                <span className="text-emerald-400">High Satisfaction</span>
              </div>
            </div>

            {/* Day 3 */}
            <div className="glass-cinema-card rounded-2xl p-5 border border-white/5 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-purple-400 px-2.5 py-1 rounded-lg bg-purple-500/10">Day 03</span>
                  <span className="text-xs text-slate-400">Culture & Heritage</span>
                </div>
                <h4 className="text-lg font-bold text-white mb-2">Latin Quarter Walk</h4>
                <ul className="space-y-2.5 text-xs text-slate-300">
                  <li className="flex items-start gap-2">
                    <FaCheckCircle className="text-purple-400 mt-0.5 shrink-0" />
                    <span>Fontainhas Portuguese architecture tour</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <FaCheckCircle className="text-purple-400 mt-0.5 shrink-0" />
                    <span>Bakery stop for authentic Bebinca</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <FaCheckCircle className="text-purple-400 mt-0.5 shrink-0" />
                    <span>Mandovi River evening cruise</span>
                  </li>
                </ul>
              </div>
              <div className="mt-4 pt-3 border-t border-white/5 text-[11px] text-slate-400 flex justify-between">
                <span>Budget: ₹5,200</span>
                <span className="text-emerald-400">On Track</span>
              </div>
            </div>
          </div>

          {/* CTA under simulator */}
          <div className="mt-8 text-center">
            <Link
              to="/login?signup=true"
              className="btn-cinema-primary px-8 py-3.5 text-sm inline-flex items-center gap-2"
            >
              <span>Build My Custom Itinerary Now</span>
              <FaArrowRight className="text-xs" />
            </Link>
          </div>
        </div>
      </section>

      {/* FEATURES & AI INTELLIGENCE MATRIX */}
      <section id="features" className="py-24 px-4 relative z-10 max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-pill text-xs font-semibold text-cyan-400 mb-3 border border-cyan-500/30">
            <span>NEURAL SUPERPOWERS</span>
          </div>
          <h2 className="text-4xl sm:text-5xl font-extrabold text-white font-display">
            Built for Flawless Travel
          </h2>
          <p className="text-slate-400 text-sm max-w-xl mx-auto mt-2">
            Every layer of SimpliTrip is engineered to remove guesswork, reduce travel stress, and deliver pure joy.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-7">
          {features.map((item, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: idx * 0.08 }}
              whileHover={{ y: -6 }}
              className="glass-cinema-card rounded-3xl p-8 border border-white/10 flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div
                    className="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl shadow-lg"
                    style={{ backgroundColor: item.bgGlow }}
                  >
                    <item.icon className={item.color} />
                  </div>
                  <span className="text-[11px] font-bold px-3 py-1 rounded-full glass-pill text-slate-300 border border-white/10">
                    {item.tag}
                  </span>
                </div>

                <h3 className="text-2xl font-bold text-white mb-3 font-display group-hover:text-cyan-400 transition-colors">
                  {item.title}
                </h3>
                <p className="text-slate-300 text-sm leading-relaxed">
                  {item.desc}
                </p>
              </div>

              <div className="mt-6 pt-4 border-t border-white/5 flex items-center text-xs font-semibold text-cyan-400 gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                <span>Explore capability</span>
                <FaArrowRight className="text-[10px]" />
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* FINAL CINEMATIC CONVERSION BANNER */}
      <section className="py-20 px-4 relative z-10 max-w-5xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="relative rounded-3xl p-10 sm:p-16 overflow-hidden border border-cyan-500/40 shadow-2xl"
          style={{
            background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(99, 102, 241, 0.2) 50%, rgba(139, 92, 246, 0.2) 100%), rgba(8, 15, 36, 0.85)',
          }}
        >
          <h2 className="text-4xl sm:text-6xl font-black text-white tracking-tight font-display mb-4">
            Your Next Adventure Awaits.
          </h2>
          <p className="text-slate-300 text-base sm:text-lg max-w-xl mx-auto mb-8 font-light">
            No endless forum browsing. No spreadsheet headaches. Just cinema-grade travel itineraries crafted in seconds.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/login?signup=true"
              className="w-full sm:w-auto btn-cinema-primary px-9 py-4 text-base font-bold shadow-xl shadow-cyan-500/30"
            >
              Start Planning for Free
            </Link>
            <Link
              to="/login"
              className="w-full sm:w-auto btn-cinema-outline px-8 py-4 text-base font-semibold"
            >
              Sign In to Account
            </Link>
          </div>
        </motion.div>
      </section>

      {/* FOOTER */}
      <footer className="py-12 px-4 border-t border-white/10 relative z-10 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-cyan-500 flex items-center justify-center text-black font-bold text-xs">
              S
            </div>
            <span className="font-bold text-slate-200">SimpliTrip</span>
            <span className="text-slate-400">• Intelligent Travel Architecture</span>
          </div>

          <div className="flex gap-6">
            <a href="#explore" className="hover:text-white transition-colors">Destinations</a>
            <a href="#features" className="hover:text-white transition-colors">Engine</a>
            <Link to="/login" className="hover:text-white transition-colors">Sign In</Link>
          </div>

          <p>© {new Date().getFullYear()} SimpliTrip AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;

import React, { useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { loginUser, registerUser } from '../services/auth';
import { useUser } from '../context/UserContext';
import { FaCompass, FaArrowLeft, FaBolt, FaLock, FaEnvelope } from 'react-icons/fa';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { setUser, loginAsGuest } = useUser();

  const searchParams = new URLSearchParams(location.search);
  const isSignUp = searchParams.get('signup') === 'true';
  const promptParam = searchParams.get('prompt') || '';

  const getTargetUrl = () => {
    if (promptParam) {
      return `/plan-trip?prompt=${encodeURIComponent(promptParam)}`;
    }
    return '/dashboard';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      let userCredential;
      if (isSignUp) {
        userCredential = await registerUser(email, password);
      } else {
        userCredential = await loginUser(email, password);
      }
      setUser(userCredential.user);
      navigate(getTargetUrl());
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleGuestLogin = () => {
    loginAsGuest();
    navigate(getTargetUrl());
  };

  const toggleMode = () => {
    const nextParams = new URLSearchParams(location.search);
    if (isSignUp) {
      nextParams.delete('signup');
    } else {
      nextParams.set('signup', 'true');
    }
    navigate(`/login?${nextParams.toString()}`);
  };

  return (
    <div className="relative min-h-screen bg-[#040714] text-slate-100 flex items-center justify-center p-4 overflow-hidden">
      {/* Aurora Glow Orbs */}
      <div className="aurora-mesh w-[500px] h-[500px] bg-cyan-500/15 top-[-10%] left-[-10%]" />
      <div className="aurora-mesh w-[500px] h-[500px] bg-purple-500/15 bottom-[-10%] right-[-10%]" />

      {/* Back to Home Button */}
      <Link
        to="/"
        className="absolute top-6 left-6 z-20 px-4 py-2 rounded-full glass-pill text-xs font-semibold text-slate-300 hover:text-white flex items-center gap-2 hover:border-cyan-500/50 transition-all"
      >
        <FaArrowLeft className="text-[10px]" />
        <span>Return to Home</span>
      </Link>

      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 15 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-md"
      >
        {/* Glassmorphic Container Card */}
        <div className="glass-cinema rounded-3xl p-8 sm:p-10 border border-white/10 shadow-2xl backdrop-blur-2xl">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
              <FaCompass className="text-white text-2xl" />
            </div>

            <h1 className="text-3xl font-black text-white tracking-tight font-display">
              {isSignUp ? 'Create Account' : 'Welcome Back'}
            </h1>
            <p className="text-slate-400 text-xs sm:text-sm mt-1.5 font-light">
              {isSignUp
                ? 'Unlock autonomous AI travel planning & itineraries'
                : 'Access your saved trips and personalized guides'}
            </p>

            {promptParam && (
              <div className="mt-3 p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-xs text-cyan-300 text-left">
                <span className="font-bold">🎯 Destination ready:</span> "{promptParam}"
              </div>
            )}
          </div>

          {/* Quick Demo Mode */}
          <button
            onClick={handleGuestLogin}
            type="button"
            className="w-full mb-6 py-3 px-4 rounded-2xl bg-gradient-to-r from-cyan-500/20 via-indigo-500/20 to-purple-500/20 border border-cyan-500/40 text-cyan-300 hover:text-white hover:border-cyan-400 hover:shadow-lg hover:shadow-cyan-500/20 transition-all text-xs font-bold flex items-center justify-center gap-2 group"
          >
            <FaBolt className="text-amber-400 group-hover:scale-110 transition-transform" />
            <span>⚡ Instant Demo Explorer (1-Click Access)</span>
          </button>

          <div className="relative flex items-center justify-center mb-6">
            <div className="w-full border-t border-white/10" />
            <span className="absolute px-3 text-[11px] uppercase tracking-wider text-slate-500 bg-[#070e24]">
              Or continue with email
            </span>
          </div>

          {/* Auth Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <FaEnvelope className="text-xs" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 glass-input rounded-2xl text-xs sm:text-sm placeholder:text-slate-500"
                  placeholder="traveler@example.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <FaLock className="text-xs" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 glass-input rounded-2xl text-xs sm:text-sm placeholder:text-slate-500"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {error && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 btn-cinema-primary text-sm font-bold flex items-center justify-center gap-2 mt-2"
            >
              {loading ? (
                <span>Authenticating...</span>
              ) : (
                <span>{isSignUp ? 'Create Free Account' : 'Sign In to SimpliTrip'}</span>
              )}
            </button>
          </form>

          {/* Toggle Mode */}
          <div className="mt-6 text-center text-xs text-slate-400">
            <span>{isSignUp ? 'Already have an account?' : "Don't have an account yet?"}</span>
            <button
              type="button"
              onClick={toggleMode}
              className="ml-1.5 font-bold text-cyan-400 hover:text-cyan-300 transition-colors underline"
            >
              {isSignUp ? 'Sign In' : 'Sign Up Free'}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default LoginPage;
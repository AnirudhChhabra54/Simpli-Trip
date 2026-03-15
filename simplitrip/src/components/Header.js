import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { logoutUser } from '../services/auth';
import { useUser } from '../context/UserContext';
import ModelSelector from './ModelSelector';
import { FaCompass, FaSignOutAlt, FaPlaneDeparture, FaComments } from 'react-icons/fa';

const Header = () => {
    const { setUser } = useUser();
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = async () => {
        await logoutUser();
        setUser(null);
        navigate('/');
    };

    const isActive = (path) => location.pathname === path;

    return (
        <header className="sticky top-0 z-40 px-4 py-3 glass-cinema border-b border-white/10 backdrop-blur-2xl">
            <div className="max-w-7xl mx-auto flex justify-between items-center">
                {/* Brand Logo */}
                <div className="flex items-center gap-8">
                    <Link to="/dashboard" className="flex items-center gap-2 group">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-md shadow-cyan-500/30 group-hover:scale-105 transition-transform">
                            <FaCompass className="text-white text-base" />
                        </div>
                        <div className="text-xl font-bold tracking-tight font-display">
                            <span className="text-white">Simpli</span>
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-400">Trip</span>
                        </div>
                    </Link>

                    {/* Navigation Tabs */}
                    <nav className="hidden sm:flex items-center gap-2">
                        <Link 
                            to="/dashboard" 
                            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                                isActive('/dashboard')
                                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                                    : 'text-slate-300 hover:text-white hover:bg-white/5'
                            }`}
                        >
                            Dashboard
                        </Link>
                        <Link 
                            to="/plan-trip" 
                            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5 ${
                                isActive('/plan-trip')
                                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                                    : 'text-slate-300 hover:text-white hover:bg-white/5'
                            }`}
                        >
                            <FaPlaneDeparture className="text-[10px]" />
                            <span>Plan Trip</span>
                        </Link>
                        <Link 
                            to="/my-trips" 
                            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                                isActive('/my-trips')
                                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                                    : 'text-slate-300 hover:text-white hover:bg-white/5'
                            }`}
                        >
                            My Trips
                        </Link>
                        <Link 
                            to="/chat" 
                            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5 ${
                                isActive('/chat')
                                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                                    : 'text-slate-300 hover:text-white hover:bg-white/5'
                            }`}
                        >
                            <FaComments className="text-[10px]" />
                            <span>AI Assistant</span>
                        </Link>
                    </nav>
                </div>

                {/* Right controls */}
                <div className="flex items-center gap-3">
                    <ModelSelector />
                    <button 
                        onClick={handleLogout} 
                        className="px-3.5 py-1.5 text-xs font-semibold text-slate-300 hover:text-white glass-pill hover:bg-red-500/20 hover:border-red-500/30 hover:text-red-300 rounded-full transition-all flex items-center gap-1.5"
                        title="Sign Out"
                    >
                        <FaSignOutAlt className="text-xs" />
                        <span className="hidden sm:inline">Logout</span>
                    </button>
                </div>
            </div>
        </header>
    );
};

export default Header;

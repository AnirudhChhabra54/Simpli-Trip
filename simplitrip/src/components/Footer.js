import React from 'react';
import { Link } from 'react-router-dom';
import { FaCompass } from 'react-icons/fa';

const Footer = () => {
  return (
    <footer className="glass-cinema border-t border-white/10 py-6 px-4 relative z-10 text-xs text-slate-400 mt-auto">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center text-white text-xs shadow-sm">
            <FaCompass className="text-[10px]" />
          </div>
          <span className="font-bold text-slate-200">SimpliTrip</span>
          <span className="text-slate-500">• Autonomous Travel AI</span>
        </div>

        <div className="flex gap-6">
          <Link to="/dashboard" className="hover:text-cyan-400 transition-colors">Dashboard</Link>
          <Link to="/plan-trip" className="hover:text-cyan-400 transition-colors">Plan Trip</Link>
          <Link to="/chat" className="hover:text-cyan-400 transition-colors">AI Chat</Link>
          <Link to="/my-trips" className="hover:text-cyan-400 transition-colors">My Trips</Link>
        </div>

        <p>© {new Date().getFullYear()} SimpliTrip AI. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;

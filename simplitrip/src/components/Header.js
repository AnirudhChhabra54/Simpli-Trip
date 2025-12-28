import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { logoutUser } from '../services/auth';
import { useUser } from '../context/UserContext';

const Header = () => {
    const { setUser } = useUser();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logoutUser();
        setUser(null);
        navigate('/');
    };

    return (
        <header className="bg-gray-800 p-4">
            <div className="container mx-auto flex justify-between items-center">
                <div className="flex items-center gap-6">
                    <Link to="/dashboard" className="text-2xl font-bold tracking-wider hover:text-cyan-400 transition-colors">SimpliTrip</Link>
                    <Link to="/my-trips" className="text-sm text-cyan-300 hover:text-white transition-colors">My Trips</Link>
                    <Link to="/chat" className="text-sm text-cyan-300 hover:text-white transition-colors">AI Chat</Link>
                </div>
                <button onClick={handleLogout} className="bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-2 px-4 rounded-lg">
                    Logout
                </button>
            </div>
        </header>
    );
};

export default Header;

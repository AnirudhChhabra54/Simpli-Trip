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
                <Link to="/dashboard" className="text-2xl font-bold tracking-wider">SimpliTrip</Link>
                <button onClick={handleLogout} className="bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-2 px-4 rounded-lg">
                    Logout
                </button>
            </div>
        </header>
    );
};

export default Header;

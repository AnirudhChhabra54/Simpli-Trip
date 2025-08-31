import React from 'react';
import { Link } from 'react-router-dom';
import { useUser } from '../context/UserContext';

const Header = () => {
  const { user, setUser } = useUser();

  const handleLogout = () => {
    // This is a simplified logout. In a real app, you'd clear tokens.
    setUser(null); 
  };

  return (
    <header className="bg-gray-800 text-white shadow-md sticky top-0 z-50">
      <nav className="container mx-auto px-6 py-3 flex justify-between items-center">
        <Link to="/" className="text-xl font-bold hover:text-cyan-400 transition-colors">
          SimpliTrip
        </Link>
        <div>
          {user ? (
            <button
              onClick={handleLogout}
              className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded transition-colors"
            >
              Logout
            </button>
          ) : (
            <Link to="/login" className="bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-2 px-4 rounded transition-colors">
              Login
            </Link>
          )}
        </div>
      </nav>
    </header>
  );
};

export default Header;

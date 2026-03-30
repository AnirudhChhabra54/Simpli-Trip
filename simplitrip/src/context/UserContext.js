import React, { createContext, useState, useEffect, useContext } from 'react';
import { auth } from '../services/firebase';
import { onAuthStateChanged } from 'firebase/auth';

const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('simplitrip_user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let unsubscribe = () => {};
    try {
      if (auth) {
        unsubscribe = onAuthStateChanged(auth, (fbUser) => {
          if (fbUser) {
            const userData = {
              uid: fbUser.uid,
              email: fbUser.email,
              displayName: fbUser.displayName || fbUser.email?.split('@')[0] || 'Traveler',
            };
            setUser(userData);
            localStorage.setItem('simplitrip_user', JSON.stringify(userData));
          } else {
            const stored = localStorage.getItem('simplitrip_user');
            if (stored) {
              setUser(JSON.parse(stored));
            } else {
              setUser(null);
            }
          }
          setLoading(false);
        });
      } else {
        setLoading(false);
      }
    } catch (e) {
      setLoading(false);
    }
    
    return () => unsubscribe();
  }, []);

  const loginAsGuest = (name = 'Guest Traveler', email = 'explorer@simplitrip.ai') => {
    const guest = {
      uid: 'guest_' + Date.now(),
      email,
      displayName: name,
      isAnonymous: true,
    };
    setUser(guest);
    localStorage.setItem('simplitrip_user', JSON.stringify(guest));
    return guest;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('simplitrip_user');
  };

  return (
    <UserContext.Provider value={{ user, loading, setUser, loginAsGuest, logout }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);
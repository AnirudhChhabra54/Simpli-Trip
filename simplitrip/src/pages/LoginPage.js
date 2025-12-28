// import React, { useState } from 'react';
// import { useLocation, useNavigate } from 'react-router-dom';
// import { motion } from 'framer-motion';
// import { loginUser, registerUser } from '../services/auth';
// import { useUser } from '../context/UserContext';

// const LoginPage = () => {
//     const [email, setEmail] = useState('');
//     const [password, setPassword] = useState('');
//     const [error, setError] = useState(null);
//     const [loading, setLoading] = useState(false);
//     const navigate = useNavigate();
//     const location = useLocation();
//     const { setUser } = useUser();

//     const isSignUp = new URLSearchParams(location.search).get('signup') === 'true';

//     const handleSubmit = async (e) => {
//         e.preventDefault();
//         setLoading(true);
//         setError(null);

//         try {
//             let userCredential;
//             if (isSignUp) {
//                 userCredential = await registerUser(email, password);
//             } else {
//                 userCredential = await loginUser(email, password);
//             }
//             setUser(userCredential.user);
//             navigate('/dashboard');
//         } catch (error) {
//             setError(error.message);
//         } finally {
//             setLoading(false);
//         }
//     };

//     return (
//         <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">
//             <motion.div 
//                 initial={{ opacity: 0, y: -20 }} 
//                 animate={{ opacity: 1, y: 0 }} 
//                 transition={{ duration: 0.5 }}
//                 className="w-full max-w-md p-8 space-y-6 bg-gray-800 rounded-lg shadow-lg"
//             >
//                 <h1 className="text-3xl font-bold text-center">{isSignUp ? 'Sign Up' : 'Login'}</h1>
//                 <form onSubmit={handleSubmit} className="space-y-6">
//                     <div>
//                         <label className="block text-sm font-medium">Email</label>
//                         <input
//                             type="email"
//                             value={email}
//                             onChange={(e) => setEmail(e.target.value)}
//                             className="w-full px-3 py-2 mt-1 text-gray-900 bg-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500"
//                             required
//                         />
//                     </div>
//                     <div>
//                         <label className="block text-sm font-medium">Password</label>
//                         <input
//                             type="password"
//                             value={password}
//                             onChange={(e) => setPassword(e.target.value)}
//                             className="w-full px-3 py-2 mt-1 text-gray-900 bg-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500"
//                             required
//                         />
//                     </div>
//                     <motion.button
//                         whileHover={{ scale: 1.05 }}
//                         whileTap={{ scale: 0.95 }}
//                         type="submit"
//                         disabled={loading}
//                         className="w-full py-2 font-bold text-white bg-cyan-600 rounded-md hover:bg-cyan-700 disabled:bg-gray-500"
//                     >
//                         {loading ? 'Loading...' : (isSignUp ? 'Sign Up' : 'Login')}
//                     </motion.button>
//                     {error && <p className="text-sm text-red-500">{error}</p>}
//                 </form>
//             </motion.div>
//         </div>
//     );
// };

// export default LoginPage;


import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { loginUser, registerUser } from '../services/auth';
import { useUser } from '../context/UserContext';

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();
    const { setUser } = useUser();

    const isSignUp = new URLSearchParams(location.search).get('signup') === 'true';

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
            navigate('/dashboard');
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const toggleMode = () => {
        navigate(isSignUp ? '/login' : '/login?signup=true');
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center p-4">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4, ease: "easeOut" }}
                className="w-full max-w-md"
            >
                {/* Glassmorphism Card */}
                <div className="relative bg-gray-800/70 backdrop-blur-lg rounded-2xl border border-gray-700/50 shadow-2xl overflow-hidden">
                    {/* Decorative top accent */}
                    <div className="h-2 bg-gradient-to-r from-cyan-500 to-purple-600"></div>
                    
                    <div className="p-8">
                        {/* Header */}
                        <div className="text-center mb-8">
                            <motion.div
                                initial={{ y: -10, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                transition={{ delay: 0.1 }}
                                className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-cyan-900/30 to-purple-900/30 mb-4"
                            >
                                <span className="text-2xl">{isSignUp ? '🚀' : '🔑'}</span>
                            </motion.div>
                            <motion.h1 
                                initial={{ y: -10, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                transition={{ delay: 0.2 }}
                                className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-400"
                            >
                                {isSignUp ? 'Create Account' : 'Welcome Back'}
                            </motion.h1>
                            <motion.p 
                                initial={{ y: -10, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                transition={{ delay: 0.3 }}
                                className="text-gray-400 mt-2"
                            >
                                {isSignUp 
                                    ? 'Start your journey with us' 
                                    : 'Sign in to continue your adventure'}
                            </motion.p>
                        </div>

                        {/* Form */}
                        <form onSubmit={handleSubmit} className="space-y-5">
                            {/* Email Field */}
                            <motion.div
                                initial={{ x: -20, opacity: 0 }}
                                animate={{ x: 0, opacity: 1 }}
                                transition={{ delay: 0.4 }}
                            >
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Email Address
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-gray-500">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                        </svg>
                                    </div>
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="w-full pl-10 pr-4 py-3 bg-gray-700/50 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all"
                                        placeholder="you@example.com"
                                        required
                                    />
                                </div>
                            </motion.div>

                            {/* Password Field */}
                            <motion.div
                                initial={{ x: -20, opacity: 0 }}
                                animate={{ x: 0, opacity: 1 }}
                                transition={{ delay: 0.5 }}
                            >
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Password
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-gray-500">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                        </svg>
                                    </div>
                                    <input
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="w-full pl-10 pr-4 py-3 bg-gray-700/50 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all"
                                        placeholder="••••••••"
                                        required
                                    />
                                </div>
                            </motion.div>

                            {/* Submit Button */}
                            <motion.div
                                initial={{ y: 20, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                transition={{ delay: 0.6 }}
                            >
                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    type="submit"
                                    disabled={loading}
                                    className="w-full py-3.5 font-bold text-white bg-gradient-to-r from-cyan-600 to-purple-600 rounded-xl shadow-lg hover:shadow-cyan-500/30 transition-all duration-300 disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center"
                                >
                                    {loading ? (
                                        <>
                                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                            </svg>
                                            Processing...
                                        </>
                                    ) : (
                                        isSignUp ? 'Create Account' : 'Sign In'
                                    )}
                                </motion.button>
                            </motion.div>

                            {/* Error Message */}
                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    className="p-3 bg-red-900/30 border border-red-800/50 rounded-xl text-red-300 text-sm"
                                >
                                    {error}
                                </motion.div>
                            )}
                        </form>

                        {/* Toggle Link */}
                        <motion.div
                            initial={{ y: 20, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            transition={{ delay: 0.7 }}
                            className="mt-6 text-center"
                        >
                            <p className="text-gray-400">
                                {isSignUp ? "Already have an account?" : "Don't have an account?"}
                                <motion.button
                                    whileHover={{ color: "#22d3ee" }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={toggleMode}
                                    className="ml-2 font-medium text-cyan-400 hover:text-cyan-300 transition-colors"
                                >
                                    {isSignUp ? 'Sign in' : 'Sign up'}
                                </motion.button>
                            </p>
                        </motion.div>
                    </div>
                </div>

                {/* Floating Decorative Elements */}
                <div className="absolute -top-6 -left-6 w-24 h-24 rounded-full bg-cyan-500/10 blur-xl"></div>
                <div className="absolute -bottom-8 -right-8 w-32 h-32 rounded-full bg-purple-500/10 blur-xl"></div>
            </motion.div>
        </div>
    );
};

export default LoginPage;
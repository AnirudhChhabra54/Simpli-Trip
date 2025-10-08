import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const LandingPage = () => {
    return (
        <>
            <style>{`
                body {
                    font-family: 'Poppins', sans-serif;
                    background-color: #0a0a1a;
                    color: #e0e0e0;
                    overflow-x: hidden;
                }
                .pulse-text {
                    animation: pulse-glow 3s infinite ease-in-out;
                }
                @keyframes pulse-glow {
                    0%, 100% { text-shadow: 0 0 10px rgba(6, 182, 212, 0.5); }
                    50% { text-shadow: 0 0 20px rgba(6, 182, 212, 1); }
                }
            `}</style>

            <div className="relative antialiased">
                <div className="fixed top-0 left-0 h-full w-full z-[-1] bg-black" />

                <header className="fixed top-0 left-0 right-0 z-50 transition-all duration-300 bg-transparent">
                    <nav className="container mx-auto flex items-center justify-between p-6">
                        <div className="text-2xl font-bold tracking-wider">SimpliTrip</div>
                        <div className="flex items-center space-x-4">
                            <Link to="/login" className="rounded-lg bg-cyan-500 px-6 py-2 font-bold text-black transition-all duration-300 hover:bg-cyan-400 hover:shadow-lg hover:shadow-cyan-500/50 transform hover:scale-105">
                                Login
                            </Link>
                            <Link to="/login?signup=true" className="rounded-lg bg-transparent border border-cyan-500 px-6 py-2 font-bold text-white transition-all duration-300 hover:bg-cyan-500 hover:text-black">
                                Sign Up
                            </Link>
                        </div>
                    </nav>
                </header>

                <main>
                    <section className="flex h-screen items-center justify-center text-center">
                        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }} className="z-10 px-4">
                            <h1 className="text-5xl font-black uppercase tracking-tighter md:text-7xl lg:text-8xl">
                                Welcome to <span className="text-cyan-400 pulse-text">SimpliTrip</span>
                            </h1>
                            <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-300 md:text-xl">
                                Your ultimate travel planner. Create, share, and manage your trips with ease.
                            </p>
                            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="mt-8">
                                <Link to="/login?signup=true" className="inline-block rounded-lg bg-white px-8 py-3 text-lg font-bold text-black shadow-lg shadow-white/30 transition-transform hover:scale-105">
                                    Get Started
                                </Link>
                            </motion.div>
                        </motion.div>
                    </section>
                </main>
            </div>
        </>
    );
};

export default LandingPage;
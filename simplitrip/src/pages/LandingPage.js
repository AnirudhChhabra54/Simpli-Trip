import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaRobot, FaMapMarkedAlt, FaMoneyBillWave, FaRoute, FaBrain, FaChartLine } from 'react-icons/fa';

const LandingPage = () => {
    const features = [
        {
            icon: FaRobot,
            title: 'AI-Powered Planning',
            description: 'Describe your trip in plain English and let our AI create the perfect itinerary',
            color: 'cyan',
        },
        {
            icon: FaMapMarkedAlt,
            title: 'Smart Recommendations',
            description: 'Get personalized destination suggestions based on your preferences and budget',
            color: 'purple',
        },
        {
            icon: FaMoneyBillWave,
            title: 'Cost Prediction',
            description: 'Accurate cost estimates with detailed breakdowns for flights, hotels, and activities',
            color: 'orange',
        },
        {
            icon: FaRoute,
            title: 'Optimized Itineraries',
            description: 'AI-optimized routes that save time and maximize your travel experience',
            color: 'green',
        },
        {
            icon: FaBrain,
            title: 'Natural Language',
            description: 'Just tell us what you want - no complex forms or confusing options',
            color: 'pink',
        },
        {
            icon: FaChartLine,
            title: 'Budget Optimization',
            description: 'Get smart suggestions to optimize your budget without compromising experience',
            color: 'yellow',
        },
    ];

    const colorClasses = {
        cyan: 'from-cyan-500 to-cyan-600',
        purple: 'from-purple-500 to-purple-600',
        orange: 'from-orange-500 to-orange-600',
        green: 'from-green-500 to-green-600',
        pink: 'from-pink-500 to-pink-600',
        yellow: 'from-yellow-500 to-yellow-600',
    };

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
                .gradient-bg {
                    background: radial-gradient(circle at 20% 50%, rgba(6, 182, 212, 0.1) 0%, transparent 50%),
                                radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
                }
            `}</style>

            <div className="relative antialiased gradient-bg">
                <div className="fixed top-0 left-0 h-full w-full z-[-1] bg-black" />

                {/* Header */}
                <header className="fixed top-0 left-0 right-0 z-50 transition-all duration-300 bg-gray-900/50 backdrop-blur-md">
                    <nav className="container mx-auto flex items-center justify-between p-6">
                        <div className="text-2xl font-bold tracking-wider flex items-center">
                            <span className="text-cyan-400">Simpli</span>
                            <span className="text-white">Trip</span>
                        </div>
                        <div className="flex items-center space-x-4">
                            <Link 
                                to="/login" 
                                className="rounded-lg bg-cyan-500 px-6 py-2 font-bold text-black transition-all duration-300 hover:bg-cyan-400 hover:shadow-lg hover:shadow-cyan-500/50 transform hover:scale-105"
                            >
                                Login
                            </Link>
                            <Link 
                                to="/login?signup=true" 
                                className="rounded-lg bg-transparent border border-cyan-500 px-6 py-2 font-bold text-white transition-all duration-300 hover:bg-cyan-500 hover:text-black"
                            >
                                Sign Up
                            </Link>
                        </div>
                    </nav>
                </header>

                <main>
                    {/* Hero Section */}
                    <section className="relative flex min-h-screen items-center justify-center text-center pt-20 overflow-hidden">
                        {/* Animated Background Elements */}
                        <div className="absolute inset-0 overflow-hidden">
                            <div className="absolute top-20 left-10 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
                            <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
                            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-orange-500/5 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
                        </div>

                        <motion.div 
                            initial={{ opacity: 0, y: 20 }} 
                            animate={{ opacity: 1, y: 0 }} 
                            transition={{ duration: 0.8 }} 
                            className="z-10 px-4 max-w-6xl"
                        >
                            <motion.div
                                initial={{ scale: 0.9 }}
                                animate={{ scale: 1 }}
                                transition={{ duration: 0.5 }}
                                className="mb-6"
                            >
                                <span className="inline-block px-6 py-3 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border-2 border-cyan-500 rounded-full text-cyan-400 text-sm font-bold mb-4 shadow-lg shadow-cyan-500/20">
                                    🤖 Powered by Advanced AI • 100% Free
                                </span>
                            </motion.div>
                            
                            <h1 className="text-6xl font-black tracking-tight md:text-7xl lg:text-8xl mb-6 leading-tight">
                                Discover Your Next
                                <br />
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 pulse-text">
                                    Adventure
                                </span>
                            </h1>
                            
                            <p className="mx-auto mt-8 max-w-3xl text-xl text-gray-300 md:text-2xl leading-relaxed font-light">
                                Tell us your dream trip in your own words. Our AI creates personalized itineraries with real-time prices, hidden gems, and local experiences.
                            </p>
                            
                            <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center items-center">
                                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                                    <Link 
                                        to="/login?signup=true" 
                                        className="inline-block rounded-lg bg-gradient-to-r from-cyan-500 to-purple-500 px-8 py-4 text-lg font-bold text-white shadow-lg shadow-cyan-500/30 transition-transform hover:shadow-xl hover:shadow-cyan-500/50"
                                    >
                                        Start Planning Free
                                    </Link>
                                </motion.div>
                                
                                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                                    <a 
                                        href="#features" 
                                        className="inline-block rounded-lg border-2 border-white px-8 py-4 text-lg font-bold text-white transition-all hover:bg-white hover:text-black"
                                    >
                                        See How It Works
                                    </a>
                                </motion.div>
                            </div>

                            {/* Popular Destinations Preview */}
                            <div className="mt-16 max-w-5xl mx-auto">
                                <p className="text-gray-400 text-sm mb-6 uppercase tracking-wider">Popular Destinations</p>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    {[
                                        { name: 'Goa', emoji: '🏖️', color: 'from-orange-500 to-pink-500' },
                                        { name: 'Ladakh', emoji: '🏔️', color: 'from-blue-500 to-cyan-500' },
                                        { name: 'Kerala', emoji: '🌴', color: 'from-green-500 to-emerald-500' },
                                        { name: 'Jaipur', emoji: '🏰', color: 'from-purple-500 to-pink-500' }
                                    ].map((dest, i) => (
                                        <motion.div
                                            key={i}
                                            initial={{ opacity: 0, scale: 0.8 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            transition={{ delay: 0.6 + i * 0.1 }}
                                            whileHover={{ scale: 1.05, y: -5 }}
                                            className={`relative bg-gradient-to-br ${dest.color} rounded-2xl p-6 cursor-pointer overflow-hidden group`}
                                        >
                                            <div className="absolute inset-0 bg-black/20 group-hover:bg-black/10 transition-all"></div>
                                            <div className="relative z-10">
                                                <p className="text-5xl mb-2">{dest.emoji}</p>
                                                <p className="text-white font-bold text-lg">{dest.name}</p>
                                            </div>
                                        </motion.div>
                                    ))}
                                </div>
                            </div>

                            {/* Stats */}
                            <div className="mt-20 grid grid-cols-3 gap-8 max-w-4xl mx-auto">
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.2 }}
                                    className="text-center p-6 bg-gray-800/50 rounded-2xl backdrop-blur-sm border border-gray-700"
                                >
                                    <p className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">10K+</p>
                                    <p className="text-gray-300 mt-3 font-semibold">Destinations</p>
                                </motion.div>
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.3 }}
                                    className="text-center p-6 bg-gray-800/50 rounded-2xl backdrop-blur-sm border border-gray-700"
                                >
                                    <p className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500">95%</p>
                                    <p className="text-gray-300 mt-3 font-semibold">Accuracy</p>
                                </motion.div>
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.4 }}
                                    className="text-center p-6 bg-gray-800/50 rounded-2xl backdrop-blur-sm border border-gray-700"
                                >
                                    <p className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-500">24/7</p>
                                    <p className="text-gray-300 mt-3 font-semibold">AI Support</p>
                                </motion.div>
                            </div>
                        </motion.div>
                    </section>

                    {/* Features Section */}
                    <section id="features" className="py-20 px-4">
                        <div className="container mx-auto max-w-6xl">
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                className="text-center mb-16"
                            >
                                <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                                    Why Choose SimpliTrip?
                                </h2>
                                <p className="text-gray-400 text-lg max-w-2xl mx-auto">
                                    Experience the future of travel planning with our AI-powered features
                                </p>
                            </motion.div>

                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {features.map((feature, index) => (
                                    <motion.div
                                        key={index}
                                        initial={{ opacity: 0, y: 20 }}
                                        whileInView={{ opacity: 1, y: 0 }}
                                        viewport={{ once: true }}
                                        transition={{ delay: index * 0.1 }}
                                        whileHover={{ y: -10, scale: 1.03 }}
                                        className="relative bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-8 border border-gray-700 hover:border-transparent hover:shadow-2xl hover:shadow-cyan-500/20 transition-all duration-300 overflow-hidden group"
                                    >
                                        {/* Gradient overlay on hover */}
                                        <div className={`absolute inset-0 bg-gradient-to-br ${colorClasses[feature.color]} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}></div>
                                        
                                        <div className="relative z-10">
                                            <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${colorClasses[feature.color]} flex items-center justify-center mb-6 shadow-lg transform group-hover:scale-110 group-hover:rotate-6 transition-transform duration-300`}>
                                                <feature.icon className="text-3xl text-white" />
                                            </div>
                                            <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-cyan-400 transition-colors">
                                                {feature.title}
                                            </h3>
                                            <p className="text-gray-400 leading-relaxed group-hover:text-gray-300 transition-colors">
                                                {feature.description}
                                            </p>
                                        </div>
                                        
                                        {/* Decorative corner element */}
                                        <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-cyan-500/10 to-transparent rounded-bl-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    </section>

                    {/* CTA Section */}
                    <section className="py-20 px-4">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            viewport={{ once: true }}
                            className="container mx-auto max-w-4xl bg-gradient-to-r from-cyan-500 to-purple-500 rounded-2xl p-12 text-center"
                        >
                            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                                Ready to Start Your Journey?
                            </h2>
                            <p className="text-white/90 text-lg mb-8">
                                Join thousands of travelers who trust SimpliTrip for their perfect vacation
                            </p>
                            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                                <Link 
                                    to="/login?signup=true" 
                                    className="inline-block rounded-lg bg-white px-10 py-4 text-lg font-bold text-black shadow-lg transition-transform hover:scale-105"
                                >
                                    Create Your Free Account
                                </Link>
                            </motion.div>
                        </motion.div>
                    </section>

                    {/* Footer */}
                    <footer className="py-8 px-4 border-t border-gray-800">
                        <div className="container mx-auto text-center text-gray-400">
                            <p>&copy; 2024 SimpliTrip. All rights reserved.</p>
                            <p className="mt-2 text-sm">Powered by Advanced AI & Machine Learning</p>
                        </div>
                    </footer>
                </main>
            </div>
        </>
    );
};

export default LandingPage;

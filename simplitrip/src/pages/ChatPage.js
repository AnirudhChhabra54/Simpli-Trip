import React from 'react';
import { motion } from 'framer-motion';
import { FaRobot, FaMagic } from 'react-icons/fa'; // Changed FaSparkles to FaMagic
import Layout from '../components/Layout';
import ChatTab from '../components/ChatTab';

const ChatPage = () => {
  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 h-[calc(100vh-80px)] flex flex-col">
        {/* Header Section */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-6 flex-none"
        >
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <div className="p-2.5 bg-gradient-to-br from-cyan-500/20 to-purple-500/20 rounded-xl border border-cyan-500/30 backdrop-blur-sm">
                  <FaRobot className="text-2xl text-cyan-400" />
                </div>
                <h1 className="text-3xl md:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-500">
                  AI Travel Assistant
                </h1>
              </div>
              <p className="text-gray-400 ml-1 flex items-center gap-2">
                Your personal guide for itineraries, hidden gems, and travel tips.
                <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-900/30 text-cyan-300 border border-cyan-500/20 flex items-center gap-1">
                  <FaMagic className="text-[10px]" /> Powered by GenZ
                </span>
              </p>
            </div>
          </div>
        </motion.div>

        {/* Chat Container */}
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.4 }}
          className="flex-1 relative min-h-0"
        >
           {/* Decorative Background Glow */}
           <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-2xl blur opacity-20"></div>
           
           {/* Glass Card */}
           <div className="relative h-full bg-gray-900/60 backdrop-blur-xl border border-gray-700/50 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
             <div className="h-full flex flex-col">
               <ChatTab />
             </div>
           </div>
        </motion.div>
      </div>
    </Layout>
  );
};

export default ChatPage;
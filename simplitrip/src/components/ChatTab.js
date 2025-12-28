import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { startChat, chatMessage } from '../services/tripPlannerService';
import { formatMessage, cleanText, renderFormattedMessage } from '../utils/messageFormatter';
import { addTrip } from '../services/firestore';
import { useUser } from '../context/UserContext';

const ChatTab = () => {
  const { user } = useUser();
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [tripName, setTripName] = useState('');
  const [error, setError] = useState('');
  const bottomRef = useRef(null);

  useEffect(() => {
    // create a lightweight session id on mount
    const init = async () => {
      const id = await startChat();
      setSessionId(id);
      setMessages([{ role: 'system', text: '👋 Hello! Tell me about your dream trip and I will create a personalized itinerary for you.\n\nExample: "Plan a 3-day Goa trip for 2 people with ₹50,000 budget, focusing on beaches and food"' }]);
    };
    init();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const reply = await chatMessage(sessionId, input);
      const raw = reply?.reply ?? reply?.message ?? reply?.text ?? reply;
      let content = '';
      if (raw == null) {
        content = '';
      } else if (typeof raw === 'string') {
        content = cleanText(raw);
      } else if (typeof raw === 'object') {
        const keys = Object.keys(raw);
        const knownKeys = ['destination', 'duration', 'travelers', 'budget', 'preferences'];
        const hasKnown = knownKeys.some(k => keys.includes(k));
        if (hasKnown) {
          const parts = [];
          if (raw.destination) parts.push(`Destination: ${raw.destination}`);
          if (raw.duration) parts.push(`Duration: ${raw.duration} days`);
          if (raw.travelers) parts.push(`Travelers: ${raw.travelers}`);
          if (raw.budget) parts.push(`Budget: ₹${raw.budget}`);
          if (raw.preferences) parts.push(`Preferences: ${Array.isArray(raw.preferences) ? raw.preferences.join(', ') : raw.preferences}`);
          content = parts.join(' | ');
        } else {
          try {
            content = JSON.stringify(raw, null, 2);
          } catch (e) {
            content = String(raw);
          }
        }
      } else {
        content = String(raw);
      }

      const formatted = formatMessage(content);
      setMessages(prev => [...prev, { role: 'assistant', text: content, formatted }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', text: 'Sorry — I could not reach the assistant.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveTrip = async () => {
    if (!tripName.trim()) {
      setError('Please enter a trip name');
      return;
    }

    try {
      // Extract trip details from conversation
      const conversationText = messages
        .filter(m => m.role === 'assistant' || m.role === 'user')
        .map(m => m.text)
        .join('\n');

      const newTrip = {
        name: tripName,
        userId: user.uid,
        destination: 'AI Generated Trip',
        itinerary: conversationText,
        createdAt: new Date(),
        status: 'planned',
        source: 'AI Chat',
        sessionId: sessionId,
        preferences: [],
        budget: 0,
        travelers: 0,
        days: 0,
      };

      await addTrip(newTrip);
      setShowSaveModal(false);
      setTripName('');
      setError('');

      // Show success message
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: `✅ Trip "${tripName}" saved successfully! You can view it in "My Trips".`
      }]);
    } catch (err) {
      setError('Failed to save trip: ' + err.message);
      console.error(err);
    }
  };

  return (
    <div className="w-full h-full flex flex-col">
      {/* Chat Display */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-2xl p-4 rounded-lg ${m.role === 'user'
                ? 'bg-cyan-600 text-white'
                : m.role === 'system'
                  ? 'bg-gray-700 text-gray-100 font-semibold'
                  : 'bg-gray-700 text-gray-100'
                }`}
            >
              {m.formatted ? (
                <div className="space-y-2 text-sm">
                  {renderFormattedMessage(m.formatted)}
                </div>
              ) : (
                <div className="chat-markdown text-sm whitespace-pre-wrap leading-relaxed">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {cleanText(m.text)}
                  </ReactMarkdown>
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-700 text-gray-300 p-4 rounded-lg">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-700 p-4 bg-gray-900/80">
        {error && (
          <div className="mb-3 p-2 bg-red-900/30 border border-red-500/50 rounded-lg text-red-300 text-sm">
            {error}
          </div>
        )}
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !isLoading) sendMessage(); }}
            placeholder="Tell me about your trip plans..."
            className="flex-1 bg-gray-700 p-3 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 disabled:opacity-50 text-white rounded-lg transition-all font-semibold"
          >
            Send
          </button>
          <button
            onClick={() => setShowSaveModal(true)}
            disabled={isLoading || messages.length <= 1}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white rounded-lg transition-all font-semibold"
          >
            Save Trip
          </button>
        </div>
      </div>

      {/* Save Modal */}
      {showSaveModal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-gray-800 border border-gray-700 rounded-2xl p-8 max-w-md w-full"
          >
            <h3 className="text-2xl font-bold text-white mb-4">Save This Trip</h3>
            <input
              type="text"
              value={tripName}
              onChange={(e) => setTripName(e.target.value)}
              placeholder="e.g., Summer Goa Adventure"
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500 mb-6"
              autoFocus
            />
            {error && (
              <div className="mb-4 p-2 bg-red-900/30 border border-red-500/50 rounded-lg text-red-300 text-sm">
                {error}
              </div>
            )}
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowSaveModal(false);
                  setError('');
                }}
                className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-2 px-4 rounded-lg transition-all"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveTrip}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg transition-all font-bold"
              >
                Save
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};

export default ChatTab;

import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import html2pdf from 'html2pdf.js';
import Layout from '../components/Layout';
import InteractiveItineraryMap from '../components/InteractiveItineraryMap';
import { startChat, chatMessage } from '../services/tripPlannerService';
import { formatMessage, cleanText, renderFormattedMessage } from '../utils/messageFormatter';
import { addTrip } from '../services/firestore';
import { useUser } from '../context/UserContext';

const TripPlannerPage = () => {
  const navigate = useNavigate();
  const { user } = useUser();
  const bottomRef = useRef(null);
  const [sessionId, setSessionId] = useState(null);
  const [step, setStep] = useState('form'); // 'form' or 'chat'

  // Form preferences
  const [currentLocation, setCurrentLocation] = useState('');
  const [destination, setDestination] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [budget, setBudget] = useState('');
  const [travelers, setTravelers] = useState('2');
  const [preferences, setPreferences] = useState({
    beach: false,
    adventure: false,
    food: false,
    photography: false,
    shopping: false,
    romantic: false,
    luxury: false,
    nightlife: false,
  });
  const [mealType, setMealType] = useState('mixed');
  const [accommodationType, setAccommodationType] = useState('hotel');
  const [transportMode, setTransportMode] = useState('flight');

  // Chat state
  const [messages, setMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [tripName, setTripName] = useState('');
  const [showSaveModal, setShowSaveModal] = useState(false);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const categoryIcons = {
    beach: '🏖️',
    adventure: '🏔️',
    food: '🍽️',
    photography: '📸',
    shopping: '🛍️',
    romantic: '💕',
    luxury: '✨',
    nightlife: '🎉',
  };

  const handlePreferenceChange = (pref) => {
    setPreferences(prev => ({ ...prev, [pref]: !prev[pref] }));
  };

  const handleGenerateItinerary = async () => {
    if (!destination.trim() || !budget.trim()) {
      setError('Please fill in destination and budget');
      return;
    }

    const days = endDate && startDate ? Math.ceil((new Date(endDate) - new Date(startDate)) / (1000 * 60 * 60 * 24)) : 0;
    const selectedPrefs = Object.keys(preferences).filter(k => preferences[k]).join(', ');

    const promptMessage = `Plan a trip with these details:
- Origin/Current Location: ${currentLocation || 'Not specified'}
- Destination: ${destination}
- Budget: ₹${budget}
- Duration: ${days > 0 ? days + ' days' : 'Not specified'}
- Number of travelers: ${travelers}
- Preferences: ${selectedPrefs || 'No specific preferences'}
- Meal type: ${mealType}
- Accommodation: ${accommodationType}
- Transport mode: ${transportMode}

Please provide a detailed itinerary with cost breakdown.`;

    setStep('chat');
    setError('');

    // Initialize chat session
    const id = await startChat();
    setSessionId(id);
    setMessages([
      { role: 'system', text: '📋 Your Personalized Travel Itinerary' }
    ]);

    // Send the preferences as first message
    setIsLoading(true);
    try {
      const reply = await chatMessage(id, promptMessage);
      const content = reply?.reply ?? reply?.message ?? reply?.text ?? String(reply);
      const formatted = formatMessage(cleanText(content));
      setMessages(prev => [...prev, { role: 'assistant', text: content, formatted }]);
    } catch (err) {
      setError('Failed to generate itinerary');
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', text: 'Failed to generate itinerary. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim()) return;

    const userMsg = { role: 'user', text: chatInput };
    setMessages(prev => [...prev, userMsg]);
    setChatInput('');
    setIsLoading(true);

    try {
      const reply = await chatMessage(sessionId, chatInput);
      const content = reply?.reply ?? reply?.message ?? reply?.text ?? String(reply);
      const formatted = formatMessage(cleanText(content));
      setMessages(prev => [...prev, { role: 'assistant', text: content, formatted }]);
    } catch (err) {
      setError('Failed to send message');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveTrip = async () => {
    if (!tripName.trim()) {
      setError('Please enter a trip name');
      return;
    }

    const days = endDate && startDate ? Math.ceil((new Date(endDate) - new Date(startDate)) / (1000 * 60 * 60 * 24)) : 0;
    const selectedPrefs = Object.keys(preferences).filter(k => preferences[k]);

    try {
      setError('');
      const tripData = {
        name: tripName,
        userId: user.uid,
        destination: destination || 'Unspecified',
        budget: parseInt(budget) || 0,
        travelers: parseInt(travelers) || 1,
        days: days,
        preferences: selectedPrefs,
        mealType: mealType,
        accommodationType: accommodationType,
        transportMode: transportMode,
        startDate: startDate,
        endDate: endDate,
        createdAt: new Date(),
        status: 'planned',
      };

      console.log('Saving trip:', tripData);
      const docRef = await addTrip(tripData);
      console.log('Trip saved successfully with ID:', docRef.id);

      // Give user feedback
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: `✅ Trip "${tripName}" saved successfully! Redirecting to My Trips...`
      }]);

      // Small delay to show message, then navigate
      setTimeout(() => {
        navigate('/dashboard');
      }, 1000);
    } catch (err) {
      setError('Failed to save trip: ' + err.message);
      console.error('Error saving trip:', err);
    }
  };

  const handleExportPDF = () => {
    const element = document.getElementById('itinerary-content-to-export');
    if (!element) return;
    const opt = {
      margin: 0.5,
      filename: `SimpliTrip_${destination || 'Itinerary'}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, backgroundColor: '#111827', useCORS: true },
      jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };
    html2pdf().set(opt).from(element).save();
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Step 1: Trip Planning Form */}
        {step === 'form' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="mb-8">
              <h1 className="text-5xl md:text-6xl font-bold text-white mb-2">
                Plan Your Perfect Trip
              </h1>
              <p className="text-xl text-gray-400">Tell us about your dream vacation and let AI create a personalized itinerary just for you.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Left Column - Form */}
              <div className="lg:col-span-2">
                <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl border border-gray-700/50 p-8 shadow-xl">
                  {/* Error */}
                  {error && (
                    <div className="mb-6 p-4 bg-red-900/30 border border-red-500/50 rounded-lg text-red-300">
                      {error}
                    </div>
                  )}

                  {/* Destination and Dates */}
                  <div className="space-y-6 mb-8">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold text-gray-300 mb-2">Starting Point / Current Location</label>
                        <input
                          type="text"
                          value={currentLocation}
                          onChange={(e) => setCurrentLocation(e.target.value)}
                          placeholder="e.g., Delhi, Mumbai..."
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-gray-300 mb-2">Where do you want to go?</label>
                        <input
                          type="text"
                          value={destination}
                          onChange={(e) => setDestination(e.target.value)}
                          placeholder="e.g., Paris, Tokyo, Goa..."
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold text-gray-300 mb-2">Start Date</label>
                        <input
                          type="date"
                          value={startDate}
                          onChange={(e) => setStartDate(e.target.value)}
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-gray-300 mb-2">End Date</label>
                        <input
                          type="date"
                          value={endDate}
                          onChange={(e) => setEndDate(e.target.value)}
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold text-gray-300 mb-2">Budget (₹)</label>
                        <input
                          type="number"
                          value={budget}
                          onChange={(e) => setBudget(e.target.value)}
                          placeholder="50000"
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-gray-300 mb-2">Travelers</label>
                        <input
                          type="number"
                          value={travelers}
                          onChange={(e) => setTravelers(e.target.value)}
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Travel Preferences */}
                  <div className="mb-8">
                    <h3 className="text-lg font-semibold text-white mb-4">Travel Preferences</h3>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      {Object.keys(preferences).map(pref => (
                        <button
                          key={pref}
                          onClick={() => handlePreferenceChange(pref)}
                          className={`p-3 rounded-lg border-2 transition-all text-center ${preferences[pref]
                            ? 'border-cyan-500 bg-cyan-500/20 text-cyan-300'
                            : 'border-gray-600 bg-gray-700/50 text-gray-400 hover:border-gray-500'
                            }`}
                        >
                          <div className="text-2xl mb-1">{categoryIcons[pref]}</div>
                          <div className="text-xs font-semibold capitalize">{pref}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Additional Options */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8 pb-8 border-b border-gray-700">
                    <div>
                      <label className="block text-sm font-semibold text-gray-300 mb-2">Meal Type</label>
                      <select
                        value={mealType}
                        onChange={(e) => setMealType(e.target.value)}
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-500"
                      >
                        <option value="veg">Vegetarian</option>
                        <option value="non-veg">Non-Vegetarian</option>
                        <option value="mixed">Mixed</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-300 mb-2">Accommodation</label>
                      <select
                        value={accommodationType}
                        onChange={(e) => setAccommodationType(e.target.value)}
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-500"
                      >
                        <option value="hotel">Hotel</option>
                        <option value="airbnb">Airbnb</option>
                        <option value="resort">Resort</option>
                        <option value="hostel">Hostel</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-300 mb-2">Transport</label>
                      <select
                        value={transportMode}
                        onChange={(e) => setTransportMode(e.target.value)}
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-500"
                      >
                        <option value="flight">Flight</option>
                        <option value="train">Train</option>
                        <option value="bus">Bus</option>
                        <option value="car">Car Rental</option>
                      </select>
                    </div>
                  </div>

                  {/* Generate Button */}
                  <button
                    onClick={handleGenerateItinerary}
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 disabled:opacity-50 text-white font-bold py-4 px-6 rounded-xl transition-all shadow-lg hover:shadow-cyan-500/30 flex items-center justify-center gap-2"
                  >
                    <span>✨</span>
                    {isLoading ? 'Generating Your Itinerary...' : 'Generate Itinerary'}
                  </button>
                </div>
              </div>

              {/* Right Column - Info Cards */}
              <div className="lg:col-span-1 space-y-4">
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 }}
                  className="bg-gradient-to-br from-cyan-600/20 to-blue-600/20 border border-cyan-500/30 rounded-xl p-6"
                >
                  <div className="text-3xl mb-2">🎯</div>
                  <h4 className="font-bold text-white mb-2">AI-Powered</h4>
                  <p className="text-sm text-gray-300">Our AI understands your preferences and creates personalized itineraries.</p>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                  className="bg-gradient-to-br from-purple-600/20 to-pink-600/20 border border-purple-500/30 rounded-xl p-6"
                >
                  <div className="text-3xl mb-2">💰</div>
                  <h4 className="font-bold text-white mb-2">Budget Friendly</h4>
                  <p className="text-sm text-gray-300">Get cost breakdowns and make the most of your budget.</p>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 }}
                  className="bg-gradient-to-br from-amber-600/20 to-orange-600/20 border border-amber-500/30 rounded-xl p-6"
                >
                  <div className="text-3xl mb-2">🗺️</div>
                  <h4 className="font-bold text-white mb-2">Detailed Plans</h4>
                  <p className="text-sm text-gray-300">Day-by-day itineraries with recommendations and tips.</p>
                </motion.div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Step 2: Chat and Itinerary */}
        {step === 'chat' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold text-white">Your Itinerary</h2>
                <p className="text-gray-400 mt-1">Destination: {destination} | Budget: ₹{budget}</p>
              </div>
              <button
                onClick={() => setStep('form')}
                className="bg-gray-800 hover:bg-gray-700 border border-gray-700 text-white py-2 px-4 rounded-lg transition-all"
              >
                ← Back
              </button>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-900/30 border border-red-500/50 rounded-lg text-red-300">
                {error}
              </div>
            )}

            {/* Split Screen Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[calc(100vh-250px)]">

              {/* Left Column: Chat Messages */}
              <div className="bg-gray-900/60 backdrop-blur-xl border border-gray-700/50 rounded-2xl shadow-2xl flex flex-col h-full overflow-hidden">
                <div id="itinerary-content-to-export" className="flex-1 overflow-y-auto p-6 space-y-4">
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

                {/* Chat Input */}
                <div className="border-t border-gray-700 p-6 bg-gray-900/80">
                  <div className="flex gap-3">
                    <input
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={(e) => { if (e.key === 'Enter' && !isLoading) sendChatMessage(); }}
                      placeholder="Ask for more details, changes, or recommendations..."
                      className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                      disabled={isLoading}
                    />
                    <button
                      onClick={sendChatMessage}
                      disabled={isLoading || !chatInput.trim()}
                      className="bg-cyan-600 hover:bg-cyan-700 disabled:opacity-50 text-white font-bold py-3 px-6 rounded-lg transition-all"
                    >
                      Send
                    </button>
                    <button
                      onClick={handleExportPDF}
                      disabled={isLoading || messages.length <= 1}
                      className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-bold py-3 px-6 rounded-lg transition-all"
                    >
                      Export PDF
                    </button>
                    <button
                      onClick={() => setShowSaveModal(true)}
                      disabled={isLoading}
                      className="bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-bold py-3 px-6 rounded-lg transition-all"
                    >
                      Save Trip
                    </button>
                  </div>
                </div>
              </div>

              {/* Right Column: Live Map */}
              <div className="bg-gray-900/60 backdrop-blur-xl border border-gray-700/50 rounded-2xl shadow-2xl flex flex-col h-full overflow-hidden relative z-0 p-1">
                <InteractiveItineraryMap
                  origin={destination.toLowerCase().includes(' to ') ? destination.split(/ to /i)[0].trim() : null}
                  destination={destination.toLowerCase().includes(' to ') ? destination.split(/ to /i)[1].trim() : destination}
                />
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
                    placeholder="e.g., Summer Goa Getaway"
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500 mb-6"
                  />
                  <div className="flex gap-3">
                    <button
                      onClick={() => setShowSaveModal(false)}
                      className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-2 px-4 rounded-lg transition-all"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSaveTrip}
                      className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg transition-all font-bold"
                    >
                      Save Trip
                    </button>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </motion.div>
        )}
      </div>
    </Layout>
  );
};

export default TripPlannerPage;

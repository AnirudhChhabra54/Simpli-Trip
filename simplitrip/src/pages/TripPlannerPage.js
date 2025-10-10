import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaMapMarkedAlt, FaMoneyBillWave, FaCheckCircle, FaRobot } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import CostBreakdownChart from '../components/CostBreakdownChart';
import DestinationCard from '../components/DestinationCard';
import {
  parseNaturalLanguageQuery,
  getDestinationRecommendations,
  predictTotalCost,
  explainRecommendation,
} from '../services/aiService';
import { addTrip } from '../services/firestore';
import { useUser } from '../context/UserContext';

const TripPlannerPage = () => {
  const navigate = useNavigate();
  const { user } = useUser();
  
  // Wizard steps
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Step 1: Natural Language Input
  const [naturalQuery, setNaturalQuery] = useState('');
  const [aiResponse, setAiResponse] = useState('');

  // Step 2: Preferences
  const [preferences, setPreferences] = useState({
    budget: 50000,
    travelers: 2,
    days: 5,
    categories: [],
    mealType: 'veg',
    accommodationType: 'hotel',
    transportMode: 'flight',
  });

  // Step 3: Recommendations
  const [recommendations, setRecommendations] = useState([]);
  const [selectedDestination, setSelectedDestination] = useState(null);
  const [explanation, setExplanation] = useState('');

  // Step 4: Cost Breakdown
  const [costData, setCostData] = useState(null);

  // Step 5: Final Review
  const [tripName, setTripName] = useState('');

  const steps = [
    { number: 1, title: 'Describe Your Trip', icon: FaRobot },
    { number: 2, title: 'Set Preferences', icon: FaMapMarkedAlt },
    { number: 3, title: 'Choose Destination', icon: FaMapMarkedAlt },
    { number: 4, title: 'Review Costs', icon: FaMoneyBillWave },
    { number: 5, title: 'Finalize Trip', icon: FaCheckCircle },
  ];

  // Step 1: Parse natural language query
  const handleParseQuery = async () => {
    if (!naturalQuery.trim()) {
      setError('Please describe your trip');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const result = await parseNaturalLanguageQuery(naturalQuery);
      
      // Update preferences with ALL parsed data including meal, accommodation, transport
      const updatedPrefs = {
        ...preferences,
        budget: result.budget || preferences.budget,
        travelers: result.travelers || preferences.travelers,
        days: result.duration || preferences.days,
        categories: result.preferences || preferences.categories,
        mealType: result.meal_preference || preferences.mealType,
        accommodationType: result.accommodation_type || preferences.accommodationType,
        transportMode: result.transport_mode || preferences.transportMode,
      };
      
      setPreferences(updatedPrefs);

      // Generate AI response
      let response = "Perfect! I've understood your requirements. ";
      if (result.destination) {
        response += `You want to visit ${result.destination}. `;
      }
      if (result.duration) {
        response += `For ${result.duration} days. `;
      }
      if (result.travelers) {
        response += `With ${result.travelers} ${result.travelers === 1 ? 'person' : 'people'}. `;
      }
      if (result.budget) {
        response += `Budget: ₹${result.budget.toLocaleString('en-IN')}. `;
      }
      if (result.meal_preference) {
        response += `I've noted your ${result.meal_preference} food preference. `;
      }
      if (result.preferences && result.preferences.length > 0) {
        response += `You're interested in ${result.preferences.join(', ')}. `;
      }
      response += "Let's refine your preferences and find the perfect destination!";
      
      setAiResponse(response);
      setCurrentStep(2);
    } catch (err) {
      setError(err.message || 'Failed to parse your query. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Step 2: Get recommendations based on preferences
  const handleGetRecommendations = async () => {
    setIsLoading(true);
    setError('');

    try {
      const result = await getDestinationRecommendations(preferences, 6);
      setRecommendations(result.recommendations || []);
      
      // Generate AI response for recommendations
      const count = result.recommendations?.length || 0;
      let response = `Great! I've found ${count} amazing destinations that match your preferences. `;
      if (preferences.budget) {
        response += `All within your budget of ₹${preferences.budget.toLocaleString('en-IN')}. `;
      }
      response += "Each destination is carefully selected based on your interests. Click on any card to see why it's perfect for you!";
      setAiResponse(response);
      
      setCurrentStep(3);
    } catch (err) {
      setError(err.message || 'Failed to get recommendations');
    } finally {
      setIsLoading(false);
    }
  };

  // Step 3: Select destination and get cost
  const handleSelectDestination = async (destination) => {
    setSelectedDestination(destination);
    setIsLoading(true);
    setError('');

    try {
      // Get cost prediction
      const costResult = await predictTotalCost({
        destination: destination.destination_name,
        travelers: preferences.travelers,
        days: preferences.days,
        preferences: {
          meal_type: preferences.mealType,
          accommodation_type: preferences.accommodationType,
          transport_mode: preferences.transportMode,
        },
      });

      setCostData(costResult);
      setCurrentStep(4);
    } catch (err) {
      setError(err.message || 'Failed to calculate costs');
    } finally {
      setIsLoading(false);
    }
  };

  // Step 4: Get explanation for recommendation
  const handleExplainRecommendation = async (destination) => {
    setIsLoading(true);
    try {
      const result = await explainRecommendation(
        destination.destination_name,
        preferences
      );
      setExplanation(result.explanation);
    } catch (err) {
      console.error('Failed to get explanation:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Step 5: Save trip
  const handleSaveTrip = async () => {
    if (!tripName.trim()) {
      setError('Please enter a trip name');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const tripData = {
        name: tripName,
        userId: user.uid,
        destination: selectedDestination.destination_name,
        state: selectedDestination.state,
        budget: preferences.budget,
        estimatedCost: costData.total_cost,
        travelers: preferences.travelers,
        days: preferences.days,
        preferences: preferences,
        costBreakdown: costData.breakdown,
        createdAt: new Date(),
        status: 'planned',
      };

      await addTrip(tripData);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Failed to save trip');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            {steps.map((step, index) => (
              <React.Fragment key={step.number}>
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex flex-col items-center"
                >
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center mb-2 transition-colors ${
                      currentStep >= step.number
                        ? 'bg-cyan-500 text-white'
                        : 'bg-gray-700 text-gray-400'
                    }`}
                  >
                    <step.icon className="text-xl" />
                  </div>
                  <p
                    className={`text-sm text-center ${
                      currentStep >= step.number ? 'text-white' : 'text-gray-400'
                    }`}
                  >
                    {step.title}
                  </p>
                </motion.div>
                {index < steps.length - 1 && (
                  <div
                    className={`flex-1 h-1 mx-2 transition-colors ${
                      currentStep > step.number ? 'bg-cyan-500' : 'bg-gray-700'
                    }`}
                  />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-red-500/20 border border-red-500 rounded-lg"
          >
            <p className="text-red-400">{error}</p>
          </motion.div>
        )}

        {/* Step Content */}
        <AnimatePresence mode="wait">
          {/* Step 1: Natural Language Input */}
          {currentStep === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              className="bg-gray-800 rounded-xl p-8"
            >
              <h2 className="text-3xl font-bold text-white mb-4">
                Describe Your Dream Trip
              </h2>
              <p className="text-gray-400 mb-6">
                Tell us about your trip in your own words. Our AI will understand and help you plan!
              </p>

              <textarea
                value={naturalQuery}
                onChange={(e) => setNaturalQuery(e.target.value)}
                placeholder="Example: Plan a relaxing 5-day beach vacation to Goa for 2 people under ₹50,000 with non-veg food"
                className="w-full h-32 px-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 mb-4"
              />

              <div className="flex gap-4">
                <button
                  onClick={handleParseQuery}
                  disabled={isLoading}
                  className="flex-1 bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Processing...' : 'Continue'}
                </button>
              </div>

              {/* Example Queries */}
              <div className="mt-6">
                <p className="text-gray-400 text-sm mb-3">Try these examples:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {[
                    'Plan a 7-day adventure trip to Ladakh for 4 people with non-veg food',
                    'Weekend getaway to Udaipur for 2 under ₹30,000 with veg food',
                    'Family trip to Kerala for 5 days with kids staying in resorts',
                    'Budget backpacking trip to Himachal for 10 days in hostels',
                  ].map((example, index) => (
                    <button
                      key={index}
                      onClick={() => setNaturalQuery(example)}
                      className="text-left p-3 bg-gray-700 hover:bg-gray-600 rounded-lg text-gray-300 text-sm transition-colors"
                    >
                      {example}
                    </button>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {/* Step 2: Preferences */}
          {currentStep === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              className="bg-gray-800 rounded-xl p-8"
            >
              <h2 className="text-3xl font-bold text-white mb-4">
                Refine Your Preferences
              </h2>
              
              {/* AI Response */}
              {aiResponse && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-6 p-4 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-500/30 rounded-lg"
                >
                  <div className="flex items-start gap-3">
                    <FaRobot className="text-cyan-400 text-2xl mt-1 flex-shrink-0" />
                    <p className="text-white">{aiResponse}</p>
                  </div>
                </motion.div>
              )}
              
              <p className="text-gray-400 mb-6">
                I've pre-filled your preferences based on your description. Feel free to adjust them!
              </p>

              <div className="space-y-6">
                {/* Budget Slider */}
                <div>
                  <label className="block text-white font-semibold mb-2">
                    Budget: ₹{preferences.budget.toLocaleString('en-IN')}
                  </label>
                  <input
                    type="range"
                    min="10000"
                    max="200000"
                    step="5000"
                    value={preferences.budget}
                    onChange={(e) =>
                      setPreferences({ ...preferences, budget: parseInt(e.target.value) })
                    }
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                  />
                  <div className="flex justify-between text-gray-400 text-sm mt-1">
                    <span>₹10,000</span>
                    <span>₹2,00,000</span>
                  </div>
                </div>

                {/* Travelers */}
                <div>
                  <label className="block text-white font-semibold mb-2">
                    Number of Travelers
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={preferences.travelers}
                    onChange={(e) =>
                      setPreferences({ ...preferences, travelers: parseInt(e.target.value) })
                    }
                    className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>

                {/* Days */}
                <div>
                  <label className="block text-white font-semibold mb-2">
                    Duration (Days)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="30"
                    value={preferences.days}
                    onChange={(e) =>
                      setPreferences({ ...preferences, days: parseInt(e.target.value) })
                    }
                    className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>

                {/* Categories */}
                <div>
                  <label className="block text-white font-semibold mb-2">
                    Preferred Categories
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {['Beach', 'Mountain', 'Historical', 'Adventure', 'Wildlife', 'Cultural', 'Spiritual', 'Relaxation'].map(
                      (category) => (
                        <button
                          key={category}
                          onClick={() => {
                            const cats = preferences.categories.includes(category)
                              ? preferences.categories.filter((c) => c !== category)
                              : [...preferences.categories, category];
                            setPreferences({ ...preferences, categories: cats });
                          }}
                          className={`py-2 px-4 rounded-lg font-semibold transition-colors ${
                            preferences.categories.includes(category)
                              ? 'bg-cyan-500 text-white'
                              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                          }`}
                        >
                          {category}
                        </button>
                      )
                    )}
                  </div>
                </div>

                {/* Meal Type */}
                <div>
                  <label className="block text-white font-semibold mb-2">
                    Meal Preference
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {['veg', 'non-veg', 'vegan'].map((type) => (
                      <button
                        key={type}
                        onClick={() => setPreferences({ ...preferences, mealType: type })}
                        className={`py-2 px-4 rounded-lg font-semibold capitalize transition-colors ${
                          preferences.mealType === type
                            ? 'bg-cyan-500 text-white'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                      >
                        {type}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Accommodation Type */}
                <div>
                  <label className="block text-white font-semibold mb-2">
                    Accommodation Type
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {['hotel', 'resort', 'hostel'].map((type) => (
                      <button
                        key={type}
                        onClick={() =>
                          setPreferences({ ...preferences, accommodationType: type })
                        }
                        className={`py-2 px-4 rounded-lg font-semibold capitalize transition-colors ${
                          preferences.accommodationType === type
                            ? 'bg-cyan-500 text-white'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                      >
                        {type}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Transport Mode */}
                <div>
                  <label className="block text-white font-semibold mb-2">
                    Transport Mode
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {['flight', 'train', 'bus'].map((mode) => (
                      <button
                        key={mode}
                        onClick={() => setPreferences({ ...preferences, transportMode: mode })}
                        className={`py-2 px-4 rounded-lg font-semibold capitalize transition-colors ${
                          preferences.transportMode === mode
                            ? 'bg-cyan-500 text-white'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                      >
                        {mode}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex gap-4 mt-8">
                <button
                  onClick={() => setCurrentStep(1)}
                  className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-lg transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={handleGetRecommendations}
                  disabled={isLoading}
                  className="flex-1 bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Getting Recommendations...' : 'Get Recommendations'}
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 3: Recommendations */}
          {currentStep === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
            >
              <h2 className="text-3xl font-bold text-white mb-4">
                AI-Powered Recommendations
              </h2>
              
              {/* AI Response */}
              {aiResponse && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-6 p-4 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-500/30 rounded-lg"
                >
                  <div className="flex items-start gap-3">
                    <FaRobot className="text-cyan-400 text-2xl mt-1 flex-shrink-0" />
                    <p className="text-white">{aiResponse}</p>
                  </div>
                </motion.div>
              )}

              {recommendations.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                  {recommendations.map((destination, index) => (
                    <DestinationCard
                      key={index}
                      destination={destination}
                      onSelect={handleSelectDestination}
                      onExplain={handleExplainRecommendation}
                      isSelected={selectedDestination?.destination_name === destination.destination_name}
                      showExplanation={true}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-400">No recommendations found. Try adjusting your preferences.</p>
                </div>
              )}

              {/* Explanation Modal */}
              {explanation && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
                  onClick={() => setExplanation('')}
                >
                  <motion.div
                    initial={{ scale: 0.9 }}
                    animate={{ scale: 1 }}
                    className="bg-gray-800 rounded-xl p-6 max-w-2xl w-full"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <h3 className="text-2xl font-bold text-white mb-4">
                      Why We Recommend This
                    </h3>
                    <p className="text-gray-300 mb-6">{explanation}</p>
                    <button
                      onClick={() => setExplanation('')}
                      className="bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-2 px-6 rounded-lg transition-colors"
                    >
                      Close
                    </button>
                  </motion.div>
                </motion.div>
              )}

              <div className="flex gap-4">
                <button
                  onClick={() => setCurrentStep(2)}
                  className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-lg transition-colors"
                >
                  Back
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 4: Cost Breakdown */}
          {currentStep === 4 && costData && (
            <motion.div
              key="step4"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
            >
              <h2 className="text-3xl font-bold text-white mb-4">
                Cost Breakdown for {selectedDestination?.destination_name}
              </h2>
              <p className="text-gray-400 mb-6">
                Here's a detailed breakdown of your estimated trip costs
              </p>

              <CostBreakdownChart costData={costData} showOptimization={true} />

              <div className="flex gap-4 mt-8">
                <button
                  onClick={() => setCurrentStep(3)}
                  className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-lg transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={() => setCurrentStep(5)}
                  className="flex-1 bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-3 px-6 rounded-lg transition-colors"
                >
                  Continue to Finalize
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 5: Finalize Trip */}
          {currentStep === 5 && (
            <motion.div
              key="step5"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              className="bg-gray-800 rounded-xl p-8"
            >
              <h2 className="text-3xl font-bold text-white mb-4">
                Finalize Your Trip
              </h2>
              <p className="text-gray-400 mb-6">
                Give your trip a name and save it to your dashboard
              </p>

              {/* Trip Summary */}
              <div className="bg-gray-700 rounded-lg p-6 mb-6">
                <h3 className="text-xl font-bold text-white mb-4">Trip Summary</h3>
                <div className="grid grid-cols-2 gap-4 text-gray-300">
                  <div>
                    <p className="text-gray-400 text-sm">Destination</p>
                    <p className="font-semibold">{selectedDestination?.destination_name}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Duration</p>
                    <p className="font-semibold">{preferences.days} days</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Travelers</p>
                    <p className="font-semibold">{preferences.travelers} people</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Estimated Cost</p>
                    <p className="font-semibold">₹{costData?.total_cost.toLocaleString('en-IN')}</p>
                  </div>
                </div>
              </div>

              {/* Trip Name Input */}
              <div className="mb-6">
                <label className="block text-white font-semibold mb-2">
                  Trip Name
                </label>
                <input
                  type="text"
                  value={tripName}
                  onChange={(e) => setTripName(e.target.value)}
                  placeholder="e.g., Summer Vacation 2024"
                  className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div className="flex gap-4">
                <button
                  onClick={() => setCurrentStep(4)}
                  className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-lg transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={handleSaveTrip}
                  disabled={isLoading}
                  className="flex-1 bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white font-bold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Saving...' : 'Save Trip'}
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </Layout>
  );
};

export default TripPlannerPage;

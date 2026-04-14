import React from 'react';

/**
 * AIRecommender - Shows personalized, data-driven travel insights.
 *
 * `type` can be "dashboard" or "trip". An optional `trips` array (each trip has
 * { name, destination, budget, preferences }) lets the card surface real
 * budget/next-step suggestions instead of static placeholder text.
 */
const AIRecommender = ({ type = 'dashboard', trips = [] }) => {
  const heading = type === 'trip' ? 'AI Budget Optimizer' : 'AI Recommendations';

  let body;

  if (type === 'trip') {
    body = [
      { icon: '🍽️', title: 'Food & Dining', text: 'Allocate ~25% of the budget to meals for local cuisine experiences without overspending.' },
      { icon: '🎯', title: 'Activities', text: 'Keep ~35% flexible for experiences and day trips that match your interests.' },
      { icon: '🏨', title: 'Stay', text: 'Booking outside peak dates can free up 15-20% for experiences or upgrades.' },
    ];
  } else if (trips && trips.length > 0) {
    const top = trips[0];
    body = {
      title: top.destination ? `Make the most of ${top.destination}` : 'Make the most of your trips',
      text: top.budget
        ? `Your plan to ${top.destination || 'your destination'} has a budget of ₹${top.budget}. Focus on 1-2 hero experiences and mix in free local gems.`
        : 'Record a budget for your trips to unlock smart allocation tips.',
    };
  } else {
    body = {
      title: 'Start planning for tailored insights',
      text: 'Plan your first trip and SimpliTrip will surface budget, weather, and activity recommendations tuned to your preferences.',
    };
  }

  return (
    <div className="mt-16">
      <h2 className="text-3xl font-bold mb-4">{heading}</h2>
      {Array.isArray(body) ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {body.map((item, i) => (
            <div key={i} className="bg-gray-800/60 border border-gray-700 rounded-xl p-5">
              <div className="text-2xl mb-2">{item.icon}</div>
              <h3 className="font-bold text-white mb-1">{item.title}</h3>
              <p className="text-gray-300 text-sm">{item.text}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold text-white mb-2">{body.title}</h3>
          <p className="text-gray-300">{body.text}</p>
        </div>
      )}
    </div>
  );
};

export default AIRecommender;
import React from 'react';

const AIRecommender = ({ type }) => {
  const recommendations = {
    dashboard: "Based on your travel history, we recommend a trip to Bali, Indonesia.",
    trip: "We suggest reducing your restaurant budget by $50 and allocating it towards activities to maximize your experience."
  };

  return (
    <div className="mt-16">
      <h2 className="text-3xl font-bold mb-4">{type === 'dashboard' ? 'AI Recommendations' : 'AI Budget Optimizer'}</h2>
      <div className="bg-gray-800 p-6 rounded-lg">
        <p className="text-lg">{recommendations[type]}</p>
      </div>
    </div>
  );
};

export default AIRecommender;
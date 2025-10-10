import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { FaChartPie, FaChartBar, FaRupeeSign } from 'react-icons/fa';
import { formatCurrency } from '../services/aiService';

const CostBreakdownChart = ({ costData, showOptimization = false }) => {
  const [chartType, setChartType] = useState('pie'); // 'pie' or 'bar'

  if (!costData || !costData.breakdown) {
    return (
      <div className="bg-gray-800 rounded-xl p-6 text-center">
        <p className="text-gray-400">No cost data available</p>
      </div>
    );
  }

  const { breakdown, total_cost, confidence } = costData;

  // Prepare data for charts
  const chartData = Object.entries(breakdown).map(([key, value]) => ({
    name: key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
    value: value,
    percentage: ((value / total_cost) * 100).toFixed(1),
  }));

  // Colors for different categories
  const COLORS = {
    flights: '#06b6d4',      // Cyan
    accommodation: '#8b5cf6', // Purple
    meals: '#f97316',         // Orange
    activities: '#10b981',    // Green
    local_transport: '#f59e0b', // Amber
    contingency: '#ef4444',   // Red
  };

  const getColor = (index) => {
    const colorKeys = Object.keys(COLORS);
    return COLORS[colorKeys[index % colorKeys.length]];
  };

  // Custom label for pie chart
  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percentage }) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        className="text-sm font-bold"
      >
        {`${percentage}%`}
      </text>
    );
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-900 border border-cyan-500 rounded-lg p-3 shadow-lg">
          <p className="text-white font-semibold">{payload[0].name}</p>
          <p className="text-cyan-400 font-bold">{formatCurrency(payload[0].value)}</p>
          <p className="text-gray-400 text-sm">{payload[0].payload.percentage}% of total</p>
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gray-800 rounded-xl p-6 shadow-lg"
    >
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-2xl font-bold text-white mb-1">Cost Breakdown</h3>
          <p className="text-gray-400 text-sm">
            Confidence: <span className="text-cyan-400 font-semibold">{(confidence * 100).toFixed(0)}%</span>
          </p>
        </div>
        
        {/* Chart Type Toggle */}
        <div className="flex gap-2 bg-gray-700 rounded-lg p-1">
          <button
            onClick={() => setChartType('pie')}
            className={`p-2 rounded-lg transition-colors ${
              chartType === 'pie' ? 'bg-cyan-500 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            <FaChartPie className="text-xl" />
          </button>
          <button
            onClick={() => setChartType('bar')}
            className={`p-2 rounded-lg transition-colors ${
              chartType === 'bar' ? 'bg-cyan-500 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            <FaChartBar className="text-xl" />
          </button>
        </div>
      </div>

      {/* Total Cost Display */}
      <motion.div
        initial={{ scale: 0.9 }}
        animate={{ scale: 1 }}
        className="bg-gradient-to-r from-cyan-500 to-purple-500 rounded-xl p-6 mb-6 text-center"
      >
        <p className="text-white text-sm font-semibold mb-1">Total Estimated Cost</p>
        <div className="flex items-center justify-center">
          <FaRupeeSign className="text-white text-3xl mr-2" />
          <p className="text-white text-5xl font-bold">
            {total_cost.toLocaleString('en-IN')}
          </p>
        </div>
      </motion.div>

      {/* Chart */}
      <div className="mb-6">
        {chartType === 'pie' ? (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderCustomLabel}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
                animationBegin={0}
                animationDuration={800}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getColor(index)} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="name" 
                stroke="#9ca3af"
                angle={-45}
                textAnchor="end"
                height={100}
              />
              <YAxis stroke="#9ca3af" />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" fill="#06b6d4" radius={[8, 8, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getColor(index)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Detailed Breakdown */}
      <div className="space-y-3">
        {chartData.map((item, index) => (
          <motion.div
            key={item.name}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center justify-between p-3 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: getColor(index) }}
              />
              <span className="text-white font-medium">{item.name}</span>
            </div>
            <div className="text-right">
              <p className="text-white font-bold">{formatCurrency(item.value)}</p>
              <p className="text-gray-400 text-sm">{item.percentage}%</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Optimization Suggestions */}
      {showOptimization && costData.suggestions && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-4 bg-purple-500/20 border border-purple-500 rounded-lg"
        >
          <h4 className="text-purple-400 font-semibold mb-2 flex items-center">
            <span className="mr-2">💡</span>
            Budget Optimization Tips
          </h4>
          <ul className="space-y-2">
            {costData.suggestions.map((suggestion, index) => (
              <li key={index} className="text-gray-300 text-sm flex items-start">
                <span className="text-purple-400 mr-2">•</span>
                {suggestion}
              </li>
            ))}
          </ul>
        </motion.div>
      )}
    </motion.div>
  );
};

export default CostBreakdownChart;

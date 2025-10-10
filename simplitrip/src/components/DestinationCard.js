import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FaStar, FaMapMarkerAlt, FaCalendarAlt, FaHeart, FaInfoCircle } from 'react-icons/fa';

const DestinationCard = ({ 
  destination, 
  onSelect, 
  onExplain,
  isSelected = false,
  showExplanation = false 
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);

  const {
    destination_name,
    state,
    category,
    rating,
    best_time_to_visit,
    score,
    image_url,
    description,
  } = destination;

  // Default image if none provided
  const imageUrl = image_url || `https://source.unsplash.com/800x600/?${destination_name},india,travel`;

  const handleFavoriteClick = (e) => {
    e.stopPropagation();
    setIsFavorite(!isFavorite);
  };

  const handleExplainClick = (e) => {
    e.stopPropagation();
    if (onExplain) {
      onExplain(destination);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={{ y: -8, scale: 1.02 }}
      transition={{ duration: 0.3 }}
      className={`relative bg-gray-800 rounded-xl overflow-hidden shadow-lg cursor-pointer ${
        isSelected ? 'ring-4 ring-cyan-500' : ''
      }`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => onSelect && onSelect(destination)}
    >
      {/* Image Section */}
      <div className="relative h-48 overflow-hidden">
        <motion.img
          src={imageUrl}
          alt={destination_name}
          className="w-full h-full object-cover"
          animate={{ scale: isHovered ? 1.1 : 1 }}
          transition={{ duration: 0.3 }}
        />
        
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-transparent to-transparent" />
        
        {/* Favorite Button */}
        <motion.button
          whileHover={{ scale: 1.2 }}
          whileTap={{ scale: 0.9 }}
          onClick={handleFavoriteClick}
          className="absolute top-3 right-3 p-2 bg-gray-900/70 backdrop-blur-sm rounded-full hover:bg-gray-900/90 transition-colors"
        >
          <FaHeart className={`text-lg ${isFavorite ? 'text-red-500' : 'text-white'}`} />
        </motion.button>

        {/* Score Badge */}
        {score && (
          <div className="absolute top-3 left-3 px-3 py-1 bg-cyan-500/90 backdrop-blur-sm rounded-full">
            <span className="text-white font-bold text-sm">
              {Math.round(score * 100)}% Match
            </span>
          </div>
        )}

        {/* Category Badge */}
        <div className="absolute bottom-3 left-3 px-3 py-1 bg-purple-500/90 backdrop-blur-sm rounded-full">
          <span className="text-white font-semibold text-xs uppercase tracking-wide">
            {category}
          </span>
        </div>
      </div>

      {/* Content Section */}
      <div className="p-5">
        {/* Title and Location */}
        <div className="mb-3">
          <h3 className="text-xl font-bold text-white mb-1 line-clamp-1">
            {destination_name}
          </h3>
          <div className="flex items-center text-gray-400 text-sm">
            <FaMapMarkerAlt className="mr-1" />
            <span>{state}</span>
          </div>
        </div>

        {/* Rating */}
        <div className="flex items-center mb-3">
          <div className="flex items-center bg-yellow-500/20 px-2 py-1 rounded-lg">
            <FaStar className="text-yellow-500 mr-1" />
            <span className="text-white font-semibold">{rating}</span>
          </div>
          <span className="text-gray-400 text-sm ml-2">Rating</span>
        </div>

        {/* Best Time to Visit */}
        {best_time_to_visit && (
          <div className="flex items-center text-gray-300 text-sm mb-3">
            <FaCalendarAlt className="mr-2 text-cyan-500" />
            <span>Best: {best_time_to_visit}</span>
          </div>
        )}

        {/* Description */}
        {description && (
          <p className="text-gray-400 text-sm line-clamp-2 mb-3">
            {description}
          </p>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2 mt-4">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => onSelect && onSelect(destination)}
            className={`flex-1 py-2 px-4 rounded-lg font-semibold transition-colors ${
              isSelected
                ? 'bg-cyan-500 text-white'
                : 'bg-gray-700 text-white hover:bg-gray-600'
            }`}
          >
            {isSelected ? 'Selected' : 'Select'}
          </motion.button>
          
          {showExplanation && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleExplainClick}
              className="p-2 bg-purple-500/20 text-purple-400 rounded-lg hover:bg-purple-500/30 transition-colors"
              title="Why recommended?"
            >
              <FaInfoCircle className="text-xl" />
            </motion.button>
          )}
        </div>
      </div>

      {/* Hover Effect Border */}
      <motion.div
        className="absolute inset-0 border-2 border-cyan-500 rounded-xl pointer-events-none"
        initial={{ opacity: 0 }}
        animate={{ opacity: isHovered ? 1 : 0 }}
        transition={{ duration: 0.2 }}
      />
    </motion.div>
  );
};

export default DestinationCard;

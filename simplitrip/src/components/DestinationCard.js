
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FaMapMarkerAlt, FaHeart, FaPlane, FaHotel } from 'react-icons/fa';

const DestinationCard = ({ destination, onSelect, isSelected = false }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);

  const { destination_name, state, match_score, image, description, flight_estimate, hotel_estimate } = destination;

  const formatCost = (amount) => amount ? `₹${amount.toLocaleString('en-IN')}` : 'N/A';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -8, scale: 1.02 }}
      className={`relative bg-gray-800 rounded-xl overflow-hidden shadow-lg cursor-pointer border border-gray-700/50 ${isSelected ? 'ring-4 ring-cyan-500' : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => onSelect && onSelect(destination)}
    >
      {/* Image */}
      <div className="relative h-48 overflow-hidden">
        <motion.img src={image || `https://source.unsplash.com/800x600/?${destination_name},travel`} alt={destination_name} className="w-full h-full object-cover" animate={{ scale: isHovered ? 1.1 : 1 }} transition={{ duration: 0.3 }} />
        <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-transparent to-transparent" />
        <motion.button whileHover={{ scale: 1.2 }} onClick={(e) => { e.stopPropagation(); setIsFavorite(!isFavorite); }} className="absolute top-3 right-3 p-2 bg-gray-900/70 rounded-full">
          <FaHeart className={`text-lg ${isFavorite ? 'text-red-500' : 'text-white'}`} />
        </motion.button>
        {match_score && <div className="absolute top-3 left-3 px-3 py-1 bg-cyan-600/90 rounded-full"><span className="text-white font-bold text-xs">{match_score}% Match</span></div>}
      </div>

      {/* Content */}
      <div className="p-5">
        <div className="flex justify-between items-start mb-3">
          <div>
            <h3 className="text-xl font-bold text-white mb-1 line-clamp-1">{destination_name}</h3>
            <div className="flex items-center text-gray-400 text-sm"><FaMapMarkerAlt className="mr-1 text-cyan-500" /><span>{state || "India"}</span></div>
          </div>
        </div>

        {/* Pricing */}
        <div className="grid grid-cols-2 gap-2 mb-4 bg-gray-700/30 p-3 rounded-lg">
          <div className="flex items-center space-x-2">
            <div className="p-1.5 bg-blue-500/20 rounded-md"><FaPlane className="text-blue-400 text-sm" /></div>
            <div><p className="text-[10px] text-gray-400 uppercase">Flight</p><p className="text-sm font-semibold text-white">{formatCost(flight_estimate)}</p></div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="p-1.5 bg-purple-500/20 rounded-md"><FaHotel className="text-purple-400 text-sm" /></div>
            <div><p className="text-[10px] text-gray-400 uppercase">Hotel/Night</p><p className="text-sm font-semibold text-white">{formatCost(hotel_estimate)}</p></div>
          </div>
        </div>

        {description && <p className="text-gray-400 text-xs line-clamp-2 mb-4 italic">"{description}"</p>}

        <motion.button whileHover={{ scale: 1.02 }} className={`w-full py-2.5 px-4 rounded-xl font-semibold text-sm ${isSelected ? 'bg-green-600 text-white' : 'bg-cyan-600 text-white hover:bg-cyan-500'}`}>
          {isSelected ? 'Selected' : 'Generate Itinerary'}
        </motion.button>
      </div>
    </motion.div>
  );
};

export default DestinationCard;
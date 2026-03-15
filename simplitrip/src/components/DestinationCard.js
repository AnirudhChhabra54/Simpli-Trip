import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FaMapMarkerAlt, FaHeart, FaPlane, FaHotel, FaArrowRight } from 'react-icons/fa';

// Curated high-resolution destination image lookup
const fallbackImages = {
  goa: 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?q=80&w=800&auto=format&fit=crop',
  ladakh: 'https://images.unsplash.com/photo-1581793745862-99fde7fa73d2?q=80&w=800&auto=format&fit=crop',
  kerala: 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?q=80&w=800&auto=format&fit=crop',
  jaipur: 'https://images.unsplash.com/photo-1599661046289-e31897846e41?q=80&w=800&auto=format&fit=crop',
  kashmir: 'https://images.unsplash.com/photo-1566837945700-30057527ade0?q=80&w=800&auto=format&fit=crop',
  manali: 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?q=80&w=800&auto=format&fit=crop',
  mumbai: 'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?q=80&w=800&auto=format&fit=crop',
  delhi: 'https://images.unsplash.com/photo-1587474260584-136574528ed5?q=80&w=800&auto=format&fit=crop',
  udaipur: 'https://images.unsplash.com/photo-1615836245337-f5b9b2303f10?q=80&w=800&auto=format&fit=crop',
  default: 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?q=80&w=800&auto=format&fit=crop',
};

const getImageUrl = (name, customImage) => {
  if (customImage && !customImage.includes('source.unsplash.com')) return customImage;
  const key = Object.keys(fallbackImages).find((k) =>
    name?.toLowerCase().includes(k)
  );
  return key ? fallbackImages[key] : fallbackImages.default;
};

const DestinationCard = ({ destination, onSelect, isSelected = false }) => {
  const [isFavorite, setIsFavorite] = useState(false);

  const { destination_name, state, match_score, image, description, flight_estimate, hotel_estimate } = destination || {};

  const formatCost = (amount) => (amount ? `₹${amount.toLocaleString('en-IN')}` : '₹3,500');
  const displayImage = getImageUrl(destination_name, image);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -6 }}
      className={`relative rounded-3xl overflow-hidden glass-cinema-card cursor-pointer flex flex-col justify-between group ${
        isSelected ? 'ring-2 ring-cyan-400 shadow-xl shadow-cyan-500/20' : ''
      }`}
      onClick={() => onSelect && onSelect(destination)}
    >
      {/* Scenic Image Container */}
      <div className="relative h-52 overflow-hidden">
        <img
          src={displayImage}
          alt={destination_name}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ease-out"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#080f24] via-[#080f24]/20 to-transparent" />

        {/* Favorite Heart Toggle */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            setIsFavorite(!isFavorite);
          }}
          className="absolute top-3.5 right-3.5 w-9 h-9 rounded-full glass-pill flex items-center justify-center hover:scale-110 transition-transform"
        >
          <FaHeart className={`text-sm ${isFavorite ? 'text-rose-500' : 'text-slate-200'}`} />
        </button>

        {/* Match Score Badge */}
        {match_score && (
          <div className="absolute top-3.5 left-3.5 px-3 py-1 rounded-full glass-pill text-xs font-bold text-white flex items-center gap-1.5 border border-cyan-500/30">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            <span>{match_score}% Match</span>
          </div>
        )}

        {/* Destination Name on Image */}
        <div className="absolute bottom-3 left-4 right-4">
          <div className="flex items-center text-cyan-300 text-xs font-semibold mb-0.5">
            <FaMapMarkerAlt className="mr-1 text-[11px]" />
            <span>{state || 'India'}</span>
          </div>
          <h3 className="text-xl font-bold text-white font-display leading-tight truncate">
            {destination_name}
          </h3>
        </div>
      </div>

      {/* Card Content & Pricing */}
      <div className="p-5 flex-1 flex flex-col justify-between">
        {description && (
          <p className="text-slate-300 text-xs line-clamp-2 mb-4 leading-relaxed font-light">
            {description}
          </p>
        )}

        {/* Cost Matrix Grid */}
        <div className="grid grid-cols-2 gap-2.5 mb-4 p-2.5 rounded-2xl bg-white/[0.03] border border-white/5">
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center text-xs">
              <FaPlane />
            </div>
            <div>
              <p className="text-[9px] text-slate-400 uppercase font-semibold">Flight</p>
              <p className="text-xs font-bold text-white">{formatCost(flight_estimate)}</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center text-xs">
              <FaHotel />
            </div>
            <div>
              <p className="text-[9px] text-slate-400 uppercase font-semibold">Stay / Night</p>
              <p className="text-xs font-bold text-white">{formatCost(hotel_estimate)}</p>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <button
          className={`w-full py-2.5 px-4 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            isSelected
              ? 'bg-emerald-500 text-black shadow-lg shadow-emerald-500/20'
              : 'btn-cinema-primary'
          }`}
        >
          <span>{isSelected ? '✓ Selected Destination' : 'Select Destination'}</span>
          {!isSelected && <FaArrowRight className="text-[10px]" />}
        </button>
      </div>
    </motion.div>
  );
};

export default DestinationCard;
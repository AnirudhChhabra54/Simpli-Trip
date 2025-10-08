import React, { useState } from 'react';

const TripForm = ({ onSubmit, initialData = {}, onCancel }) => {
    const [trip, setTrip] = useState(initialData);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setTrip({ ...trip, [name]: value });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(trip);
    };

    return (
        <form onSubmit={handleSubmit} className="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">{initialData.id ? 'Edit Trip' : 'Create a New Trip'}</h2>
            <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Trip Name</label>
                <input
                    type="text"
                    name="name"
                    value={trip.name || ''}
                    onChange={handleChange}
                    placeholder="Trip Name"
                    className="w-full px-3 py-2 text-gray-900 bg-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
            </div>
            <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Budget</label>
                <input
                    type="number"
                    name="budget"
                    value={trip.budget || 0}
                    onChange={handleChange}
                    className="w-full px-3 py-2 text-gray-900 bg-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
            </div>
            <div className="flex justify-end space-x-4">
                {onCancel && <button type="button" onClick={onCancel} className="text-gray-400 hover:text-white">Cancel</button>}
                <button type="submit" className="bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-2 px-4 rounded-lg">{initialData.id ? 'Save Changes' : 'Create'}</button>
            </div>
        </form>
    );
};

export default TripForm;

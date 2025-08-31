import React from 'react';
import { useParams } from 'react-router-dom';

const TripDetailPage = () => {
  const { id } = useParams();

  return (
    <div>
      <h2>Trip Detail Page</h2>
      <p>Details for trip with ID: {id}</p>
    </div>
  );
};

export default TripDetailPage;
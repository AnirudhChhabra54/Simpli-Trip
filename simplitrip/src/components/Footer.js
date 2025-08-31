import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-gray-100 text-gray-600 text-center py-4 text-sm">
      <div className="container mx-auto">
        &copy; {new Date().getFullYear()} SimpliTrip. All rights reserved.
      </div>
    </footer>
  );
};

export default Footer;
import React from 'react';

const Footer = () => {
    return (
        <footer className="bg-gray-800 p-4 mt-8">
            <div className="container mx-auto text-center text-gray-500">
                &copy; {new Date().getFullYear()} SimpliTrip. All rights reserved.
            </div>
        </footer>
    );
};

export default Footer;

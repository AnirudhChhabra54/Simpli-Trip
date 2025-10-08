import React from 'react';
import Header from './Header';
import Footer from './Footer';

const Layout = ({ children }) => {
    return (
        <div className="min-h-screen bg-gray-900 text-white">
            <Header />
            <main className="p-8">
                {children}
            </main>
            <Footer />
        </div>
    );
};

export default Layout;
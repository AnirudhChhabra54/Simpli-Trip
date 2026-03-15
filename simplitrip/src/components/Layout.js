import React from 'react';
import Header from './Header';
import Footer from './Footer';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-[#040714] text-slate-100 flex flex-col relative overflow-x-hidden">
      {/* Subtle Aurora Ambient Lights */}
      <div className="aurora-mesh w-[500px] h-[500px] bg-cyan-600/10 top-0 left-[-10%] pointer-events-none" />
      <div className="aurora-mesh w-[500px] h-[500px] bg-purple-600/10 bottom-[20%] right-[-10%] pointer-events-none" />

      <Header />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {children}
      </main>
      <Footer />
    </div>
  );
};

export default Layout;
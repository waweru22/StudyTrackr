import React from 'react';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';

const LandingPage: React.FC = () => {
    return (
        <div className="min-h-screen bg-white font-sans text-gray-900 selection:bg-blue-100 selection:text-blue-900">
            <Navbar />
            <main>
                <Hero />
            </main>

            {/* Simple Footer/Copyright for completeness similar to designs usually implies valid page */}
            {/* <footer className="py-8 text-center text-gray-400 text-sm">
        © 2026 StudyTrackr. All rights reserved.
      </footer> */}
        </div>
    );
};

export default LandingPage;

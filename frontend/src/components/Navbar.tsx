import React from 'react';
import logo from '../assets/logo.png';
import { useNavigate } from 'react-router-dom';

const Navbar: React.FC = () => {
    const navigate = useNavigate();

    return (
        <nav className="flex items-center justify-between px-8 py-6 max-w-7xl mx-auto w-full">
            {/* Logo */}
            <div className="flex items-center">
                <img src={logo} alt="StudyTrackr Logo" className="h-12 w-auto" />
            </div>

            {/* Navigation Links and Buttons */}
            <div className="flex items-center space-x-8">
                <a href="#" className="text-gray-600 hover:text-gray-900 font-medium text-base font-dm-sans">About</a>
                <a href="#" className="text-gray-600 hover:text-gray-900 font-medium text-base font-dm-sans">Contact</a>

                <div className="flex items-center space-x-4">
                    <button
                        onClick={() => navigate('/login')}
                        className="px-5 py-2 text-base font-medium font-dm-sans text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                        Log In
                    </button>
                    <button
                        onClick={() => navigate('/onboarding')}
                        className="px-5 py-2 text-base font-medium font-dm-sans text-white bg-blue-800 rounded-lg hover:bg-blue-900 transition-colors shadow-sm"
                    >
                        Sign Up
                    </button>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;

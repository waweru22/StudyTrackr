import React from 'react';
import heroImage from '../assets/hero_illustration_v2.png';
import { useNavigate } from 'react-router-dom';

const Hero: React.FC = () => {
    const navigate = useNavigate();

    return (
        <section className="max-w-7xl mx-auto px-8 py-16 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="space-y-8 max-w-lg">
                <h1 className="text-2xl md:text-3xl lg:text-6xl font-bold font-josefin text-gray-900 leading-[1.1]">
                    Study Smarter. <br />
                    By Design
                </h1>
                <p className="text-base md:text-md font-light font-dm-sans text-gray-500 leading-relaxed max-w-2xl">
                    The intelligent study planner that adapts to you. Tell us
                    how you work, and we'll handle the "when" and "where."
                </p>
                <button
                    onClick={() => navigate('/onboarding')}
                    className="px-6 py-3 bg-blue-800 text-white text-base font-medium font-dm-sans rounded-lg shadow-md hover:bg-blue-900 transition-transform transform hover:-translate-y-0.5"
                >
                    Get Started
                </button>
            </div>

            {/* Right Image */}
            <div className="relative flex justify-center lg:justify-end">
                {/* Placeholder for the illustration - utilizing the generated asset */}
                <div className="relative w-full max-w-xl">
                    {/* Decorative elements (blobs/circles) behind the image can be added here if needed to match closely, 
               but for now we depend on the image content itself or simple CSS shapes */}
                    <div className="absolute top-0 right-0 -mr-20 -mt-20 w-72 h-72 bg-blue-50 rounded-full blur-3xl opacity-50 z-0"></div>
                    <div className="absolute bottom-0 left-0 -ml-10 -mb-10 w-64 h-64 bg-indigo-50 rounded-full blur-3xl opacity-50 z-0"></div>

                    <img
                        src={heroImage}
                        alt="Study planning illustration"
                        className="relative z-10 w-full h-auto max-h-80 md:max-h-96 object-contain drop-shadow-xl"
                    />
                </div>
            </div>
        </section>
    );
};

export default Hero;

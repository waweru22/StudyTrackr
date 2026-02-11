import React from 'react';
import Sidebar from '../components/Sidebar';

const Materials: React.FC = () => {
    return (
        <div className="flex h-screen bg-white font-sans text-gray-900">
            <Sidebar />
            <div className="flex-1 ml-64 py-8 pr-8 pl-[75px]">
                <header className="mb-8">
                    <h1 className="text-2xl font-bold text-gray-900">Materials</h1>
                    <p className="text-gray-500 mt-2">Access your course resources and external libraries.</p>
                </header>

                <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm mb-8">
                    <div className="relative">
                        <input
                            type="text"
                            placeholder="Search for notes, PDFs, or recordings..."
                            className="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                        <svg className="absolute left-4 top-3.5 text-gray-400 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </div>
                </div>

                <div className="text-center py-12 text-gray-400">
                    <p>No materials uploaded yet.</p>
                </div>
            </div>
        </div>
    );
};

export default Materials;

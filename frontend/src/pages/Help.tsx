import React from 'react';
import Sidebar from '../components/Sidebar';

const Help: React.FC = () => {
    return (
        <div className="flex h-screen bg-white font-sans text-gray-900">
            <Sidebar />
            <div className="flex-1 ml-64 py-8 pr-8 pl-[75px]">
                <h1 className="text-2xl font-bold">Help & Support</h1>
                <p className="text-gray-500 mt-2">Support resources coming soon.</p>
            </div>
        </div>
    );
};

export default Help;

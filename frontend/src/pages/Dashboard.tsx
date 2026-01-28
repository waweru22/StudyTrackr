import React from 'react';
import Sidebar from '../components/Sidebar';
import quoteBg from '../assets/quote_background.png';
import mathIcon from '../assets/math_icon.png';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { ExternalLink, Flame, Clock, Brain, Award, User } from 'lucide-react';
import { useState } from 'react';
import SessionModal from '../components/SessionModal';

const focusData = [
    { name: 'Mon', focus: 50 },
    { name: 'Tue', focus: 65 },
    { name: 'Wed', focus: 30 },
    { name: 'Thur', focus: 62 },
    { name: 'Fri', focus: 75 },
    { name: 'Sat', focus: 60 },
    { name: 'Sun', focus: 35 },
    { name: 'NextMon', focus: 85 }, // Extrapolated for curve
];


import { useUser } from '../context/UserContext';
//...

const Dashboard: React.FC = () => {
    const { level, semester } = useUser();
    const [isSessionModalOpen, setIsSessionModalOpen] = useState(false);

    return (
        <div className="flex h-screen bg-white font-sans text-gray-900">
            <Sidebar />

            {/* Main Content Area */}
            <div className="flex-1 ml-64 py-8 pr-8 pl-[75px] overflow-y-auto">

                {/* Top Header */}
                <header className="flex justify-between items-start mb-8 border-b border-gray-100 pb-4">
                    <div>
                        <div className="flex space-x-8">
                            <div>
                                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Semester</p>
                                <p className="text-sm font-bold text-blue-700">{semester}</p>
                            </div>
                            <div>
                                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Level</p>
                                <p className="text-sm font-bold text-blue-700">{level}</p>
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center space-x-3">
                        <span className="text-sm font-bold text-gray-900">Waweru Ezaga</span>
                        <div className="h-10 w-10 rounded-full bg-pink-500 overflow-hidden border-2 border-white shadow-sm flex items-center justify-center">
                            {/* Placeholder Avatar */}
                            <span className="text-lg">👨🏾‍🎓</span>
                        </div>
                    </div>
                </header>

                {/* Dashboard Grid */}
                <div className="grid grid-cols-12 gap-8">

                    {/* Left Column (Main) */}
                    <div className="col-span-12 lg:col-span-8 space-y-8">

                        {/* Next Session Card */}
                        <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow relative">
                            <div className="flex justify-between items-start mb-4">
                                <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wide">Next Session</h3>
                            </div>
                            <div className="flex items-start justify-between">
                                <div className="flex items-start space-x-4">
                                    <div className="h-16 w-16 bg-blue-50 rounded-xl flex items-center justify-center p-2">
                                        <img src={mathIcon} alt="Course Icon" className="h-full w-full object-contain" />
                                    </div>
                                    <div>
                                        <h2 className="text-lg font-bold text-gray-900 mb-1">MTH202 – Mathematical Methods II</h2>
                                        <div className="flex items-center space-x-4 text-xs text-gray-500 font-medium">
                                            <span className="flex items-center"><Clock size={14} className="mr-1" /> 90 mins</span>
                                            <span className="flex items-center"><Brain size={14} className="mr-1" /> Deep Work</span>
                                            <span className="flex items-center"><User size={14} className="mr-1" /> Individual</span>
                                        </div>
                                    </div>
                                </div>
                                <button className="text-xs font-bold text-pink-600 hover:text-pink-700">View Details</button>
                            </div>

                            <div className="mt-6">
                                <button
                                    onClick={() => setIsSessionModalOpen(true)}
                                    className="bg-blue-800 hover:bg-blue-900 text-white font-semibold py-2.5 px-6 rounded-lg text-sm shadow-sm transition-all transform active:scale-95"
                                >
                                    Start Session
                                </button>
                            </div>
                        </div>

                        {/* Quote of the Day */}
                        <div className="relative rounded-2xl overflow-hidden h-36 bg-gray-900 flex items-center">
                            <img src={quoteBg} alt="Background" className="absolute inset-0 w-full h-full object-cover opacity-60" />
                            <div className="relative z-10 px-8 w-full">
                                <h3 className="text-xs font-bold text-gray-300 uppercase mb-2">Quote of the Day</h3>
                                <p className="text-white font-serif italic text-lg leading-relaxed max-w-2xl">
                                    "Success is not final, failure is not fatal: it is the courage to continue that counts."
                                </p>
                                <p className="text-right text-white text-xs font-medium mt-2">— Winston Churchill</p>
                            </div>
                        </div>

                        {/* Focus Pulse Chart */}
                        <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-sm font-bold text-gray-700">Focus Pulse</h3>
                                <ExternalLink size={16} className="text-gray-400 cursor-pointer hover:text-gray-600" />
                            </div>

                            <div className="flex justify-end mb-4">
                                <div className="flex items-center space-x-2 text-xs">
                                    <span className="px-2 py-1 bg-gray-100 rounded text-gray-600">ID</span>
                                    <div className="flex items-center">
                                        <span className="w-2 h-2 rounded-full bg-blue-800 mr-1.5"></span>
                                        <span className="text-gray-500">Focus Level</span>
                                    </div>
                                </div>
                            </div>

                            <div className="h-64 w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={focusData}>
                                        <defs>
                                            <linearGradient id="colorFocus" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#2563EB" stopOpacity={0.3} />
                                                <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <XAxis
                                            dataKey="name"
                                            axisLine={false}
                                            tickLine={false}
                                            tick={{ fontSize: 10, fill: '#9CA3AF' }}
                                            dy={10}
                                        />
                                        <YAxis hide />
                                        <Tooltip />
                                        <Area
                                            type="monotone"
                                            dataKey="focus"
                                            stroke="#4F46E5"
                                            strokeWidth={3}
                                            fillOpacity={1}
                                            fill="url(#colorFocus)"
                                        />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>

                    {/* Right Column (Sidebar) */}
                    <div className="col-span-12 lg:col-span-4 space-y-8">

                        {/* Daily Streak */}
                        <div className="bg-[#EDEFF4] rounded-2xl p-6 mr-[90px]">
                            <div className="flex justify-between items-center mb-4">
                                <h3 className="text-sm font-bold text-gray-700">Daily Streak</h3>
                                <ExternalLink size={14} className="text-gray-400" />
                            </div>
                            <div className="bg-white rounded-xl p-4 flex items-center justify-between shadow-sm border border-gray-100">
                                <div className="flex flex-col">
                                    <div className="flex items-center space-x-2 mb-1">
                                        <Flame className="text-orange-500 fill-current" size={20} />
                                        <span className="text-lg font-black text-gray-900">20 Days</span>
                                    </div>
                                    <div className="flex items-center space-x-1.5">
                                        <Award size={14} className="text-yellow-500" />
                                        <span className="text-xs font-bold text-purple-600">Bookworm</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Recent Activity */}
                        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm min-h-[400px] mr-[90px]">
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-sm font-bold text-gray-700">Recent Activity</h3>
                                <ExternalLink size={14} className="text-gray-400" />
                            </div>

                            <div className="space-y-6 relative">
                                {/* Timeline Line (simplified) */}
                                <div className="absolute left-1.5 top-2 bottom-2 w-0.5 bg-gray-100"></div>

                                {/* Item 1 */}
                                <div className="relative pl-6">
                                    <span className="absolute left-0 top-1.5 w-3.5 h-3.5 rounded-full bg-red-500 border-2 border-white shadow-sm z-10"></span>
                                    <div className="flex justify-between items-start mb-1">
                                        <h4 className="text-xs font-bold text-gray-900">Missed Session</h4>
                                        <span className="text-[10px] text-gray-400">09:34 am</span>
                                    </div>
                                    <p className="text-xs text-gray-500 leading-relaxed">
                                        You missed your Thermodynamics deep-work block. To keep your progr...
                                    </p>
                                </div>

                                {/* Item 2 */}
                                <div className="relative pl-6">
                                    <span className="absolute left-0 top-1.5 w-3.5 h-3.5 rounded-full bg-green-500 border-2 border-white shadow-sm z-10"></span>
                                    <div className="flex justify-between items-start mb-1">
                                        <h4 className="text-xs font-bold text-gray-900">Productivity Analysis</h4>
                                        <span className="text-[10px] text-gray-400">15 Dec</span>
                                    </div>
                                    <p className="text-xs text-gray-500 leading-relaxed">
                                        Your focus rate is up 15% this week. The AI has identified that your 8:00 AM 'E...
                                    </p>
                                </div>

                                {/* Item 3 */}
                                <div className="relative pl-6">
                                    <span className="absolute left-0 top-1.5 w-3.5 h-3.5 rounded-full bg-yellow-400 border-2 border-white shadow-sm z-10"></span>
                                    <div className="flex justify-between items-start mb-1">
                                        <h4 className="text-xs font-bold text-gray-900">Location Optimization</h4>
                                        <span className="text-[10px] text-gray-400">13 Dec</span>
                                    </div>
                                    <p className="text-xs text-gray-500 leading-relaxed">
                                        Performance in the Dorm has dropped by 20%. The AI has reassigned your n...
                                    </p>
                                </div>

                                {/* Item 4 */}
                                <div className="relative pl-6">
                                    <span className="absolute left-0 top-1.5 w-3.5 h-3.5 rounded-full bg-green-500 border-2 border-white shadow-sm z-10"></span>
                                    <div className="flex justify-between items-start mb-1">
                                        <h4 className="text-xs font-bold text-gray-900">Milestone Reached</h4>
                                        <span className="text-[10px] text-gray-400">13 Dec</span>
                                    </div>
                                    <p className="text-xs text-gray-500 leading-relaxed">
                                        5 days of optimized sessions complete! The AI has upgraded your profile to ...
                                    </p>
                                </div>

                            </div>
                        </div>

                    </div>

                </div>

            </div>
            <SessionModal isOpen={isSessionModalOpen} onClose={() => setIsSessionModalOpen(false)} />
        </div>
    );
};

export default Dashboard;

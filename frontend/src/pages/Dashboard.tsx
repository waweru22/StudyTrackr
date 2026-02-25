import React, { useEffect, useState } from 'react';
import Sidebar from '../components/Sidebar';
import quoteBg from '../assets/quote_background.png';
import mathIcon from '../assets/math_icon.png';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { ExternalLink, Flame, Clock, Brain, Award, User, RefreshCw } from 'lucide-react';
import SessionModal from '../components/SessionModal';
import { useUser } from '../context/UserContext';
import { api } from '../api/client';
import type { DashboardData, FeedItem } from '../types';


const Dashboard: React.FC = () => {
    const { level, semester } = useUser();
    const [isSessionModalOpen, setIsSessionModalOpen] = useState(false);
    const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
    const [loading, setLoading] = useState(true);

    // Focus Pulse state (P4)
    const [focusData, setFocusData] = useState<{ name: string; focus: number }[]>([]);
    const [focusDays, setFocusDays] = useState(7);
    const [loadingFocus, setLoadingFocus] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const data = await api.get<DashboardData>('/dashboard');
                setDashboardData(data);
            } catch (error) {
                console.error("Failed to fetch dashboard data", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    // Fetch focus pulse data (P4)
    const fetchFocusData = async (days: number) => {
        setLoadingFocus(true);
        try {
            const data = await api.get<{ name: string; focus: number }[]>(
                `/dashboard/focus-pulse?days=${days}`
            );
            setFocusData(data);
        } catch (e) {
            console.error('Failed to fetch focus pulse', e);
        } finally {
            setLoadingFocus(false);
        }
    };

    useEffect(() => {
        fetchFocusData(focusDays);
    }, [focusDays]);

    const getIconForType = (type: string) => {
        if (type === 'alert') return <span className="absolute left-0 top-1.5 w-3.5 h-3.5 rounded-full bg-red-500 border-2 border-white shadow-sm z-10"></span>;
        if (type === 'tip') return <span className="absolute left-0 top-1.5 w-3.5 h-3.5 rounded-full bg-blue-400 border-2 border-white shadow-sm z-10"></span>;
        return <span className="absolute left-0 top-1.5 w-3.5 h-3.5 rounded-full bg-green-500 border-2 border-white shadow-sm z-10"></span>;
    };

    const getTitleForType = (item: FeedItem) => {
        if (item.title) return item.title;
        if (item.type === 'alert') return 'System Alert';
        if (item.type === 'tip') return 'Study Tip';
        return 'Update';
    };

    // Build a SessionBlock-like object from next_session for the modal (P6)
    const nextSessionForModal = dashboardData?.next_session && dashboardData.next_session.id ? {
        id: dashboardData.next_session.id,
        course_code: dashboardData.next_session.course,
        course_title: dashboardData.next_session.course_title,
        start_time: dashboardData.next_session.time,
        end_time: '',
        block_type: 'Study Session',
        status: dashboardData.next_session.status as 'pending' | 'completed' | 'missed' | 'active',
        technique_name: dashboardData.next_session.technique,
        technique_details: dashboardData.next_session.technique_details,
        color_theme: 'blue',
        duration_minutes: dashboardData.next_session.duration_minutes,
    } : null;

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
                                <p className="text-sm font-bold text-blue-700">{dashboardData?.user?.level || level}</p>
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center space-x-3">
                        <span className="text-sm font-bold text-gray-900">{dashboardData?.user?.username || 'Student'}</span>
                        <div className="h-10 w-10 rounded-full bg-pink-500 overflow-hidden border-2 border-white shadow-sm flex items-center justify-center">
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
                                        <h2 className="text-lg font-bold text-gray-900 mb-1">{dashboardData?.next_session?.course !== "None" ? dashboardData?.next_session?.course : "No Upcoming Session"}</h2>
                                        {dashboardData?.next_session?.course_title && dashboardData.next_session.course !== "None" && (
                                            <p className="text-xs text-gray-400 mb-1">{dashboardData.next_session.course_title}</p>
                                        )}
                                        <div className="flex items-center space-x-4 text-xs text-gray-500 font-medium">
                                            {dashboardData?.next_session?.time && dashboardData.next_session.time !== "N/A" && (
                                                <span className="flex items-center"><Clock size={14} className="mr-1" /> {dashboardData.next_session.time}</span>
                                            )}
                                            <span className="flex items-center"><Brain size={14} className="mr-1" /> {dashboardData?.next_session?.technique || "General Study"}</span>
                                            {dashboardData?.next_session?.duration_minutes ? (
                                                <span className="flex items-center"><User size={14} className="mr-1" /> {dashboardData.next_session.duration_minutes} min</span>
                                            ) : (
                                                <span className="flex items-center"><User size={14} className="mr-1" /> Individual</span>
                                            )}
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
                                    "{dashboardData?.quote?.text || "Success is not final, failure is not fatal: it is the courage to continue that counts."}"
                                </p>
                                <p className="text-right text-white text-xs font-medium mt-2">— {dashboardData?.quote?.author || "Winston Churchill"}</p>
                            </div>
                        </div>

                        {/* Focus Pulse Chart */}
                        <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-sm font-bold text-gray-700">Focus Pulse</h3>
                                <div className="flex items-center space-x-2">
                                    {[7, 14, 30].map(d => (
                                        <button
                                            key={d}
                                            onClick={() => setFocusDays(d)}
                                            className={`text-xs px-2 py-1 rounded font-medium transition-colors ${focusDays === d
                                                ? 'bg-blue-800 text-white'
                                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                                }`}
                                        >
                                            {d}d
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div className="flex justify-end mb-4">
                                <div className="flex items-center space-x-2 text-xs">
                                    <div className="flex items-center">
                                        <span className="w-2 h-2 rounded-full bg-blue-800 mr-1.5"></span>
                                        <span className="text-gray-500">Focus Level</span>
                                    </div>
                                </div>
                            </div>
                            {focusData.length === 0 ? (
                                <div className="h-64 flex items-center justify-center text-sm text-gray-400">
                                    {loadingFocus ? 'Loading...' : 'Complete sessions to see your focus trend.'}
                                </div>
                            ) : (
                                <div className="h-64 w-full">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <AreaChart data={focusData}>
                                            <defs>
                                                <linearGradient id="colorFocus" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor="#2563EB" stopOpacity={0.3} />
                                                    <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
                                                </linearGradient>
                                            </defs>
                                            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#9CA3AF' }} dy={10} />
                                            <YAxis hide />
                                            <Tooltip />
                                            <Area type="monotone" dataKey="focus" stroke="#4F46E5" strokeWidth={3} fillOpacity={1} fill="url(#colorFocus)" />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                </div>
                            )}
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
                                        <span className="text-lg font-black text-gray-900">
                                            {dashboardData?.streak ?? 0} {dashboardData?.streak === 1 ? 'Day' : 'Days'}
                                        </span>
                                    </div>
                                    <div className="flex items-center space-x-1.5">
                                        <Award size={14} className="text-yellow-500" />
                                        <span className="text-xs font-bold text-purple-600">{dashboardData?.badge || 'Novice'}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Recent Activity */}
                        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm min-h-[400px] mr-[90px]">
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-sm font-bold text-gray-700">Recent Activity</h3>
                                <button onClick={() => window.location.reload()}><RefreshCw size={14} className="text-gray-400 hover:text-blue-600" /></button>
                            </div>

                            <div className="space-y-6 relative">
                                {/* Timeline Line */}
                                <div className="absolute left-1.5 top-2 bottom-2 w-0.5 bg-gray-100"></div>

                                {loading && <p className="text-sm text-gray-400 pl-6">Loading feed...</p>}

                                {!loading && dashboardData?.feed && dashboardData.feed.map((item, index) => (
                                    <div key={index} className="relative pl-6">
                                        {getIconForType(item.type)}
                                        <div className="flex justify-between items-start mb-1">
                                            <h4 className="text-xs font-bold text-gray-900">{getTitleForType(item)}</h4>
                                            <span className="text-[10px] text-gray-400">{new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                        </div>
                                        <p className="text-xs text-gray-500 leading-relaxed">
                                            {item.message}
                                        </p>
                                    </div>
                                ))}

                                {!loading && (!dashboardData?.feed || dashboardData.feed.length === 0) && (
                                    <div className="pl-6 text-xs text-gray-400">No recent activity</div>
                                )}
                            </div>
                        </div>

                    </div>

                </div>

            </div>
            <SessionModal isOpen={isSessionModalOpen} onClose={() => setIsSessionModalOpen(false)} session={nextSessionForModal} />
        </div>
    );
};

export default Dashboard;

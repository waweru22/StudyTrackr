import React, { useEffect, useState } from 'react';
import AdminSidebar from '../../components/AdminSidebar';
import { adminDashboard } from '../../api/adminService';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Users, BookCheck, Target, Clock, ShieldAlert, TrendingUp } from 'lucide-react';
import type { AdminDashboardData } from '../../types';

const CHART_COLORS = ['#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef'];

const AdminDashboard: React.FC = () => {
    const [data, setData] = useState<AdminDashboardData | null>(null);
    const [weeks, setWeeks] = useState(1);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        setLoading(true);
        try {
            const res = await adminDashboard.getMetrics(weeks);
            setData(res);
        } catch (e) {
            console.error('Dashboard fetch failed', e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchData(); }, [weeks]);

    const statCards = data ? [
        { label: 'Total Students', value: data.total_students, icon: Users, color: 'bg-blue-500/10 text-blue-400', border: 'border-blue-500/20' },
        { label: 'Sessions Completed', value: data.total_sessions_completed, icon: BookCheck, color: 'bg-green-500/10 text-green-400', border: 'border-green-500/20' },
        { label: 'Avg Focus Score', value: data.avg_focus_score.toFixed(1), icon: Target, color: 'bg-purple-500/10 text-purple-400', border: 'border-purple-500/20' },
        { label: 'Avg Duration (min)', value: data.avg_session_duration.toFixed(0), icon: Clock, color: 'bg-amber-500/10 text-amber-400', border: 'border-amber-500/20' },
        { label: 'Pending Verification', value: data.student_verification_pending, icon: ShieldAlert, color: 'bg-red-500/10 text-red-400', border: 'border-red-500/20' },
    ] : [];

    return (
        <div className="flex h-screen bg-slate-950 text-white">
            <AdminSidebar />

            <div className="flex-1 ml-64 py-8 pr-8 pl-10 overflow-y-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
                        <p className="text-sm text-slate-400 mt-1">System overview & key metrics</p>
                    </div>
                    <div className="flex items-center space-x-2 bg-slate-800/60 rounded-xl p-1 border border-slate-700/50">
                        {[1, 2, 4, 12].map(w => (
                            <button
                                key={w}
                                onClick={() => setWeeks(w)}
                                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${weeks === w ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                            >
                                {w === 1 ? 'This Week' : `${w}w`}
                            </button>
                        ))}
                    </div>
                </div>

                {loading ? (
                    <div className="flex items-center justify-center h-64">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
                    </div>
                ) : (
                    <>
                        {/* Stat Cards */}
                        <div className="grid grid-cols-5 gap-4 mb-8">
                            {statCards.map((card) => (
                                <div key={card.label} className={`bg-slate-800/60 backdrop-blur rounded-2xl p-5 border ${card.border} hover:border-opacity-50 transition-all`}>
                                    <div className={`inline-flex items-center justify-center w-10 h-10 rounded-xl ${card.color} mb-3`}>
                                        <card.icon size={20} />
                                    </div>
                                    <p className="text-2xl font-black text-white">{card.value}</p>
                                    <p className="text-xs text-slate-400 mt-1 font-medium">{card.label}</p>
                                </div>
                            ))}
                        </div>

                        {/* Charts Row */}
                        <div className="grid grid-cols-2 gap-6">
                            {/* Top Techniques */}
                            <div className="bg-slate-800/60 backdrop-blur rounded-2xl p-6 border border-slate-700/30">
                                <div className="flex items-center space-x-2 mb-6">
                                    <TrendingUp size={18} className="text-blue-400" />
                                    <h3 className="text-sm font-bold text-white">Top Techniques</h3>
                                </div>
                                {data?.top_techniques && data.top_techniques.length > 0 ? (
                                    <ResponsiveContainer width="100%" height={250}>
                                        <BarChart data={data.top_techniques} layout="vertical" margin={{ left: 20 }}>
                                            <XAxis type="number" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                                            <YAxis dataKey="technique_name" type="category" tick={{ fontSize: 11, fill: '#94a3b8' }} width={110} axisLine={false} tickLine={false} />
                                            <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', color: '#e2e8f0' }} />
                                            <Bar dataKey="usage_count" radius={[0, 6, 6, 0]} barSize={20}>
                                                {data.top_techniques.map((_, i) => (
                                                    <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                                                ))}
                                            </Bar>
                                        </BarChart>
                                    </ResponsiveContainer>
                                ) : (
                                    <div className="h-[250px] flex items-center justify-center text-sm text-slate-500">No technique data yet</div>
                                )}
                            </div>

                            {/* Top Courses */}
                            <div className="bg-slate-800/60 backdrop-blur rounded-2xl p-6 border border-slate-700/30">
                                <div className="flex items-center space-x-2 mb-6">
                                    <BookCheck size={18} className="text-green-400" />
                                    <h3 className="text-sm font-bold text-white">Top Courses by Sessions</h3>
                                </div>
                                {data?.top_courses && data.top_courses.length > 0 ? (
                                    <ResponsiveContainer width="100%" height={250}>
                                        <BarChart data={data.top_courses} layout="vertical" margin={{ left: 20 }}>
                                            <XAxis type="number" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                                            <YAxis dataKey="course_code" type="category" tick={{ fontSize: 11, fill: '#94a3b8' }} width={90} axisLine={false} tickLine={false} />
                                            <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', color: '#e2e8f0' }} />
                                            <Bar dataKey="session_count" radius={[0, 6, 6, 0]} fill="#22c55e" barSize={20} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                ) : (
                                    <div className="h-[250px] flex items-center justify-center text-sm text-slate-500">No course session data yet</div>
                                )}
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default AdminDashboard;

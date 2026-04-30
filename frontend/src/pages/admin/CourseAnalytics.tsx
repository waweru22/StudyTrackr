import React, { useEffect, useState } from 'react';
import AdminSidebar from '../../components/AdminSidebar';
import { adminAnalytics } from '../../api/adminService';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { BarChart3, AlertTriangle, Filter } from 'lucide-react';
import type { CourseAnalyticsItem } from '../../types';

const CourseAnalytics: React.FC = () => {
    const [data, setData] = useState<CourseAnalyticsItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [level, setLevel] = useState<number | undefined>(undefined);
    const [weeks, setWeeks] = useState<number | undefined>(undefined);

    const fetchData = async () => {
        setLoading(true);
        try {
            const res = await adminAnalytics.courses({ level, weeks });
            setData(res);
        } catch (e) { console.error(e); }
        finally { setLoading(false); }
    };

    useEffect(() => { fetchData(); }, [level, weeks]);

    const getScoreColor = (score: number) => {
        if (score >= 4) return 'text-green-400';
        if (score >= 3) return 'text-blue-400';
        if (score >= 2) return 'text-amber-400';
        return 'text-red-400';
    };

    return (
        <div className="flex h-screen bg-slate-950 text-white">
            <AdminSidebar />
            <div className="flex-1 ml-64 py-8 pr-8 pl-10 overflow-y-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-2xl font-bold">Course Performance</h1>
                        <p className="text-sm text-slate-400 mt-1">Sorted by struggling students (low performers first)</p>
                    </div>
                    <div className="flex items-center space-x-3">
                        <div className="flex items-center space-x-2">
                            <Filter size={14} className="text-slate-400" />
                            <select
                                value={level || ''}
                                onChange={(e) => setLevel(e.target.value ? Number(e.target.value) : undefined)}
                                className="px-3 py-2 rounded-xl bg-slate-800/60 border border-slate-700/50 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                            >
                                <option value="">All Levels</option>
                                {[100, 200, 300, 400].map(l => <option key={l} value={l}>Level {l}</option>)}
                            </select>
                        </div>
                        <select
                            value={weeks || ''}
                            onChange={(e) => setWeeks(e.target.value ? Number(e.target.value) : undefined)}
                            className="px-3 py-2 rounded-xl bg-slate-800/60 border border-slate-700/50 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                        >
                            <option value="">All Time</option>
                            <option value="1">Last Week</option>
                            <option value="2">Last 2 Weeks</option>
                            <option value="4">Last Month</option>
                            <option value="12">Last 3 Months</option>
                        </select>
                    </div>
                </div>

                {loading ? (
                    <div className="flex items-center justify-center h-64">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
                    </div>
                ) : (
                    <>
                        {/* Low Performers Chart */}
                        {data.length > 0 && (
                            <div className="bg-slate-800/60 backdrop-blur rounded-2xl p-6 border border-slate-700/30 mb-8">
                                <div className="flex items-center space-x-2 mb-4">
                                    <AlertTriangle size={18} className="text-amber-400" />
                                    <h3 className="text-sm font-bold">Low Performer Distribution</h3>
                                </div>
                                <ResponsiveContainer width="100%" height={220}>
                                    <BarChart data={data.slice(0, 10)}>
                                        <XAxis dataKey="course_code" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                                        <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                                        <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', color: '#e2e8f0' }} />
                                        <Bar dataKey="low_performers" radius={[6, 6, 0, 0]} barSize={32}>
                                            {data.slice(0, 10).map((entry, i) => (
                                                <Cell key={i} fill={entry.low_performers > 5 ? '#ef4444' : entry.low_performers > 2 ? '#f59e0b' : '#22c55e'} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        )}

                        {/* Table */}
                        <div className="bg-slate-800/60 backdrop-blur rounded-2xl border border-slate-700/30 overflow-hidden">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-slate-700/30">
                                        {['Code', 'Course Name', 'Total Sessions', 'Avg Success', 'Avg Focus', 'Low Performers'].map(h => (
                                            <th key={h} className="text-left px-5 py-4 text-[11px] font-bold text-slate-400 uppercase tracking-wider">{h}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.length === 0 ? (
                                        <tr><td colSpan={6} className="text-center py-12 text-slate-500">No analytics data available</td></tr>
                                    ) : data.map(c => (
                                        <tr key={c.course_id} className="border-b border-slate-700/20 hover:bg-slate-700/20 transition-colors">
                                            <td className="px-5 py-3.5 text-sm font-bold text-blue-300">{c.course_code}</td>
                                            <td className="px-5 py-3.5 text-sm text-slate-200">{c.course_name}</td>
                                            <td className="px-5 py-3.5 text-sm text-slate-300">{c.total_sessions}</td>
                                            <td className={`px-5 py-3.5 text-sm font-bold ${getScoreColor(c.avg_success_score)}`}>{c.avg_success_score}</td>
                                            <td className="px-5 py-3.5 text-sm text-slate-300">{c.avg_focus_level}</td>
                                            <td className="px-5 py-3.5">
                                                <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-bold ${c.low_performers > 5
                                                    ? 'bg-red-500/15 text-red-400'
                                                    : c.low_performers > 0
                                                        ? 'bg-amber-500/15 text-amber-400'
                                                        : 'bg-green-500/15 text-green-400'
                                                    }`}>
                                                    {c.low_performers > 0 && <AlertTriangle size={12} className="mr-1" />}
                                                    {c.low_performers}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default CourseAnalytics;

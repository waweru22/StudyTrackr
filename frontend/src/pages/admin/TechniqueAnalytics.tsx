import React, { useEffect, useState } from 'react';
import AdminSidebar from '../../components/AdminSidebar';
import { adminAnalytics } from '../../api/adminService';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { FlaskConical, TrendingUp, TrendingDown } from 'lucide-react';
import type { TechniqueItem } from '../../types';

const TechniqueAnalytics: React.FC = () => {
    const [data, setData] = useState<TechniqueItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await adminAnalytics.techniques();
                setData(res);
            } catch (e) { console.error(e); }
            finally { setLoading(false); }
        };
        fetchData();
    }, []);

    const getImpactColor = (impact: number) => {
        if (impact > 0.5) return 'text-green-400';
        if (impact > 0) return 'text-emerald-300';
        if (impact > -0.5) return 'text-amber-400';
        return 'text-red-400';
    };

    const getBarColor = (impact: number) => {
        if (impact > 0.5) return '#22c55e';
        if (impact > 0) return '#6ee7b7';
        if (impact > -0.5) return '#f59e0b';
        return '#ef4444';
    };

    return (
        <div className="flex h-screen bg-slate-950 text-white">
            <AdminSidebar />
            <div className="flex-1 ml-64 py-8 pr-8 pl-10 overflow-y-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-2xl font-bold">Technique Effectiveness</h1>
                    <p className="text-sm text-slate-400 mt-1">Study technique usage & relative performance impact</p>
                </div>

                {loading ? (
                    <div className="flex items-center justify-center h-64">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
                    </div>
                ) : data.length === 0 ? (
                    <div className="bg-slate-800/60 rounded-2xl p-12 border border-slate-700/30 text-center">
                        <FlaskConical size={48} className="text-slate-600 mx-auto mb-4" />
                        <p className="text-slate-400">No technique data available yet. Data populates as students complete sessions.</p>
                    </div>
                ) : (
                    <>
                        {/* Charts Row */}
                        <div className="grid grid-cols-2 gap-6 mb-8">
                            {/* Usage Count */}
                            <div className="bg-slate-800/60 backdrop-blur rounded-2xl p-6 border border-slate-700/30">
                                <div className="flex items-center space-x-2 mb-4">
                                    <FlaskConical size={18} className="text-blue-400" />
                                    <h3 className="text-sm font-bold">Usage Count</h3>
                                </div>
                                <ResponsiveContainer width="100%" height={280}>
                                    <BarChart data={data} layout="vertical" margin={{ left: 30 }}>
                                        <XAxis type="number" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                                        <YAxis dataKey="technique_name" type="category" tick={{ fontSize: 11, fill: '#94a3b8' }} width={120} axisLine={false} tickLine={false} />
                                        <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', color: '#e2e8f0' }} />
                                        <Bar dataKey="usage_count" radius={[0, 6, 6, 0]} fill="#3b82f6" barSize={18} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>

                            {/* Focus Impact */}
                            <div className="bg-slate-800/60 backdrop-blur rounded-2xl p-6 border border-slate-700/30">
                                <div className="flex items-center space-x-2 mb-4">
                                    <TrendingUp size={18} className="text-green-400" />
                                    <h3 className="text-sm font-bold">Focus Impact (vs. Global Avg)</h3>
                                </div>
                                <ResponsiveContainer width="100%" height={280}>
                                    <BarChart data={data} layout="vertical" margin={{ left: 30 }}>
                                        <XAxis type="number" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                                        <YAxis dataKey="technique_name" type="category" tick={{ fontSize: 11, fill: '#94a3b8' }} width={120} axisLine={false} tickLine={false} />
                                        <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', color: '#e2e8f0' }} />
                                        <Bar dataKey="avg_focus_impact" radius={[0, 6, 6, 0]} barSize={18}>
                                            {data.map((entry, i) => (
                                                <Cell key={i} fill={getBarColor(entry.avg_focus_impact)} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Table */}
                        <div className="bg-slate-800/60 backdrop-blur rounded-2xl border border-slate-700/30 overflow-hidden">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-slate-700/30">
                                        {['Technique', 'Usage Count', 'Avg Success Score', 'Focus Impact'].map(h => (
                                            <th key={h} className="text-left px-6 py-4 text-[11px] font-bold text-slate-400 uppercase tracking-wider">{h}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.map(t => (
                                        <tr key={t.technique_name} className="border-b border-slate-700/20 hover:bg-slate-700/20 transition-colors">
                                            <td className="px-6 py-4 text-sm font-semibold text-slate-200">{t.technique_name}</td>
                                            <td className="px-6 py-4 text-sm text-slate-300">
                                                <div className="flex items-center space-x-2">
                                                    <div className="w-24 bg-slate-700 rounded-full h-2">
                                                        <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${Math.min(100, (t.usage_count / Math.max(...data.map(d => d.usage_count))) * 100)}%` }}></div>
                                                    </div>
                                                    <span>{t.usage_count}</span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 text-sm font-bold text-blue-300">{t.avg_success_score}</td>
                                            <td className={`px-6 py-4 text-sm font-bold ${getImpactColor(t.avg_focus_impact)}`}>
                                                <div className="flex items-center space-x-1">
                                                    {t.avg_focus_impact >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                                                    <span>{t.avg_focus_impact > 0 ? '+' : ''}{t.avg_focus_impact}</span>
                                                </div>
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

export default TechniqueAnalytics;

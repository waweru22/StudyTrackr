import React, { useEffect, useState } from 'react';
import AdminSidebar from '../../components/AdminSidebar';
import { adminVerification } from '../../api/adminService';
import { ShieldCheck, ShieldX, UserCheck, Clock, AlertCircle } from 'lucide-react';
import type { UnverifiedStudent } from '../../types';

const Verification: React.FC = () => {
    const [students, setStudents] = useState<UnverifiedStudent[]>([]);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState<number | null>(null);

    const fetchStudents = async () => {
        setLoading(true);
        try {
            const data = await adminVerification.listUnverified();
            setStudents(data);
        } catch (e) { console.error(e); }
        finally { setLoading(false); }
    };

    useEffect(() => { fetchStudents(); }, []);

    const handleApprove = async (id: number) => {
        setActionLoading(id);
        try {
            await adminVerification.approve(id);
            setStudents(prev => prev.filter(s => s.id !== id));
        } catch (e) { console.error(e); }
        finally { setActionLoading(null); }
    };

    const handleReject = async (id: number, email: string) => {
        if (!confirm(`Reject and remove ${email}? This action cannot be undone.`)) return;
        setActionLoading(id);
        try {
            await adminVerification.reject(id);
            setStudents(prev => prev.filter(s => s.id !== id));
        } catch (e) { console.error(e); }
        finally { setActionLoading(null); }
    };

    const timeAgo = (dateStr: string | null): string => {
        if (!dateStr) return 'Unknown';
        const diffMs = Date.now() - new Date(dateStr).getTime();
        const mins = Math.floor(diffMs / 60000);
        if (mins < 60) return `${mins}m ago`;
        const hrs = Math.floor(mins / 60);
        if (hrs < 24) return `${hrs}h ago`;
        const days = Math.floor(hrs / 24);
        return `${days}d ago`;
    };

    return (
        <div className="flex h-screen bg-slate-950 text-white">
            <AdminSidebar />
            <div className="flex-1 ml-64 py-8 pr-8 pl-10 overflow-y-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-2xl font-bold">Student Verification</h1>
                        <p className="text-sm text-slate-400 mt-1">Approve or reject pending student registrations</p>
                    </div>
                    <div className="flex items-center space-x-2 bg-slate-800/60 rounded-xl px-4 py-2 border border-slate-700/50">
                        <Clock size={16} className="text-amber-400" />
                        <span className="text-sm font-semibold text-amber-300">{students.length} pending</span>
                    </div>
                </div>

                {loading ? (
                    <div className="flex items-center justify-center h-64">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
                    </div>
                ) : students.length === 0 ? (
                    <div className="bg-slate-800/60 rounded-2xl p-12 border border-slate-700/30 text-center">
                        <UserCheck size={48} className="text-green-500/40 mx-auto mb-4" />
                        <p className="text-lg font-semibold text-slate-300 mb-2">All caught up!</p>
                        <p className="text-sm text-slate-500">No pending verifications at this time.</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {students.map(student => (
                            <div key={student.id} className="bg-slate-800/60 backdrop-blur rounded-2xl border border-slate-700/30 p-6 hover:border-slate-600/50 transition-all">
                                <div className="flex justify-between items-start">
                                    <div className="flex items-start space-x-4">
                                        <div className="w-12 h-12 rounded-xl bg-slate-700 flex items-center justify-center text-lg">
                                            👨🏾‍🎓
                                        </div>
                                        <div>
                                            <h3 className="text-base font-bold text-white">{student.username}</h3>
                                            <p className="text-sm text-slate-400 mt-0.5">{student.email}</p>
                                            <div className="flex items-center space-x-4 mt-2">
                                                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-bold bg-blue-500/15 text-blue-300">
                                                    Level {student.level}
                                                </span>
                                                <span className="text-[11px] text-slate-500 flex items-center">
                                                    <Clock size={12} className="mr-1" />
                                                    Registered {timeAgo(student.registration_date)}
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex items-center space-x-3">
                                        <button
                                            onClick={() => handleReject(student.id, student.email)}
                                            disabled={actionLoading === student.id}
                                            className="flex items-center space-x-2 px-4 py-2.5 rounded-xl border border-red-500/30 text-red-400 hover:bg-red-500/10 text-sm font-semibold transition-all disabled:opacity-50"
                                        >
                                            <ShieldX size={16} />
                                            <span>Reject</span>
                                        </button>
                                        <button
                                            onClick={() => handleApprove(student.id)}
                                            disabled={actionLoading === student.id}
                                            className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-green-600 hover:bg-green-500 text-white text-sm font-bold shadow-lg shadow-green-500/20 transition-all disabled:opacity-50 active:scale-[0.98]"
                                        >
                                            <ShieldCheck size={16} />
                                            <span>{actionLoading === student.id ? 'Processing...' : 'Approve'}</span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Verification;

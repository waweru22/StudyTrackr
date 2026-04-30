import React, { useEffect, useState } from 'react';
import AdminSidebar from '../../components/AdminSidebar';
import { adminBroadcast } from '../../api/adminService';
import { Megaphone, Send, Clock, Users, ChevronDown } from 'lucide-react';
import type { BroadcastRecord } from '../../types';

const AdminBroadcast: React.FC = () => {
    const [title, setTitle] = useState('');
    const [message, setMessage] = useState('');
    const [targetLevel, setTargetLevel] = useState<number | null>(null);
    const [sending, setSending] = useState(false);
    const [successMsg, setSuccessMsg] = useState('');
    const [error, setError] = useState('');
    const [history, setHistory] = useState<BroadcastRecord[]>([]);
    const [loadingHistory, setLoadingHistory] = useState(true);

    const fetchHistory = async () => {
        setLoadingHistory(true);
        try {
            const data = await adminBroadcast.history();
            setHistory(data);
        } catch (e) { console.error(e); }
        finally { setLoadingHistory(false); }
    };

    useEffect(() => { fetchHistory(); }, []);

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccessMsg('');

        if (!title.trim() || !message.trim()) {
            setError('Title and message are required');
            return;
        }

        setSending(true);
        try {
            const res = await adminBroadcast.send({
                title: title.trim(),
                message: message.trim(),
                target_level: targetLevel,
            });
            setSuccessMsg(`${res.message}`);
            setTitle('');
            setMessage('');
            setTargetLevel(null);
            fetchHistory();
        } catch (err: any) {
            setError(err.message || 'Broadcast failed');
        } finally {
            setSending(false);
        }
    };

    const formatDate = (dateStr: string | null) => {
        if (!dateStr) return '—';
        return new Date(dateStr).toLocaleDateString('en-NG', {
            day: 'numeric', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    };

    return (
        <div className="flex h-screen bg-slate-950 text-white">
            <AdminSidebar />
            <div className="flex-1 ml-64 py-8 pr-8 pl-10 overflow-y-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-2xl font-bold">Broadcast Notifications</h1>
                    <p className="text-sm text-slate-400 mt-1">Send announcements to student cohorts</p>
                </div>

                <div className="grid grid-cols-12 gap-8">
                    {/* Compose Form */}
                    <div className="col-span-5">
                        <div className="bg-slate-800/60 backdrop-blur rounded-2xl border border-slate-700/30 p-6 sticky top-8">
                            <div className="flex items-center space-x-2 mb-6">
                                <div className="w-10 h-10 bg-blue-500/15 rounded-xl flex items-center justify-center">
                                    <Megaphone size={20} className="text-blue-400" />
                                </div>
                                <h2 className="text-base font-bold">Compose Broadcast</h2>
                            </div>

                            <form onSubmit={handleSend} className="space-y-5">
                                <div>
                                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Title</label>
                                    <input
                                        type="text"
                                        value={title}
                                        onChange={(e) => setTitle(e.target.value)}
                                        placeholder="e.g. Exam Preparation Week"
                                        className="w-full px-4 py-3 rounded-xl bg-slate-700/50 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-sm"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Message</label>
                                    <textarea
                                        value={message}
                                        onChange={(e) => setMessage(e.target.value)}
                                        rows={5}
                                        placeholder="Write your announcement here..."
                                        className="w-full px-4 py-3 rounded-xl bg-slate-700/50 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-sm resize-none"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Target Audience</label>
                                    <div className="relative">
                                        <select
                                            value={targetLevel ?? ''}
                                            onChange={(e) => setTargetLevel(e.target.value ? Number(e.target.value) : null)}
                                            className="w-full px-4 py-3 rounded-xl bg-slate-700/50 border border-slate-600/50 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-sm appearance-none"
                                        >
                                            <option value="">All Students</option>
                                            <option value="100">Level 100 Only</option>
                                            <option value="200">Level 200 Only</option>
                                            <option value="300">Level 300 Only</option>
                                            <option value="400">Level 400 Only</option>
                                        </select>
                                        <ChevronDown size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                                    </div>
                                </div>

                                {error && (
                                    <div className="text-red-300 text-sm bg-red-500/10 border border-red-500/20 p-3 rounded-xl">{error}</div>
                                )}
                                {successMsg && (
                                    <div className="text-green-300 text-sm bg-green-500/10 border border-green-500/20 p-3 rounded-xl">{successMsg}</div>
                                )}

                                <button
                                    type="submit"
                                    disabled={sending}
                                    className="w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3.5 rounded-xl text-sm shadow-lg shadow-blue-500/25 transition-all disabled:opacity-50 active:scale-[0.98]"
                                >
                                    <Send size={16} />
                                    <span>{sending ? 'Sending...' : 'Send Broadcast'}</span>
                                </button>
                            </form>
                        </div>
                    </div>

                    {/* History */}
                    <div className="col-span-7">
                        <div className="flex items-center space-x-2 mb-4">
                            <Clock size={16} className="text-slate-400" />
                            <h2 className="text-sm font-bold text-slate-300">Broadcast History</h2>
                        </div>

                        {loadingHistory ? (
                            <div className="flex items-center justify-center h-32">
                                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-400"></div>
                            </div>
                        ) : history.length === 0 ? (
                            <div className="bg-slate-800/60 rounded-2xl border border-slate-700/30 p-10 text-center">
                                <Megaphone size={36} className="text-slate-600 mx-auto mb-3" />
                                <p className="text-sm text-slate-500">No broadcasts sent yet</p>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {history.map(b => (
                                    <div key={b.id} className="bg-slate-800/60 backdrop-blur rounded-2xl border border-slate-700/30 p-5 hover:border-slate-600/50 transition-all">
                                        <div className="flex justify-between items-start mb-2">
                                            <h3 className="text-sm font-bold text-white">{b.title}</h3>
                                            <span className="text-[11px] text-slate-500 flex-shrink-0 ml-4">{formatDate(b.created_at)}</span>
                                        </div>
                                        <p className="text-sm text-slate-300 mb-3 line-clamp-2">{b.message}</p>
                                        <div className="flex items-center space-x-4 text-[11px] text-slate-500">
                                            <span className="flex items-center">
                                                <Users size={12} className="mr-1" />
                                                {b.target_level ? `Level ${b.target_level}` : 'All Students'}
                                            </span>
                                            <span>by {b.created_by}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminBroadcast;

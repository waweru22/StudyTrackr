import React, { useEffect, useState } from 'react';
import Sidebar from '../components/Sidebar';
import { api } from '../api/client';
import { CheckCircle } from 'lucide-react';

interface Notification {
    id: number;
    title: string;
    message: string;
    type: 'system' | 'encouragement' | 'alert' | 'milestone';
    is_read: boolean;
    created_at: string;
}

const typeConfig: Record<string, { border: string; bg: string; icon: string }> = {
    encouragement: { border: 'border-l-teal-400', bg: 'bg-teal-50/50', icon: '🔥' },
    alert: { border: 'border-l-red-400', bg: 'bg-red-50/50', icon: '⚠️' },
    milestone: { border: 'border-l-yellow-400', bg: 'bg-yellow-50/50', icon: '🏆' },
    system: { border: 'border-l-gray-300', bg: 'bg-gray-50/50', icon: 'ℹ️' },
};

function timeAgo(dateStr: string): string {
    const now = new Date();
    // Backend sends UTC timestamps without 'Z' suffix — append it so JS parses as UTC
    const normalized = dateStr.endsWith('Z') ? dateStr : dateStr + 'Z';
    const date = new Date(normalized);
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    // Today's notifications: show precise time
    const isToday = date.toLocaleDateString() === now.toLocaleDateString();
    if (isToday) {
        if (diffMins < 1) return 'Just now';
        return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    }

    // Yesterday
    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);
    if (date.toLocaleDateString() === yesterday.toLocaleDateString()) {
        return 'Yesterday, ' + date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    }

    // Older
    const diffDays = Math.floor(diffMs / 86400000);
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
}

const NotificationsPage: React.FC = () => {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get<Notification[]>('/notifications/')
            .then(setNotifications)
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    const markAsRead = (id: number) => {
        setNotifications(prev =>
            prev.map(n => n.id === id ? { ...n, is_read: true } : n)
        );
        api.put('/notifications/' + id + '/read', {}).catch(console.error);
    };

    const markAllAsRead = () => {
        setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
        api.put('/notifications/read-all', {}).catch(console.error);
    };

    const unread = notifications.filter(n => !n.is_read);
    const read = notifications.filter(n => n.is_read);
    const hasUnread = unread.length > 0;

    const renderCard = (n: Notification) => {
        const cfg = typeConfig[n.type] || typeConfig.system;
        return (
            <div
                key={n.id}
                onClick={() => !n.is_read && markAsRead(n.id)}
                className={`border-l-4 ${cfg.border} ${!n.is_read ? cfg.bg : 'bg-white'} rounded-xl px-5 py-4 shadow-sm transition-all duration-200 ${!n.is_read ? 'cursor-pointer hover:shadow-md' : ''}`}
            >
                <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start space-x-3">
                        <span className="text-lg mt-0.5">{cfg.icon}</span>
                        <div>
                            <p className="text-sm font-semibold text-gray-900">{n.title}</p>
                            <p className="text-sm text-gray-500 mt-0.5">{n.message}</p>
                        </div>
                    </div>
                    <span className="text-[11px] text-gray-400 whitespace-nowrap shrink-0">{timeAgo(n.created_at)}</span>
                </div>
            </div>
        );
    };

    if (loading) return (
        <div className="flex h-screen bg-white font-sans text-gray-900">
            <Sidebar />
            <div className="flex-1 ml-64 flex items-center justify-center">
                <p className="text-gray-400">Loading notifications...</p>
            </div>
        </div>
    );

    return (
        <div className="flex h-screen bg-white font-sans text-gray-900">
            <Sidebar />
            <div className="flex-1 ml-64 py-8 pr-8 pl-[75px] overflow-y-auto">
                <div className="flex items-center justify-between mb-8">
                    <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
                    {hasUnread && (
                        <button
                            onClick={markAllAsRead}
                            className="text-sm font-bold text-blue-600 bg-blue-50 px-4 py-2 rounded-lg hover:bg-blue-100 transition-colors"
                        >
                            Mark all as read
                        </button>
                    )}
                </div>

                {notifications.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-96 text-gray-400">
                        <CheckCircle size={48} className="mb-4 text-green-400" />
                        <p className="text-lg font-semibold">You're all caught up</p>
                    </div>
                ) : (
                    <>
                        {hasUnread && (
                            <>
                                <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">
                                    Unread ({unread.length})
                                </h2>
                                <div className="space-y-3 mb-8">
                                    {unread.map(renderCard)}
                                </div>
                            </>
                        )}
                        {read.length > 0 && (
                            <>
                                <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">
                                    {hasUnread ? 'Earlier' : 'All Notifications'}
                                </h2>
                                <div className="space-y-3">
                                    {read.map(renderCard)}
                                </div>
                            </>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};

export default NotificationsPage;

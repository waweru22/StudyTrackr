import React, { useEffect, useState } from 'react';
import Sidebar from '../components/Sidebar';
import { api } from '../api/client';
import { Settings as SettingsIcon, Bell, User, Brain } from 'lucide-react';
import { useUser } from '../context/UserContext';

interface NotificationTrigger {
    id: number;
    trigger_name: string;
    description: string;
    is_active: boolean;
}

const Settings: React.FC = () => {
    const { user, refreshUser } = useUser();
    const [loading, setLoading] = useState(true);
    
    // Account Settings
    const [username, setUsername] = useState('');
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    
    // Study Preferences
    const [peakTime, setPeakTime] = useState('');
    const [focusThreshold, setFocusThreshold] = useState<number>(60);
    const [environmentPref, setEnvironmentPref] = useState('');
    const [learningStyle, setLearningStyle] = useState('');

    // Notification Triggers
    const [triggers, setTriggers] = useState<NotificationTrigger[]>([]);
    
    // Toasts
    const [toastMessage, setToastMessage] = useState<{ text: string, type: 'success' | 'error' } | null>(null);

    useEffect(() => {
        if (user) {
            setUsername(user.username || '');
            setPeakTime(user.peak_time || '');
            setFocusThreshold(user.focus_threshold || 60);
            setEnvironmentPref(user.environment_pref || user.preferred_environment_v2 || 'Silent');
            setLearningStyle(user.learning_style || '');
        }

        api.get<NotificationTrigger[]>('/notifications/triggers')
            .then(res => setTriggers(res))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, [user]);

    const showToast = (text: string, type: 'success' | 'error') => {
        setToastMessage({ text, type });
        setTimeout(() => setToastMessage(null), 3000);
    };

    const handleUpdateProfile = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.put('/users/profile', { username });
            showToast('Profile updated successfully', 'success');
            refreshUser();
        } catch (error: any) {
            showToast(error.message || 'Failed to update profile', 'error');
        }
    };

    const handleUpdatePassword = async (e: React.FormEvent) => {
        e.preventDefault();
        if (newPassword !== confirmPassword) {
            showToast('New passwords do not match', 'error');
            return;
        }
        try {
            await api.put('/auth/change-password', {
                current_password: currentPassword,
                new_password: newPassword
            });
            showToast('Password updated successfully', 'success');
            setCurrentPassword('');
            setNewPassword('');
            setConfirmPassword('');
        } catch (error: any) {
            showToast(error.message || 'Failed to update password', 'error');
        }
    };

    const handleUpdatePreferences = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.put('/users/update-preferences', {
                peak_time: peakTime,
                focus_threshold: focusThreshold,
                environment_pref: environmentPref,
                preferred_environment_v2: environmentPref,
                learning_style: learningStyle
            });
            showToast('Preferences saved', 'success');
            refreshUser();
        } catch (error: any) {
            showToast(error.message || 'Failed to save preferences', 'error');
        }
    };

    const handleToggleTrigger = async (triggerName: string, currentStatus: boolean) => {
        const newStatus = !currentStatus;
        setTriggers(triggers.map(t => t.trigger_name === triggerName ? { ...t, is_active: newStatus } : t));
        try {
            await api.patch(`/notifications/triggers/${triggerName}`, { is_active: newStatus });
        } catch (error: any) {
            showToast('Failed to update notification setting', 'error');
            setTriggers(triggers.map(t => t.trigger_name === triggerName ? { ...t, is_active: currentStatus } : t));
        }
    };

    if (loading) return (
        <div className="flex h-screen bg-white font-sans text-gray-900">
            <Sidebar />
            <div className="flex-1 md:py-8 py-16 pr-4 md:pr-8 pl-4 md:pl-[75px] flex justify-center items-center w-full">
                <p className="text-gray-400">Loading settings...</p>
            </div>
        </div>
    );

    return (
        <div className="flex h-screen bg-white font-sans text-gray-900">
            <Sidebar />
            <div className="flex-1 md:py-8 py-16 pr-4 md:pr-8 pl-4 md:pl-[75px] overflow-y-auto w-full">
                {toastMessage && (
                    <div className={`fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg font-semibold text-sm transition-all ${toastMessage.type === 'success' ? 'bg-green-100 text-green-800 border border-green-200' : 'bg-red-100 text-red-800 border border-red-200'}`}>
                        {toastMessage.text}
                    </div>
                )}
                <div className="max-w-2xl mx-auto">
                    <header className="mb-10 flex items-center space-x-3">
                        <SettingsIcon className="text-gray-900" size={28} />
                        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
                    </header>
                    <section className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm mb-8">
                        <div className="flex items-center space-x-3 mb-6">
                            <User className="text-blue-500" size={22} />
                            <h2 className="text-lg font-semibold text-gray-900">Account Settings</h2>
                        </div>
                        <form onSubmit={handleUpdateProfile} className="space-y-4 mb-8">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-1">Display Name</label>
                                    <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" required />
                                </div>
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-1">Email (Read-only)</label>
                                    <input type="email" value={user?.email || ''} readOnly className="w-full border border-gray-200 bg-gray-50 rounded-lg px-4 py-2 text-sm text-gray-500 cursor-not-allowed" />
                                </div>
                            </div>
                            <div className="flex justify-end">
                                <button type="submit" className="bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-2 px-6 rounded-lg text-sm transition-colors">Update Profile</button>
                            </div>
                        </form>
                        <div className="border-t border-gray-100 pt-6">
                            <h3 className="text-sm font-semibold text-gray-900 mb-4">Change Password</h3>
                            <form onSubmit={handleUpdatePassword} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Current Password</label>
                                    <input type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" required />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
                                        <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" required />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
                                        <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" required />
                                    </div>
                                </div>
                                <div className="flex justify-end mt-4">
                                    <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg text-sm shadow-sm transition-colors">Update Password</button>
                                </div>
                            </form>
                        </div>
                    </section>
                    <section className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm mb-8">
                        <div className="flex items-center space-x-3 mb-6">
                            <Brain className="text-indigo-500" size={22} />
                            <h2 className="text-lg font-semibold text-gray-900">Study Preferences</h2>
                        </div>
                        <form onSubmit={handleUpdatePreferences} className="space-y-5">
                            <div className="grid grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-1">Peak study time</label>
                                    <select value={peakTime} onChange={(e) => setPeakTime(e.target.value)} className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white">
                                        <option value="Morning">Morning</option>
                                        <option value="Afternoon">Afternoon</option>
                                        <option value="Evening">Evening</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-1">Focus session length</label>
                                    <select value={focusThreshold} onChange={(e) => setFocusThreshold(Number(e.target.value))} className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white">
                                        <option value={25}>Short 25min</option>
                                        <option value={45}>Medium 45min</option>
                                        <option value={90}>Long 90min</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-1">Preferred study environment</label>
                                    <select value={environmentPref} onChange={(e) => setEnvironmentPref(e.target.value)} className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white">
                                        <option value="Silent">Silent</option>
                                        <option value="Background noise">Background noise</option>
                                        <option value="Music">Music</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-1">Learning style</label>
                                    <select value={learningStyle} onChange={(e) => setLearningStyle(e.target.value)} className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white">
                                        <option value="Visual">Visual</option>
                                        <option value="Auditory">Auditory</option>
                                        <option value="Reading-Writing">Reading-Writing</option>
                                        <option value="Kinaesthetic">Kinaesthetic</option>
                                    </select>
                                </div>
                            </div>
                            <div className="flex flex-col items-end border-t border-gray-100 pt-5 mt-2">
                                <button type="submit" className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-6 rounded-lg text-sm shadow-sm transition-colors mb-2">Save Preferences</button>
                                <p className="text-xs text-gray-400">Changes will be applied when your schedule next adapts.</p>
                            </div>
                        </form>
                    </section>
                    <section className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm mb-12">
                        <div className="flex items-center space-x-3 mb-6">
                            <Bell className="text-pink-500" size={22} />
                            <h2 className="text-lg font-semibold text-gray-900">Notification Preferences</h2>
                        </div>
                        <div className="space-y-4">
                            {triggers.length === 0 ? (
                                <p className="text-sm text-gray-400">No notification triggers found.</p>
                            ) : (
                                triggers.map((trigger) => (
                                    <div key={trigger.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-100">
                                        <div className="pr-4">
                                            <h3 className="text-sm font-semibold text-gray-900">{trigger.trigger_name.replace(/_/g, ' ')}</h3>
                                            <p className="text-xs text-gray-500 mt-1">{trigger.description}</p>
                                        </div>
                                        <label className="relative inline-flex items-center cursor-pointer flex-shrink-0">
                                            <input type="checkbox" className="sr-only peer" checked={trigger.is_active} onChange={() => handleToggleTrigger(trigger.trigger_name, trigger.is_active)} />
                                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                                        </label>
                                    </div>
                                ))
                            )}
                        </div>
                    </section>
                </div>
            </div>
        </div>
    );
};

export default Settings;

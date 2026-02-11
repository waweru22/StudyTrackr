import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import { api } from '../api/client';
import { Save, AlertCircle, CheckCircle } from 'lucide-react';

const Settings: React.FC = () => {
    const [username, setUsername] = useState('');
    const [phone, setPhone] = useState('');
    const [level, setLevel] = useState(100);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    useEffect(() => {
        // Fetch current values
        api.get<any>('/users/profile').then(data => {
            setUsername(data.username);
            setPhone(data.phone_number || '');
            setLevel(data.level);
        });
    }, []);

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);

        try {
            await api.put('/users/profile', {
                username,
                phone_number: phone,
                level: Number(level)
            });
            setMessage({ type: 'success', text: 'Profile updated successfully!' });
        } catch (err) {
            setMessage({ type: 'error', text: 'Failed to update profile.' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex h-screen bg-white font-sans text-gray-900">
            <Sidebar />

            <div className="flex-1 ml-64 py-8 pr-8 pl-[75px] overflow-y-auto">
                <header className="mb-10 border-b border-gray-100 pb-4">
                    <h1 className="text-2xl font-bold text-gray-900">Account Settings</h1>
                </header>

                <div className="max-w-2xl">
                    {message && (
                        <div className={`p-4 rounded-lg mb-6 flex items-center ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                            {message.type === 'success' ? <CheckCircle size={20} className="mr-2" /> : <AlertCircle size={20} className="mr-2" />}
                            {message.text}
                        </div>
                    )}

                    <form onSubmit={handleSave} className="space-y-6 bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">

                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2">Username</label>
                            <input
                                type="text"
                                value={username}
                                onChange={e => setUsername(e.target.value)}
                                className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2">Phone Number</label>
                            <input
                                type="tel"
                                value={phone}
                                onChange={e => setPhone(e.target.value)}
                                placeholder="+234..."
                                className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2">Academic Level</label>
                            <select
                                value={level}
                                onChange={e => setLevel(Number(e.target.value))}
                                className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all bg-white"
                            >
                                <option value={100}>100 Level</option>
                                <option value={200}>200 Level</option>
                                <option value={300}>300 Level</option>
                                <option value={400}>400 Level</option>
                                <option value={500}>500 Level</option>
                            </select>
                        </div>

                        <div className="pt-4">
                            <button
                                type="submit"
                                disabled={loading}
                                className="flex items-center justify-center space-x-2 bg-blue-800 hover:bg-blue-900 text-white font-bold py-3 px-8 rounded-xl shadow-lg shadow-blue-200 transition-all w-full sm:w-auto"
                            >
                                {loading ? <span>Saving...</span> : (
                                    <>
                                        <Save size={18} />
                                        <span>Save Changes</span>
                                    </>
                                )}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Settings;

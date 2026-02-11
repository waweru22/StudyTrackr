import React, { useEffect, useState } from 'react';
import Sidebar from '../components/Sidebar';
import { api } from '../api/client';
import { Award, Flame, Zap, Edit2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface UserProfile {
    id: number;
    username: string;
    email: string;
    level: number;
    phone_number: string;
    xp_points: number;
    badge: string;
    streak_count: number;
    base_template: string;
}

const Profile: React.FC = () => {
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        api.get<UserProfile>('/users/profile')
            .then(data => setProfile(data))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div>Loading...</div>;
    if (!profile) return <div>User not found.</div>;

    return (
        <div className="flex h-screen bg-white font-sans text-gray-900">
            <Sidebar />

            <div className="flex-1 ml-64 py-8 pr-8 pl-[75px] overflow-y-auto">
                <header className="mb-10">
                    <h1 className="text-2xl font-bold text-gray-900">Student Profile</h1>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {/* Main Card */}
                    <div className="col-span-2 bg-white rounded-3xl border border-gray-100 shadow-xl overflow-hidden">
                        <div className="h-32 bg-gradient-to-r from-blue-600 to-indigo-700 relative"></div>
                        <div className="px-8 pb-8">
                            <div className="relative -mt-16 mb-6 flex justify-between items-end">
                                <div className="h-32 w-32 rounded-full border-4 border-white bg-gray-200 flex items-center justify-center text-4xl shadow-md">
                                    👨🏾‍🎓
                                </div>
                                <button
                                    onClick={() => navigate('/settings')}
                                    className="flex items-center space-x-2 text-sm font-bold text-blue-600 bg-blue-50 px-4 py-2 rounded-lg hover:bg-blue-100 transition-colors"
                                >
                                    <Edit2 size={16} />
                                    <span>Edit Profile</span>
                                </button>
                            </div>

                            <h2 className="text-2xl font-bold text-gray-900">{profile.username}</h2>
                            <p className="text-gray-500 font-medium">{profile.email}</p>

                            <div className="mt-8 grid grid-cols-2 gap-6">
                                <div className="p-4 bg-gray-50 rounded-xl">
                                    <p className="text-xs text-gray-400 uppercase font-bold tracking-wider">Level</p>
                                    <p className="text-xl font-bold text-gray-900">{profile.level} Lvl</p>
                                </div>
                                <div className="p-4 bg-gray-50 rounded-xl">
                                    <p className="text-xs text-gray-400 uppercase font-bold tracking-wider">Phone</p>
                                    <p className="text-xl font-bold text-gray-900">{profile.phone_number || '-'}</p>
                                </div>
                                <div className="p-4 bg-gray-50 rounded-xl col-span-2">
                                    <p className="text-xs text-gray-400 uppercase font-bold tracking-wider">Cognitive Profile</p>
                                    <p className="text-lg font-bold text-indigo-600 mt-1">{profile.base_template}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Gamification Stats */}
                    <div className="space-y-6">
                        <div className="bg-gradient-to-br from-yellow-400 to-orange-500 rounded-2xl p-6 text-white shadow-lg">
                            <div className="flex items-center space-x-3 mb-2">
                                <Award className="text-white fill-current opacity-80" size={24} />
                                <h3 className="text-lg font-bold opacity-90">Current Badge</h3>
                            </div>
                            <p className="text-3xl font-black">{profile.badge}</p>
                        </div>

                        <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-sm font-bold text-gray-500">Total XP</h3>
                                <Zap className="text-yellow-500 fill-current" size={20} />
                            </div>
                            <p className="text-4xl font-black text-gray-900">{profile.xp_points} XP</p>
                        </div>

                        <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-sm font-bold text-gray-500">Day Streak</h3>
                                <Flame className="text-orange-500 fill-current" size={20} />
                            </div>
                            <p className="text-4xl font-black text-gray-900">{profile.streak_count} Days</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Profile;

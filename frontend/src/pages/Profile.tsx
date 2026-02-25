import React, { useEffect, useState } from 'react';
import Sidebar from '../components/Sidebar';
import { api } from '../api/client';
import { Award, Flame, Zap, Edit2, Brain, BarChart3, BookOpen, ChevronDown, ChevronUp } from 'lucide-react';
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
    peak_time: string;
    focus_threshold: number;
    learning_style: string;
    daily_cognitive_budget: number;
}

interface WeeklySummary {
    total: number;
    completed: number;
    missed: number;
    remaining: number;
}

interface UserCourse {
    id: number;
    code: string;
    name: string;
    credits: number;
    weight: number;
}

// ─── Value Transformers ────────────────────────────────────────
const blueprintLabel = (raw: string | null): string => {
    if (!raw) return 'Not set';
    const key = raw.toLowerCase();
    if (key.includes('sprinter') || key.includes('pomodoro')) return 'Balanced Sprinter (Pomodoro)';
    if (key.includes('deep') || key.includes('deepwork')) return 'Deep-Work Specialist';
    if (key.includes('recall') || key.includes('recaller')) return 'Active Recaller';
    return raw;
};

const peakLabel = (raw: string | null): string => {
    const map: Record<string, string> = {
        morning: '9 am – 12 pm',
        afternoon: '1 pm – 5 pm',
        evening: '8 pm – 12 am',
        night: '1 am – 4 am',
        early_morning: '4 am – 8 am',
    };
    return map[(raw || '').toLowerCase()] || raw || 'Not set';
};

const focusLabel = (val: number | null): string => {
    if (!val) return 'Not set';
    if (val <= 30) return 'Short (< 30 min)';
    if (val <= 75) return 'Balanced (45 min – 1 hr)';
    return 'Intense (90 min – 2 hrs)';
};

const styleLabel = (raw: string | null): string => {
    if (!raw || raw === 'Unknown') return 'Not set';
    const map: Record<string, string> = {
        visual: 'Visual',
        aural: 'Aural',
        read_write: 'Read / Write',
        kinesthetic: 'Kinesthetic',
    };
    return map[raw.toLowerCase()] || raw.charAt(0).toUpperCase() + raw.slice(1);
};

const Profile: React.FC = () => {
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [weekly, setWeekly] = useState<WeeklySummary | null>(null);
    const [courses, setCourses] = useState<UserCourse[]>([]);
    const [loading, setLoading] = useState(true);
    const [showAllCourses, setShowAllCourses] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        Promise.all([
            api.get<UserProfile>('/users/profile'),
            api.get<WeeklySummary>('/schedule/weekly-summary'),
            api.get<UserCourse[]>('/users/courses'),
        ])
            .then(([profileData, weeklyData, coursesData]) => {
                setProfile(profileData);
                setWeekly(weeklyData);
                setCourses(coursesData);
            })
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="flex h-screen items-center justify-center text-gray-400">Loading...</div>;
    if (!profile) return <div className="flex h-screen items-center justify-center text-gray-400">User not found.</div>;

    const visibleCourses = showAllCourses ? courses : courses.slice(0, 6);

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
                                    <p className="text-lg font-bold text-indigo-600 mt-1">{blueprintLabel(profile.base_template)}</p>
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

                {/* ─── Section 1: Cognitive Profile ─────────────────────── */}
                <div className="mt-8 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                    <div className="flex items-center space-x-3 mb-6">
                        <Brain className="text-indigo-500" size={22} />
                        <h3 className="text-lg font-bold text-gray-900">Cognitive Profile</h3>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
                        <div className="p-4 bg-indigo-50 rounded-xl">
                            <p className="text-xs text-indigo-400 uppercase font-bold tracking-wider mb-1">Blueprint</p>
                            <p className="text-sm font-bold text-indigo-700">{blueprintLabel(profile.base_template)}</p>
                        </div>
                        <div className="p-4 bg-amber-50 rounded-xl">
                            <p className="text-xs text-amber-400 uppercase font-bold tracking-wider mb-1">Peak Focus Time</p>
                            <p className="text-sm font-bold text-amber-700">{peakLabel(profile.peak_time)}</p>
                        </div>
                        <div className="p-4 bg-emerald-50 rounded-xl">
                            <p className="text-xs text-emerald-400 uppercase font-bold tracking-wider mb-1">Focus Duration</p>
                            <p className="text-sm font-bold text-emerald-700">{focusLabel(profile.focus_threshold)}</p>
                        </div>
                        <div className="p-4 bg-sky-50 rounded-xl">
                            <p className="text-xs text-sky-400 uppercase font-bold tracking-wider mb-1">Learning Style</p>
                            <p className="text-sm font-bold text-sky-700">{styleLabel(profile.learning_style)}</p>
                        </div>
                    </div>
                </div>

                {/* ─── Section 2: Weekly Performance Snapshot ────────────── */}
                {weekly && (
                    <div className="mt-8 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                        <div className="flex items-center space-x-3 mb-6">
                            <BarChart3 className="text-blue-500" size={22} />
                            <h3 className="text-lg font-bold text-gray-900">This Week</h3>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
                            <div className="p-4 bg-emerald-50 rounded-xl text-center">
                                <p className="text-3xl font-black text-emerald-600">{weekly.completed}</p>
                                <p className="text-xs text-emerald-500 uppercase font-bold tracking-wider mt-1">Completed</p>
                            </div>
                            <div className="p-4 bg-red-50 rounded-xl text-center">
                                <p className="text-3xl font-black text-red-500">{weekly.missed}</p>
                                <p className="text-xs text-red-400 uppercase font-bold tracking-wider mt-1">Missed</p>
                            </div>
                            <div className="p-4 bg-blue-50 rounded-xl text-center">
                                <p className="text-3xl font-black text-blue-600">{weekly.remaining}</p>
                                <p className="text-xs text-blue-400 uppercase font-bold tracking-wider mt-1">Remaining</p>
                            </div>
                            <div className="p-4 bg-gray-50 rounded-xl text-center">
                                <p className="text-3xl font-black text-gray-600">{weekly.total}</p>
                                <p className="text-xs text-gray-400 uppercase font-bold tracking-wider mt-1">Total Scheduled</p>
                            </div>
                        </div>
                    </div>
                )}

                {/* ─── Section 3: Enrolled Courses ──────────────────────── */}
                {courses.length > 0 && (
                    <div className="mt-8 mb-12 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                        <div className="flex items-center space-x-3 mb-6">
                            <BookOpen className="text-violet-500" size={22} />
                            <h3 className="text-lg font-bold text-gray-900">Enrolled Courses</h3>
                            <span className="text-xs font-bold text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">{courses.length}</span>
                        </div>
                        <div className="flex flex-wrap gap-3">
                            {visibleCourses.map(c => (
                                <div key={c.id} className="flex items-center space-x-2 bg-gray-50 border border-gray-100 rounded-xl px-4 py-3">
                                    <span className="text-sm font-bold text-gray-900">{c.code}</span>
                                    <span className="text-sm text-gray-500">{c.name}</span>
                                    <span className="text-xs text-gray-300 font-medium">{c.credits} CR</span>
                                </div>
                            ))}
                        </div>
                        {courses.length > 6 && (
                            <button
                                onClick={() => setShowAllCourses(!showAllCourses)}
                                className="mt-4 flex items-center space-x-1 text-sm font-bold text-blue-600 hover:text-blue-800 transition-colors"
                            >
                                {showAllCourses ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                <span>{showAllCourses ? 'Show less' : `Show all ${courses.length} courses`}</span>
                            </button>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Profile;

import React from 'react';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import { useNavigate } from 'react-router-dom';
import {
    Brain, Calendar, BookOpen, Timer, BarChart3, Sparkles,
    Zap, Clock, Target, ArrowRight, CheckCircle, Lightbulb
} from 'lucide-react';

/* ────────────────────────────────────────────────────────── */
/*  Data — all sourced from actual app functionality          */
/* ────────────────────────────────────────────────────────── */

const features = [
    {
        icon: Brain,
        title: 'AI-Powered Scheduling',
        description: 'Our adaptive engine builds your weekly study plan around your class timetable, peak focus hours, and cognitive profile — then refines it each week based on your actual performance.',
        accent: 'bg-indigo-50 text-indigo-600',
    },
    {
        icon: Timer,
        title: 'Technique-Aware Timer',
        description: 'Start sessions with built-in Pomodoro, Active Recall, or Deep Work timers. The system tracks work/break phases, reps, and logs distractions automatically.',
        accent: 'bg-red-50 text-red-600',
    },
    {
        icon: BookOpen,
        title: 'Curated Study Materials',
        description: 'Course-specific resources are sourced and tagged by learning style (Visual, Aural, Read/Write, Kinesthetic) so you always have the right materials at hand.',
        accent: 'bg-emerald-50 text-emerald-600',
    },
    {
        icon: BarChart3,
        title: 'Progress & Insights',
        description: 'Track your focus trends, session completion rates, and environment preferences. The system learns what works for you and surfaces behavioural insights on your profile.',
        accent: 'bg-amber-50 text-amber-600',
    },
    {
        icon: Sparkles,
        title: 'Adaptive Techniques',
        description: 'Struggling with a course? The engine automatically swaps study techniques — moving you from Pomodoro to Deep Work or Active Recall based on your session scores.',
        accent: 'bg-purple-50 text-purple-600',
    },
    {
        icon: Calendar,
        title: 'Smart Timetable Integration',
        description: 'Upload your class timetable once. StudyTrackr schedules study blocks around your lectures, labs, and free periods — never double-booking you.',
        accent: 'bg-sky-50 text-sky-600',
    },
];

const steps = [
    {
        number: '01',
        title: 'Create Your Profile',
        description: 'Sign up with your university email, select your courses, and choose a study blueprint — Balanced Sprinter, Deep-Work Specialist, or Active Recaller.',
        icon: Target,
    },
    {
        number: '02',
        title: 'Upload Your Timetable',
        description: 'Add your class schedule. Our AI analyses your free periods, preferred study times, and cognitive budget to generate a personalised weekly plan.',
        icon: Calendar,
    },
    {
        number: '03',
        title: 'Start Studying',
        description: 'Launch technique-specific timers, log your sessions, and watch the system adapt. Every completed session earns XP, builds your streak, and makes your next schedule smarter.',
        icon: Zap,
    },
];

const techniques = [
    {
        name: 'Pomodoro',
        cycle: '25 min work / 5 min break',
        best: 'Staying focused, fighting procrastination',
        rating: 3,
    },
    {
        name: 'Active Recall',
        cycle: '30 min retrieval / 5 min review',
        best: 'Exams, memorisation-heavy courses',
        rating: 3,
    },
    {
        name: 'Deep Work',
        cycle: '90 min uninterrupted focus',
        best: 'Complex problem-solving, coding',
        rating: 3,
    },
];

/* ────────────────────────────────────────────────────────── */
/*  Component                                                 */
/* ────────────────────────────────────────────────────────── */

const LandingPage: React.FC = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-white font-sans text-gray-900 selection:bg-blue-100 selection:text-blue-900">
            <Navbar />

            <main>
                {/* ── Hero ───────────────────────────────── */}
                <Hero />

                {/* ── Features ───────────────────────────── */}
                <section className="bg-gray-50 py-16">
                    <div className="max-w-7xl mx-auto px-8">
                        <div className="text-center mb-12">
                            <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-600 mb-3">What You Get</p>
                            <h2 className="text-2xl md:text-3xl font-bold font-josefin text-gray-900">
                                Everything You Need to Study Effectively
                            </h2>
                            <p className="mt-3 text-sm text-gray-500 max-w-2xl mx-auto font-dm-sans">
                                Built specifically for university students who want to stop guessing and start optimising how they learn.
                            </p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {features.map((f) => (
                                <div
                                    key={f.title}
                                    className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow group"
                                >
                                    <div className={`w-10 h-10 rounded-xl ${f.accent} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                                        <f.icon size={20} />
                                    </div>
                                    <h3 className="text-base font-bold text-gray-900 mb-2 font-dm-sans">{f.title}</h3>
                                    <p className="text-sm text-gray-500 leading-relaxed font-dm-sans">{f.description}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* ── How It Works ────────────────────────── */}
                <section className="py-16">
                    <div className="max-w-7xl mx-auto px-8">
                        <div className="text-center mb-12">
                            <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-600 mb-3">How It Works</p>
                            <h2 className="text-2xl md:text-3xl font-bold font-josefin text-gray-900">
                                From Sign-Up to Smarter Studying in 3 Steps
                            </h2>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                            {steps.map((s, i) => (
                                <div key={s.number} className="relative">
                                    {/* Connector line (hidden on last card) */}
                                    {i < steps.length - 1 && (
                                        <div className="hidden md:block absolute top-10 left-[calc(50%+2rem)] right-0 h-px bg-gray-200 -mr-4" />
                                    )}

                                    <div className="text-center space-y-4">
                                        <div className="w-16 h-16 rounded-2xl bg-blue-800 text-white flex items-center justify-center mx-auto shadow-lg shadow-blue-200">
                                            <s.icon size={28} />
                                        </div>
                                        <span className="inline-block text-xs font-bold text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
                                            Step {s.number}
                                        </span>
                                        <h3 className="text-lg font-bold text-gray-900 font-dm-sans">{s.title}</h3>
                                        <p className="text-sm text-gray-500 leading-relaxed font-dm-sans max-w-xs mx-auto">
                                            {s.description}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* ── Study Techniques ────────────────────── */}
                <section className="bg-gray-900 py-16">
                    <div className="max-w-7xl mx-auto px-8">
                        <div className="text-center mb-12">
                            <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-400 mb-3">Built-In Techniques</p>
                            <h2 className="text-2xl md:text-3xl font-bold font-josefin text-white">
                                Proven Methods, Zero Guesswork
                            </h2>
                            <p className="mt-3 text-sm text-gray-400 max-w-2xl mx-auto font-dm-sans">
                                Each technique is backed by cognitive science research. The system assigns and rotates them based on your performance.
                            </p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {techniques.map((t) => (
                                <div
                                    key={t.name}
                                    className="bg-gray-800/60 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50 hover:border-blue-500/30 transition-colors"
                                >
                                    <div className="flex items-center justify-between mb-4">
                                        <h3 className="text-lg font-bold text-white font-dm-sans">{t.name}</h3>
                                        <div className="flex space-x-1">
                                            {[1, 2, 3].map((n) => (
                                                <div
                                                    key={n}
                                                    className={`w-2 h-2 rounded-full ${n <= t.rating ? 'bg-green-400' : 'bg-gray-600'}`}
                                                />
                                            ))}
                                        </div>
                                    </div>
                                    <div className="space-y-3">
                                        <div className="flex items-center space-x-2">
                                            <Clock size={14} className="text-gray-500" />
                                            <span className="text-sm text-gray-300 font-dm-sans">{t.cycle}</span>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            <CheckCircle size={14} className="text-gray-500" />
                                            <span className="text-sm text-gray-300 font-dm-sans">{t.best}</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* ── Adaptation Explainer ────────────────── */}
                <section className="py-16">
                    <div className="max-w-7xl mx-auto px-8">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
                            <div className="space-y-6">
                                <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-600">Adaptive Intelligence</p>
                                <h2 className="text-2xl md:text-3xl font-bold font-josefin text-gray-900 leading-tight">
                                    Your Schedule Gets Smarter Every Week
                                </h2>
                                <p className="text-sm text-gray-500 leading-relaxed font-dm-sans">
                                    After each week, the adaptation engine analyses your completed sessions, focus scores, and environment preferences. It then regenerates your schedule — reallocating time to struggling courses and swapping techniques that aren't working.
                                </p>
                                <ul className="space-y-3">
                                    {[
                                        'Technique swaps based on session efficacy scores',
                                        'Time reallocation to courses with low completion rates',
                                        'Environment-aware scheduling (library vs. home vs. lab)',
                                        'Burnout detection from declining focus trends',
                                    ].map((item) => (
                                        <li key={item} className="flex items-start space-x-3">
                                            <CheckCircle size={16} className="text-green-500 mt-0.5 shrink-0" />
                                            <span className="text-sm text-gray-600 font-dm-sans">{item}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div className="bg-gray-50 rounded-2xl p-6 border border-gray-100">
                                <div className="space-y-4">
                                    <div className="flex items-center space-x-3 mb-6">
                                        <Lightbulb size={20} className="text-amber-500" />
                                        <span className="text-sm font-bold text-gray-700 font-dm-sans">Example Adaptation</span>
                                    </div>

                                    {/* Simulated adaptation card */}
                                    <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-xs font-bold text-gray-400 uppercase tracking-wide">CSC 301 — Databases</span>
                                            <span className="text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full font-medium">Technique Swap</span>
                                        </div>
                                        <div className="flex items-center space-x-2 text-sm font-dm-sans">
                                            <span className="text-gray-400 line-through">Pomodoro</span>
                                            <ArrowRight size={14} className="text-blue-500" />
                                            <span className="text-blue-700 font-semibold">Deep Work</span>
                                        </div>
                                        <p className="text-xs text-gray-400 mt-2 font-dm-sans">
                                            3 consecutive sessions scored below 3/5 — switching to extended focus blocks
                                        </p>
                                    </div>

                                    <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-xs font-bold text-gray-400 uppercase tracking-wide">CSC 205 — Algorithms</span>
                                            <span className="text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded-full font-medium">Preserved</span>
                                        </div>
                                        <p className="text-xs text-gray-400 mt-1 font-dm-sans">
                                            Active Recall maintained — 4.2 avg efficacy, 100% completion rate
                                        </p>
                                    </div>

                                    <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-xs font-bold text-gray-400 uppercase tracking-wide">CSC 311 — Networks</span>
                                            <span className="text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full font-medium">Time Added</span>
                                        </div>
                                        <div className="flex items-center space-x-2 text-sm font-dm-sans">
                                            <span className="text-gray-400">3 blocks/week</span>
                                            <ArrowRight size={14} className="text-blue-500" />
                                            <span className="text-blue-700 font-semibold">5 blocks/week</span>
                                        </div>
                                        <p className="text-xs text-gray-400 mt-2 font-dm-sans">
                                            Missed 2 sessions last week — increasing study frequency
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* ── Built For ───────────────────────────── */}
                <section className="bg-blue-800 py-16">
                    <div className="max-w-7xl mx-auto px-8">
                        <div className="text-center mb-10">
                            <h2 className="text-2xl md:text-3xl font-bold font-josefin text-white">
                                Built for Nile University Students
                            </h2>
                            <p className="mt-3 text-sm text-blue-200 max-w-2xl mx-auto font-dm-sans">
                                Pre-loaded with your department's course catalogue. Select your level and semester — your courses are already waiting.
                            </p>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-3 gap-6 text-center">
                            {[
                                { label: 'Supported Levels', value: '100 – 400' },
                                { label: 'Study Techniques', value: '8 Built-in' },
                                { label: 'Adaptation Cycles', value: 'Weekly' },
                            ].map((stat) => (
                                <div key={stat.label} className="bg-blue-900/40 backdrop-blur-sm rounded-xl p-4 border border-blue-700/30">
                                    <p className="text-xl font-black text-white font-dm-sans">{stat.value}</p>
                                    <p className="text-xs text-blue-300 mt-1 font-dm-sans">{stat.label}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* ── Final CTA ───────────────────────────── */}
                <section className="py-16">
                    <div className="max-w-3xl mx-auto px-8 text-center">
                        <h2 className="text-2xl md:text-3xl font-bold font-josefin text-gray-900 mb-4">
                            Ready to Study Smarter?
                        </h2>
                        <p className="text-sm text-gray-500 font-dm-sans mb-8 max-w-xl mx-auto">
                            Set up your personalised study plan in under 5 minutes. Tell us your courses, your preferences, and let the system handle the rest.
                        </p>
                        <div className="flex items-center justify-center space-x-4">
                            <button
                                onClick={() => navigate('/onboarding')}
                                className="px-6 py-3 bg-blue-800 text-white text-sm font-semibold font-dm-sans rounded-lg shadow-md hover:bg-blue-900 transition-transform transform hover:-translate-y-0.5"
                            >
                                Get Started — It's Free
                            </button>
                            <button
                                onClick={() => navigate('/login')}
                                className="px-6 py-3 text-sm font-semibold font-dm-sans text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                            >
                                I Already Have an Account
                            </button>
                        </div>
                    </div>
                </section>
            </main>

            {/* ── Footer ──────────────────────────────── */}
            <footer className="border-t border-gray-100 py-8">
                <div className="max-w-7xl mx-auto px-8 flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
                    <p className="text-xs text-gray-400 font-dm-sans">
                        © {new Date().getFullYear()} StudyTrackr. A Software Engineering capstone project — Nile University, Abuja.
                    </p>
                    <div className="flex items-center space-x-6">
                        <a href="#" className="text-xs text-gray-400 hover:text-gray-600 font-dm-sans transition-colors">About</a>
                        <a href="#" className="text-xs text-gray-400 hover:text-gray-600 font-dm-sans transition-colors">Contact</a>
                        <a href="#" className="text-xs text-gray-400 hover:text-gray-600 font-dm-sans transition-colors">Privacy</a>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;

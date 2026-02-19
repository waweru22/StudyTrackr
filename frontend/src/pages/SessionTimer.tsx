import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { api } from '../api/client';

interface TimerState {
    courseName: string;
    courseCode: string;
    durationMinutes: number;
    technique: string;
    goal: string;
    sessionId?: number; // Added sessionId
}

const SessionTimer: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();

    // Default State if accessed directly (fallback)
    const initialState: TimerState = location.state || {
        courseName: 'General Study',
        courseCode: 'STUDY',
        durationMinutes: 90,
        technique: 'Standard',
        goal: 'Focus on material',
        sessionId: undefined
    };

    const isPomodoro = initialState.technique.toLowerCase().includes('pomodoro');

    // Timer State
    const [timeLeft, setTimeLeft] = useState(isPomodoro ? 25 * 60 : initialState.durationMinutes * 60);
    const [totalTimeElapsed, setTotalTimeElapsed] = useState(0);
    const [isActive, setIsActive] = useState(true);

    // Pomodoro Specific State
    const [pomoPhase, setPomoPhase] = useState<'Focus' | 'Break'>('Focus');
    const [cycleCount, setCycleCount] = useState(1);

    // Alerts
    const [showEndSessionAlert, setShowEndSessionAlert] = useState(false);
    const [showDistractionAlert, setShowDistractionAlert] = useState(false);
    const [showUnfinishedAlert, setShowUnfinishedAlert] = useState(false);
    const [distractionTimeLeft, setDistractionTimeLeft] = useState(300); // 5 mins

    // Prevent back navigation
    useEffect(() => {
        const handlePopState = () => {
            if (timeLeft > 0) {
                window.history.pushState(null, '', window.location.pathname);
                setIsActive(false);
                setShowUnfinishedAlert(true);
            }
        };
        window.history.pushState(null, '', window.location.pathname);
        window.addEventListener('popstate', handlePopState);
        return () => window.removeEventListener('popstate', handlePopState);
    }, [timeLeft]);

    // Timer Tick
    useEffect(() => {
        let interval: ReturnType<typeof setInterval> | null = null;
        if (isActive && timeLeft > 0) {
            interval = setInterval(() => {
                setTimeLeft((prev) => prev - 1);
                setTotalTimeElapsed((prev) => prev + 1);
            }, 1000);
        } else if (timeLeft === 0 && isActive) {
            // Timer finished
            if (isPomodoro) {
                handlePomodoroSwitch();
            } else {
                setIsActive(false); // End of standard session
            }
        }
        return () => { if (interval) clearInterval(interval); };
    }, [isActive, timeLeft, isPomodoro]);

    // Distraction Timer
    useEffect(() => {
        let interval: ReturnType<typeof setInterval> | null = null;
        if (showDistractionAlert && distractionTimeLeft > 0) {
            interval = setInterval(() => setDistractionTimeLeft((prev) => prev - 1), 1000);
        }
        return () => { if (interval) clearInterval(interval); };
    }, [showDistractionAlert, distractionTimeLeft]);

    const handlePomodoroSwitch = () => {
        if (pomoPhase === 'Focus') {
            // Switch to Break
            setPomoPhase('Break');
            setTimeLeft(5 * 60);
            // Play notification sound?
        } else {
            // Switch back to Focus
            setPomoPhase('Focus');
            setCycleCount(prev => prev + 1);
            setTimeLeft(25 * 60);
        }
    };

    const formatTime = (seconds: number) => {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;
        return {
            h: h.toString().padStart(2, '0'),
            m: m.toString().padStart(2, '0'),
            s: s.toString().padStart(2, '0'),
        };
    };

    const time = formatTime(timeLeft);
    const distractionTime = formatTime(distractionTimeLeft);

    const handleResume = () => {
        setShowEndSessionAlert(false);
        setShowDistractionAlert(false);
        setShowUnfinishedAlert(false);
        setIsActive(true);
    };

    const handleEndAnyway = async () => {
        if (initialState.sessionId) {
            try {
                await api.post(`/schedule/${initialState.sessionId}/complete`, {});
            } catch (error) {
                console.error("Failed to mark session as complete", error);
            }
        }
        navigate('/dashboard');
    };

    return (
        <div className={`min-h-screen flex flex-col items-center justify-center font-sans transition-colors duration-500 ${pomoPhase === 'Break' ? 'bg-green-50' : 'bg-white'}`}>

            {/* Header / Info */}
            <div className="w-full max-w-4xl px-8 flex justify-between items-start mb-16 text-center">
                <div className="flex-1 text-center">
                    <p className="text-sm font-semibold text-blue-800 mb-1">Currently Studying</p>
                    <p className="text-lg text-gray-700 font-medium">
                        <span className="font-bold text-gray-900">{initialState.courseCode}</span> – {initialState.courseName}
                    </p>
                </div>
                <div className="flex-1 text-center">
                    <p className="text-sm font-semibold text-blue-800 mb-1">Technique</p>
                    <p className="text-lg text-gray-500 font-light flex items-center justify-center gap-2">
                        {initialState.technique}
                        {isPomodoro && <span className="text-xs font-bold bg-gray-100 px-2 py-1 rounded-full text-gray-600">Cycle {cycleCount}</span>}
                    </p>
                </div>
                <div className="flex-1 text-center">
                    <p className="text-sm font-semibold text-blue-800 mb-1">Goal</p>
                    <p className="text-lg text-gray-500 font-light">{initialState.goal}</p>
                </div>
            </div>

            {/* Phase Indicator (Pomodoro) */}
            {isPomodoro && (
                <div className="mb-8">
                    <span className={`px-4 py-2 rounded-full text-sm font-bold tracking-widest uppercase ${pomoPhase === 'Focus' ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600'}`}>
                        {pomoPhase} Mode
                    </span>
                </div>
            )}

            {/* Timer Display */}
            <div className="flex items-center space-x-8 text-gray-900 mb-24">
                {/* Only show hours if > 0 */}
                {parseInt(time.h) > 0 && (
                    <>
                        <div className="flex flex-col items-center">
                            <span className="text-[128px] font-light font-josefin leading-none">{time.h}</span>
                            <span className="text-gray-400 text-lg mt-2 font-dm-sans">Hours</span>
                        </div>
                        <span className="text-[128px] font-light font-josefin text-gray-900 relative -top-8">:</span>
                    </>
                )}

                <div className="flex flex-col items-center">
                    <span className="text-[128px] font-light font-josefin leading-none">{time.m}</span>
                    <span className="text-gray-400 text-lg mt-2 font-dm-sans">Minutes</span>
                </div>
                <span className="text-[128px] font-light font-josefin text-gray-900 relative -top-8">:</span>
                <div className="flex flex-col items-center">
                    <span className="text-[128px] font-light font-josefin leading-none">{time.s}</span>
                    <span className="text-gray-400 text-lg mt-2 font-dm-sans">Seconds</span>
                </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-8">
                <button
                    onClick={() => { setIsActive(false); setShowDistractionAlert(true); setDistractionTimeLeft(300); }}
                    className="bg-blue-800 hover:bg-blue-900 text-white font-semibold py-4 px-10 rounded-lg text-base shadow-sm transition-transform active:scale-95"
                >
                    Log Distraction
                </button>
                <button
                    onClick={() => { setIsActive(false); setShowEndSessionAlert(true); }}
                    className="bg-red-700 hover:bg-red-800 text-white font-semibold py-4 px-10 rounded-lg text-base shadow-sm transition-transform active:scale-95"
                >
                    End Session
                </button>
            </div>

            {/* --- ALERTS & OVERLAYS --- */}

            {/* Completion View (Shown when timer is 00:00:00 AND not pomodoro loop) */}
            {timeLeft === 0 && !isPomodoro && (
                <div className="absolute inset-0 bg-white flex flex-col items-center justify-center z-20">
                    <div className="text-center mb-12">
                        <p className="text-pink-600 font-bold mb-2">Session Complete!</p>
                        <h2 className="text-gray-600 text-sm max-w-lg mx-auto leading-relaxed">
                            You stayed in the zone. Great work!
                        </h2>
                    </div>
                    <button
                        onClick={handleEndAnyway}
                        className="bg-green-600 hover:bg-green-700 text-white font-semibold py-4 px-10 rounded-lg text-base shadow-sm transition-transform active:scale-95"
                    >
                        Return to Dashboard
                    </button>
                </div>
            )}

            {/* Distraction Alert */}
            {showDistractionAlert && (
                <div className="absolute inset-0 z-50 bg-gray-900/20 backdrop-blur-sm flex items-center justify-center">
                    <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full animate-in fade-in zoom-in-95 duration-200 text-center">
                        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Resuming in <span className="text-pink-600 font-bold">{distractionTime.m}:{distractionTime.s}</span> </p>
                        <h3 className="text-lg font-bold text-gray-900 mb-3">Distraction Logged</h3>
                        <p className="text-gray-600 text-sm mb-6">Write it down, get it out of your head, and get back to work.</p>
                        <button onClick={handleResume} className="bg-blue-800 text-white font-semibold py-2.5 px-8 rounded-lg text-sm">Resume</button>
                    </div>
                </div>
            )}

            {/* End Session Alert */}
            {showEndSessionAlert && (
                <div className="absolute inset-0 z-50 bg-gray-900/20 backdrop-blur-sm flex items-center justify-center">
                    <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full">
                        <h3 className="text-lg font-bold text-gray-900 mb-3">End Session?</h3>
                        <p className="text-gray-600 text-sm mb-6">You still have time left. Ending now will log this as incomplete.</p>
                        <div className="flex justify-end space-x-3">
                            <button onClick={handleResume} className="bg-gray-100 text-gray-800 py-2 px-6 rounded-lg text-sm">Resume</button>
                            <button onClick={handleEndAnyway} className="bg-red-700 text-white py-2 px-6 rounded-lg text-sm">End Anyway</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Unfinished Alert (Back Button) */}
            {showUnfinishedAlert && (
                <div className="absolute inset-0 z-50 bg-gray-900/20 backdrop-blur-sm flex items-center justify-center">
                    <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full">
                        <h3 className="text-lg font-bold text-gray-900 mb-3">Leave Session?</h3>
                        <p className="text-gray-600 text-sm mb-6">Timer is running. Progress will be lost.</p>
                        <div className="flex justify-end space-x-3">
                            <button onClick={handleResume} className="bg-gray-100 text-gray-800 py-2 px-6 rounded-lg text-sm">Stay</button>
                            <button onClick={handleEndAnyway} className="bg-red-700 text-white py-2 px-6 rounded-lg text-sm">Leave</button>
                        </div>
                    </div>
                </div>
            )}

        </div>
    );
};

export default SessionTimer;

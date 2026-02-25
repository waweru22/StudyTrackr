import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { api } from '../api/client';

interface TimerState {
    courseName: string;
    courseCode: string;
    durationMinutes: number;
    technique: string;
    goal: string;
    sessionId?: number;
    totalSets?: number;
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
    const isActiveRecall = initialState.technique.toLowerCase().includes('recall');
    const midpoint = Math.floor(initialState.durationMinutes * 60 / 2);
    const totalSets = initialState.totalSets || 2;

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
    const [distractionTimeLeft, setDistractionTimeLeft] = useState(300);

    // Active Recall midpoint prompt (P6)
    const [showRecallPrompt, setShowRecallPrompt] = useState(false);

    // Post-session rating (P4)
    const [showRating, setShowRating] = useState(false);
    const [rating, setRating] = useState({
        success_score: 0,
        mood_after: 0,
        would_repeat: null as boolean | null
    });

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
            if (isPomodoro) {
                handlePomodoroSwitch();
            } else {
                setIsActive(false);
            }
        }
        return () => { if (interval) clearInterval(interval); };
    }, [isActive, timeLeft, isPomodoro]);

    // Active Recall midpoint check (P6)
    useEffect(() => {
        if (isActiveRecall && totalTimeElapsed === midpoint && !showRecallPrompt && midpoint > 0) {
            setIsActive(false);
            setShowRecallPrompt(true);
        }
    }, [totalTimeElapsed, isActiveRecall, midpoint, showRecallPrompt]);

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
            setPomoPhase('Break');
            setTimeLeft(5 * 60);
        } else {
            const nextCycle = cycleCount + 1;
            if (nextCycle > totalSets) {
                // All sets complete — end session
                setIsActive(false);
                setShowRating(true);
            } else {
                setPomoPhase('Focus');
                setCycleCount(nextCycle);
                setTimeLeft(25 * 60);
            }
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

    const handleEndAnyway = () => {
        setIsActive(false);
        setShowEndSessionAlert(false);
        setShowUnfinishedAlert(false);
        setShowRating(true);
    };

    const handleSubmitRating = async () => {
        const elapsedMinutes = Math.floor(totalTimeElapsed / 60);
        const scheduledMinutes = initialState.durationMinutes;

        if (initialState.sessionId) {
            try {
                await api.post(`/schedule/${initialState.sessionId}/complete`, {});
            } catch (error) {
                console.error("Failed to mark session as complete", error);
            }
        }

        try {
            await api.post('/sessions/end', {
                session_id: initialState.sessionId,
                success_score: rating.success_score,
                mood_after: rating.mood_after,
                would_repeat: rating.would_repeat,
                actual_duration_minutes: elapsedMinutes,
                completed_on_time: elapsedMinutes >= scheduledMinutes * 0.9,
                total_distraction_seconds: 0
            });
        } catch (error) {
            console.error('Failed to submit session rating', error);
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
                        {isPomodoro && <span className="text-xs font-bold bg-gray-100 px-2 py-1 rounded-full text-gray-600">Set {cycleCount} of {totalSets}</span>}
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

            {/* Completion View (timer hit 00:00:00 AND not pomodoro loop) */}
            {timeLeft === 0 && !isPomodoro && !showRating && (
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
                        Rate & Finish
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

            {/* Active Recall Midpoint Prompt (P6) */}
            {showRecallPrompt && (
                <div className="absolute inset-0 z-50 bg-gray-900/20 backdrop-blur-sm flex items-center justify-center">
                    <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full text-center">
                        <h3 className="text-lg font-bold text-gray-900 mb-3">⏸️ Halfway Point</h3>
                        <p className="text-gray-600 text-sm mb-6">
                            Close your notes. Write down everything you remember from this topic without looking.
                            This is the most important part of Active Recall.
                        </p>
                        <button
                            onClick={() => { setShowRecallPrompt(false); setIsActive(true); }}
                            className="bg-blue-800 text-white font-semibold py-2.5 px-8 rounded-lg text-sm"
                        >
                            I've done it — Continue
                        </button>
                    </div>
                </div>
            )}

            {/* Post-Session Rating Screen (P4) */}
            {showRating && (
                <div className="absolute inset-0 z-50 bg-white flex items-center justify-center">
                    <div className="max-w-lg w-full px-8">
                        <h2 className="text-2xl font-bold text-gray-900 mb-1 text-center">Quick Session Review</h2>
                        <p className="text-gray-400 text-sm mb-8 text-center">Takes under 15 seconds</p>

                        {/* Effectiveness (1-5) */}
                        <div className="mb-6">
                            <label className="block text-sm font-semibold text-gray-700 mb-3">How effective was this session?</label>
                            <div className="flex gap-2 justify-center">
                                {[1, 2, 3, 4, 5].map((n) => (
                                    <button
                                        key={n}
                                        onClick={() => setRating({ ...rating, success_score: n })}
                                        className={`w-12 h-12 rounded-lg text-lg font-bold transition-all ${rating.success_score === n
                                            ? 'bg-blue-800 text-white shadow-md scale-110'
                                            : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                                            }`}
                                    >
                                        {n}
                                    </button>
                                ))}
                            </div>
                            <div className="flex justify-between text-xs text-gray-400 mt-1 px-1">
                                <span>Not at all</span>
                                <span>Very effective</span>
                            </div>
                        </div>

                        {/* Mood After */}
                        <div className="mb-6">
                            <label className="block text-sm font-semibold text-gray-700 mb-3">How do you feel?</label>
                            <div className="flex gap-3 justify-center">
                                {[
                                    { value: 1, label: '😩 Drained' },
                                    { value: 2, label: '😐 Neutral' },
                                    { value: 3, label: '⚡ Energized' }
                                ].map((opt) => (
                                    <button
                                        key={opt.value}
                                        onClick={() => setRating({ ...rating, mood_after: opt.value })}
                                        className={`flex-1 py-3 rounded-lg text-sm font-semibold transition-all ${rating.mood_after === opt.value
                                            ? 'bg-blue-800 text-white shadow-md'
                                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                            }`}
                                    >
                                        {opt.label}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Would Repeat */}
                        <div className="mb-8">
                            <label className="block text-sm font-semibold text-gray-700 mb-3">
                                Would you use <span className="text-blue-800">{initialState.technique}</span> again?
                            </label>
                            <div className="flex gap-3 justify-center">
                                {[
                                    { value: true, label: '👍 Yes' },
                                    { value: false, label: '👎 No' }
                                ].map((opt) => (
                                    <button
                                        key={String(opt.value)}
                                        onClick={() => setRating({ ...rating, would_repeat: opt.value })}
                                        className={`flex-1 py-3 rounded-lg text-sm font-semibold transition-all ${rating.would_repeat === opt.value
                                            ? 'bg-blue-800 text-white shadow-md'
                                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                            }`}
                                    >
                                        {opt.label}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Submit */}
                        <button
                            onClick={handleSubmitRating}
                            disabled={!rating.success_score || !rating.mood_after || rating.would_repeat === null}
                            className={`w-full py-3 rounded-lg text-base font-semibold transition-all ${rating.success_score && rating.mood_after && rating.would_repeat !== null
                                ? 'bg-green-600 hover:bg-green-700 text-white shadow-sm'
                                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                                }`}
                        >
                            Submit & Return to Dashboard
                        </button>
                    </div>
                </div>
            )}

        </div>
    );
};

export default SessionTimer;

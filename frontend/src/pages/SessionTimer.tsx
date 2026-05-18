import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { api } from '../api/client';

interface TimerState {
    courseName: string;
    courseCode: string;
    durationMinutes: number;
    technique: string;
    goal: string;
    blockId?: number;
    studySessionId?: number;
    courseId?: number;
    totalSets?: number;
}

type Phase = 'idle' | 'work' | 'break' | 'complete';

interface TechniqueConfig {
    workMinutes: number;
    breakMinutes: number;
    defaultReps: number;
    label: string;
    workLabel: (rep: number, total: number) => string;
    breakLabel: (rep: number) => string;
}

function getTechniqueConfig(technique: string, durationMinutes: number): TechniqueConfig {
    const t = technique.toLowerCase();
    const dur = durationMinutes > 0 ? durationMinutes : 90; // guard against missing value

    if (t.includes('pomodoro')) {
        // 25 min work + 5 min break = 30 min per rep
        const reps = Math.max(1, Math.round(dur / 30));
        return {
            workMinutes: 25, breakMinutes: 5, defaultReps: reps,
            label: 'Pomodoro',
            workLabel: (r, t) => `Focus Time — Rep ${r} of ${t}`,
            breakLabel: (r) => `Break Time — Rep ${r} complete`,
        };
    }
    if (t.includes('recall')) {
        // 45 min work + 10 min break = 55 min per rep
        const WORK = 45, BREAK = 10, CYCLE = 55;
        if (dur < WORK) {
            // Block too short for a full work phase — use full duration as single work block
            return {
                workMinutes: dur, breakMinutes: 0, defaultReps: 1,
                label: 'Active Recall',
                workLabel: (r, t) => `Recall Session ${r} of ${t}`,
                breakLabel: () => 'Review Break',
            };
        } else if (dur < CYCLE) {
            // Room for one work phase but not a full break
            return {
                workMinutes: WORK, breakMinutes: dur - WORK, defaultReps: 1,
                label: 'Active Recall',
                workLabel: (r, t) => `Recall Session ${r} of ${t}`,
                breakLabel: () => 'Review Break',
            };
        } else {
            const reps = Math.max(1, Math.round(dur / CYCLE));
            return {
                workMinutes: WORK, breakMinutes: BREAK, defaultReps: reps,
                label: 'Active Recall',
                workLabel: (r, t) => `Recall Session ${r} of ${t}`,
                breakLabel: () => 'Review Break',
            };
        }
    }
    if (t.includes('deep')) {
        // Deep Work: full block duration as single uninterrupted session
        return {
            workMinutes: dur, breakMinutes: 0, defaultReps: 1,
            label: 'Deep Work',
            workLabel: () => 'Deep Work Session',
            breakLabel: () => '',
        };
    }
    // Standard / unknown — single block, full duration
    return {
        workMinutes: dur, breakMinutes: 0, defaultReps: 1,
        label: 'Standard',
        workLabel: () => 'Focus Session',
        breakLabel: () => '',
    };
}

// localStorage helpers
const LS = {
    set: (phase: Phase, rep: number, totalReps: number, endTime: number) => {
        localStorage.setItem('session_end_time', endTime.toString());
        localStorage.setItem('session_phase', phase);
        localStorage.setItem('session_rep_current', rep.toString());
        localStorage.setItem('session_rep_total', totalReps.toString());
    },
    get: () => ({
        endTime: parseInt(localStorage.getItem('session_end_time') || '0'),
        phase: (localStorage.getItem('session_phase') || 'idle') as Phase,
        rep: parseInt(localStorage.getItem('session_rep_current') || '1'),
        totalReps: parseInt(localStorage.getItem('session_rep_total') || '1'),
    }),
    clear: () => {
        localStorage.removeItem('session_end_time');
        localStorage.removeItem('session_phase');
        localStorage.removeItem('session_rep_current');
        localStorage.removeItem('session_rep_total');
        localStorage.removeItem('session_state');
    },
};

const SessionTimer: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const initialState: TimerState = (() => {
        // If returning from Notes, restore the full state from localStorage
        const saved = localStorage.getItem('session_state');
        const activeSession = localStorage.getItem('session_end_time');
        if (saved && activeSession) {
            try {
                const parsed = JSON.parse(saved) as TimerState;
                if (parsed.courseName) return parsed;
            } catch { /* fall through */ }
        }
        return (location.state as TimerState) || {
            courseName: 'General Study', courseCode: 'STUDY',
            durationMinutes: 90, technique: 'Standard',
            goal: 'Focus on material',
        };
    })();

    const config = getTechniqueConfig(initialState.technique, initialState.durationMinutes);
    const totalReps = initialState.totalSets || config.defaultReps;
    const hasBreaks = config.breakMinutes > 0 && totalReps > 1;

    // ── Compute initial timer values from localStorage if an active session exists ──
    const _storedEndTime = parseInt(localStorage.getItem('session_end_time') || '0');
    const _storedRemaining = _storedEndTime - Date.now();
    const _hasActive = _storedEndTime > 0 && _storedRemaining > 0;

    // Core timer state — initialized from localStorage on restore, or fresh values otherwise
    const [phase, setPhase] = useState<Phase>(() =>
        _hasActive ? (localStorage.getItem('session_phase') || 'work') as Phase : 'work'
    );
    const [currentRep, setCurrentRep] = useState(() =>
        _hasActive ? parseInt(localStorage.getItem('session_rep_current') || '1') : 1
    );
    const [remainingMs, setRemainingMs] = useState(() =>
        _hasActive ? Math.max(0, _storedRemaining) : config.workMinutes * 60 * 1000
    );
    const [isPaused, setIsPaused] = useState(false);
    const [totalElapsedSec, setTotalElapsedSec] = useState(0);
    const startTimestamp = useRef(Date.now());
    // endTimeRef is pre-seeded from localStorage so the tick sees the correct value immediately
    const endTimeRef = useRef(_hasActive ? _storedEndTime : 0);

    // Alerts
    const [showEndSessionAlert, setShowEndSessionAlert] = useState(false);
    const [showDistractionAlert, setShowDistractionAlert] = useState(false);
    const [showUnfinishedAlert, setShowUnfinishedAlert] = useState(false);
    const [distractionTimeLeft, setDistractionTimeLeft] = useState(300);

    // Active Recall midpoint
    const [showRecallPrompt, setShowRecallPrompt] = useState(false);
    const recallPromptShown = useRef(false);

    // Post-session rating
    const [showRating, setShowRating] = useState(false);
    const [rating, setRating] = useState({
        success_score: 0, mood_after: 0, would_repeat: null as boolean | null,
    });
    const completedNaturally = useRef(true);
    const navigatingToNotes = useRef(false); // prevent LS.clear on notes navigation

    // Start a phase by anchoring an absolute end time
    const startPhaseTimer = useCallback((p: Phase, rep: number, durationMs: number) => {
        const endTime = Date.now() + durationMs;
        endTimeRef.current = endTime;
        setPhase(p);
        setCurrentRep(rep);
        setRemainingMs(durationMs);
        setIsPaused(false);
        LS.set(p, rep, totalReps, endTime);
    }, [totalReps]);

    // Sync display from the stored end time
    const syncFromEndTime = useCallback(() => {
        if (isPaused) return;
        const remaining = endTimeRef.current - Date.now();
        setRemainingMs(Math.max(0, remaining));
    }, [isPaused]);

    // Handle phase transition when timer hits zero
    const handlePhaseComplete = useCallback((currentPhase: Phase, rep: number) => {
        if (currentPhase === 'work') {
            if (rep >= totalReps || !hasBreaks) {
                // Session complete
                setPhase('complete');
                setIsPaused(true);
                LS.clear();
                setShowRating(true);
            } else {
                // Transition to break
                startPhaseTimer('break', rep, config.breakMinutes * 60 * 1000);
            }
        } else if (currentPhase === 'break') {
            // Transition to next work rep
            const nextRep = rep + 1;
            startPhaseTimer('work', nextRep, config.workMinutes * 60 * 1000);
        }
    }, [totalReps, hasBreaks, config, startPhaseTimer]);

    // Initialize timer on mount
    useEffect(() => {
        const storedEndTime = parseInt(localStorage.getItem('session_end_time') || '0');
        const remaining = storedEndTime - Date.now();

        if (storedEndTime && remaining > 0) {
            // Restoring from Notes — all state already set via lazy useState + endTimeRef above.
            // Nothing to do; the tick interval will pick up from endTimeRef.current.
        } else {
            // Fresh start — kick off the first phase
            startPhaseTimer('work', 1, config.workMinutes * 60 * 1000);
            startTimestamp.current = Date.now();
        }

        // DO NOT call LS.clear() here. StrictMode double-invokes this cleanup in dev,
        // which would wipe localStorage between the two mounts and break restore.
        // LS.clear() is called explicitly in all end paths (handleEndAnyway,
        // handlePhaseComplete, handleSubmitRating).
    }, []); // eslint-disable-line react-hooks/exhaustive-deps

    // Main tick interval (500ms)
    useEffect(() => {
        if (isPaused || phase === 'complete') return;
        const interval = setInterval(() => {
            const remaining = endTimeRef.current - Date.now();
            const clamped = Math.max(0, remaining);
            setRemainingMs(clamped);
            setTotalElapsedSec(Math.floor((Date.now() - startTimestamp.current) / 1000));
            if (clamped <= 0) {
                clearInterval(interval);
                handlePhaseComplete(phase, currentRep);
            }
        }, 500);
        return () => clearInterval(interval);
    }, [isPaused, phase, currentRep, handlePhaseComplete]);

    // Visibility change listener — snap timer on tab return
    useEffect(() => {
        const handleVisibility = () => {
            if (document.visibilityState === 'visible') syncFromEndTime();
        };
        document.addEventListener('visibilitychange', handleVisibility);
        return () => document.removeEventListener('visibilitychange', handleVisibility);
    }, [syncFromEndTime]);

    // Active Recall midpoint prompt
    useEffect(() => {
        if (config.label !== 'Active Recall' || recallPromptShown.current) return;
        const halfWork = config.workMinutes * 60 * 1000 / 2;
        if (phase === 'work' && remainingMs <= halfWork && remainingMs > 0) {
            recallPromptShown.current = true;
            setIsPaused(true);
            setShowRecallPrompt(true);
            // Freeze the end time so pause doesn't lose time
            const pausedRemaining = endTimeRef.current - Date.now();
            endTimeRef.current = Date.now() + Math.max(0, pausedRemaining);
        }
    }, [remainingMs, phase, config]);

    // Distraction timer
    useEffect(() => {
        if (!showDistractionAlert || distractionTimeLeft <= 0) return;
        const interval = setInterval(() => setDistractionTimeLeft(p => p - 1), 1000);
        return () => clearInterval(interval);
    }, [showDistractionAlert, distractionTimeLeft]);

    // Prevent back navigation
    useEffect(() => {
        const handlePopState = () => {
            if (phase !== 'complete') {
                window.history.pushState(null, '', window.location.pathname);
                pauseTimer();
                setShowUnfinishedAlert(true);
            }
        };
        window.history.pushState(null, '', window.location.pathname);
        window.addEventListener('popstate', handlePopState);
        return () => window.removeEventListener('popstate', handlePopState);
    }, [phase]);

    // Pause / resume helpers
    const pauseTimer = () => {
        const remaining = endTimeRef.current - Date.now();
        endTimeRef.current = Date.now() + Math.max(0, remaining); // freeze
        setIsPaused(true);
    };

    const resumeTimer = () => {
        // Re-anchor end time from current remaining
        const remaining = endTimeRef.current - Date.now();
        const newEnd = Date.now() + Math.max(0, remaining);
        endTimeRef.current = newEnd;
        LS.set(phase, currentRep, totalReps, newEnd);
        setIsPaused(false);
        setShowEndSessionAlert(false);
        setShowDistractionAlert(false);
        setShowUnfinishedAlert(false);
    };

    const handleEndAnyway = () => {
        completedNaturally.current = false;
        setPhase('complete');
        setIsPaused(true);
        LS.clear();
        setShowEndSessionAlert(false);
        setShowUnfinishedAlert(false);
        setShowRating(true);
    };

    const handleSubmitRating = async () => {
        const elapsedMinutes = Math.floor(totalElapsedSec / 60);
        const scheduledMinutes = initialState.durationMinutes;

        if (initialState.blockId && completedNaturally.current) {
            try {
                await api.post(`/schedule/${initialState.blockId}/complete`, {});
            } catch (error) {
                console.error("Failed to mark session as complete", error);
            }
        }
        try {
            await api.post('/sessions/end', {
                session_id: initialState.studySessionId,
                success_score: rating.success_score,
                mood_after: rating.mood_after,
                would_repeat: rating.would_repeat,
                actual_duration_minutes: elapsedMinutes,
                completed_on_time: completedNaturally.current && elapsedMinutes >= scheduledMinutes * 0.9,
                total_distraction_seconds: 0,
            });
        } catch (error) {
            console.error('Failed to submit session rating', error);
        }
        LS.clear();
        const outcome = completedNaturally.current ? 'completed' : 'ended_early';
        if (initialState.blockId) {
            localStorage.setItem(`block_status_${initialState.blockId}`, outcome);
        }
        navigate('/schedule', {
            state: { completedBlockId: initialState.blockId, outcome }
        });
    };

    // Format helpers
    const totalSec = Math.ceil(remainingMs / 1000);
    const h = Math.floor(totalSec / 3600).toString().padStart(2, '0');
    const m = Math.floor((totalSec % 3600) / 60).toString().padStart(2, '0');
    const s = (totalSec % 60).toString().padStart(2, '0');
    const dH = Math.floor(distractionTimeLeft / 60).toString().padStart(2, '0');
    const dS = (distractionTimeLeft % 60).toString().padStart(2, '0');

    // Progress bar
    const totalSessionMs = (() => {
        const workTotal = config.workMinutes * 60 * 1000 * totalReps;
        const breakTotal = hasBreaks ? config.breakMinutes * 60 * 1000 * (totalReps - 1) : 0;
        return workTotal + breakTotal;
    })();
    const elapsedMs = Date.now() - startTimestamp.current;
    const progressPct = Math.min(100, (elapsedMs / totalSessionMs) * 100);

    // Phase label
    const phaseLabel = phase === 'work'
        ? config.workLabel(currentRep, totalReps)
        : phase === 'break'
            ? config.breakLabel(currentRep)
            : 'Session Complete';

    const isBreakPhase = phase === 'break';

    return (
        <div className={`min-h-screen flex flex-col items-center justify-center font-sans transition-colors duration-500 ${isBreakPhase ? 'bg-green-50' : 'bg-white'}`}>

            {/* Header / Info */}
            <div className="w-full max-w-4xl px-8 flex justify-between items-start mb-8 text-center">
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
                        {totalReps > 1 && <span className="text-xs font-bold bg-gray-100 px-2 py-1 rounded-full text-gray-600">Rep {currentRep} of {totalReps}</span>}
                    </p>
                </div>
                <div className="flex-1 text-center">
                    <p className="text-sm font-semibold text-blue-800 mb-1">Goal</p>
                    <p className="text-lg text-gray-500 font-light">{initialState.goal}</p>
                </div>
            </div>

            {/* Phase Indicator */}
            <div className="mb-4">
                <span className={`px-4 py-2 rounded-full text-sm font-bold tracking-widest uppercase ${isBreakPhase ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                    {phaseLabel}
                </span>
            </div>

            {/* Subtitle for Deep Work */}
            {config.label === 'Deep Work' && phase === 'work' && (
                <p className="text-sm text-gray-400 mb-4">No interruptions until the timer ends</p>
            )}

            {/* Progress Bar */}
            <div className="w-full max-w-md mb-8">
                <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-600 rounded-full transition-all duration-1000" style={{ width: `${progressPct}%` }} />
                </div>
            </div>

            {/* Timer Display */}
            <div className="flex items-center space-x-8 text-gray-900 mb-24">
                {parseInt(h) > 0 && (
                    <>
                        <div className="flex flex-col items-center">
                            <span className="text-[128px] font-light font-josefin leading-none">{h}</span>
                            <span className="text-gray-400 text-lg mt-2 font-dm-sans">Hours</span>
                        </div>
                        <span className="text-[128px] font-light font-josefin text-gray-900 relative -top-8">:</span>
                    </>
                )}
                <div className="flex flex-col items-center">
                    <span className="text-[128px] font-light font-josefin leading-none">{m}</span>
                    <span className="text-gray-400 text-lg mt-2 font-dm-sans">Minutes</span>
                </div>
                <span className="text-[128px] font-light font-josefin text-gray-900 relative -top-8">:</span>
                <div className="flex flex-col items-center">
                    <span className="text-[128px] font-light font-josefin leading-none">{s}</span>
                    <span className="text-gray-400 text-lg mt-2 font-dm-sans">Seconds</span>
                </div>
            </div>

            {/* Action Buttons */}
            {phase !== 'complete' && (
                <div className="flex flex-col items-center gap-4">
                    <div className="flex space-x-8">
                        <button
                            onClick={() => { pauseTimer(); setShowDistractionAlert(true); setDistractionTimeLeft(300); }}
                            className="bg-blue-800 hover:bg-blue-900 text-white font-semibold py-4 px-10 rounded-lg text-base shadow-sm transition-transform active:scale-95"
                        >Log Distraction</button>
                        <button
                            onClick={() => { pauseTimer(); setShowEndSessionAlert(true); }}
                            className="bg-red-700 hover:bg-red-800 text-white font-semibold py-4 px-10 rounded-lg text-base shadow-sm transition-transform active:scale-95"
                        >End Session</button>
                    </div>
                    <button
                        onClick={() => {
                            // Write full, verified state before navigating
                            navigatingToNotes.current = true;
                            const stateToSave: TimerState = {
                                ...initialState,
                                // Re-anchor IDs in case they came from localStorage restore
                            };
                            localStorage.setItem('session_state', JSON.stringify(stateToSave));
                            // Verify write succeeded before navigating
                            const verify = localStorage.getItem('session_state');
                            if (!verify) {
                                console.error('[Timer] Failed to persist session_state');
                                navigatingToNotes.current = false;
                                return;
                            }
                            navigate('/notes', {
                                state: {
                                    fromTimer: true,
                                    courseName: initialState.courseName,
                                    courseCode: initialState.courseCode,
                                    courseId: initialState.courseId,
                                }
                            });
                        }}
                        className="border border-gray-300 hover:border-gray-400 text-gray-600 hover:text-gray-800 font-medium py-2 px-8 rounded-lg text-sm transition-colors flex items-center gap-2"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                        Open Notes
                    </button>
                </div>
            )}

            {/* --- ALERTS & OVERLAYS --- */}

            {/* Distraction Alert */}
            {showDistractionAlert && (
                <div className="absolute inset-0 z-50 bg-gray-900/20 backdrop-blur-sm flex items-center justify-center">
                    <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full text-center">
                        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Resuming in <span className="text-pink-600 font-bold">{dH}:{dS}</span></p>
                        <h3 className="text-lg font-bold text-gray-900 mb-3">Distraction Logged</h3>
                        <p className="text-gray-600 text-sm mb-6">Write it down, get it out of your head, and get back to work.</p>
                        <button onClick={resumeTimer} className="bg-blue-800 text-white font-semibold py-2.5 px-8 rounded-lg text-sm">Resume</button>
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
                            <button onClick={resumeTimer} className="bg-gray-100 text-gray-800 py-2 px-6 rounded-lg text-sm">Resume</button>
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
                            <button onClick={resumeTimer} className="bg-gray-100 text-gray-800 py-2 px-6 rounded-lg text-sm">Stay</button>
                            <button onClick={handleEndAnyway} className="bg-red-700 text-white py-2 px-6 rounded-lg text-sm">Leave</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Active Recall Midpoint Prompt */}
            {showRecallPrompt && (
                <div className="absolute inset-0 z-50 bg-gray-900/20 backdrop-blur-sm flex items-center justify-center">
                    <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full text-center">
                        <h3 className="text-lg font-bold text-gray-900 mb-3">⏸️ Halfway Point</h3>
                        <p className="text-gray-600 text-sm mb-6">
                            Close your notes. Write down everything you remember from this topic without looking.
                            This is the most important part of Active Recall.
                        </p>
                        <button
                            onClick={() => { setShowRecallPrompt(false); resumeTimer(); }}
                            className="bg-blue-800 text-white font-semibold py-2.5 px-8 rounded-lg text-sm"
                        >I've done it — Continue</button>
                    </div>
                </div>
            )}

            {/* Post-Session Rating Screen */}
            {showRating && (
                <div className="absolute inset-0 z-50 bg-white flex items-center justify-center">
                    <div className="max-w-lg w-full px-8">
                        <h2 className="text-2xl font-bold text-gray-900 mb-1 text-center">Quick Session Review</h2>
                        <p className="text-gray-400 text-sm mb-8 text-center">Takes under 15 seconds</p>

                        <div className="mb-6">
                            <label className="block text-sm font-semibold text-gray-700 mb-3">How effective was this session?</label>
                            <div className="flex gap-2 justify-center">
                                {[1, 2, 3, 4, 5].map((n) => (
                                    <button key={n} onClick={() => setRating({ ...rating, success_score: n })}
                                        className={`w-12 h-12 rounded-lg text-lg font-bold transition-all ${rating.success_score === n ? 'bg-blue-800 text-white shadow-md scale-110' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'}`}
                                    >{n}</button>
                                ))}
                            </div>
                            <div className="flex justify-between text-xs text-gray-400 mt-1 px-1">
                                <span>Not at all</span><span>Very effective</span>
                            </div>
                        </div>

                        <div className="mb-6">
                            <label className="block text-sm font-semibold text-gray-700 mb-3">How do you feel?</label>
                            <div className="flex gap-3 justify-center">
                                {[{ value: 1, label: '😩 Drained' }, { value: 2, label: '😐 Neutral' }, { value: 3, label: '⚡ Energized' }].map((opt) => (
                                    <button key={opt.value} onClick={() => setRating({ ...rating, mood_after: opt.value })}
                                        className={`flex-1 py-3 rounded-lg text-sm font-semibold transition-all ${rating.mood_after === opt.value ? 'bg-blue-800 text-white shadow-md' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                                    >{opt.label}</button>
                                ))}
                            </div>
                        </div>

                        <div className="mb-8">
                            <label className="block text-sm font-semibold text-gray-700 mb-3">
                                Would you use <span className="text-blue-800">{initialState.technique}</span> again?
                            </label>
                            <div className="flex gap-3 justify-center">
                                {[{ value: true, label: '👍 Yes' }, { value: false, label: '👎 No' }].map((opt) => (
                                    <button key={String(opt.value)} onClick={() => setRating({ ...rating, would_repeat: opt.value })}
                                        className={`flex-1 py-3 rounded-lg text-sm font-semibold transition-all ${rating.would_repeat === opt.value ? 'bg-blue-800 text-white shadow-md' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                                    >{opt.label}</button>
                                ))}
                            </div>
                        </div>

                        <button onClick={handleSubmitRating}
                            disabled={!rating.success_score || !rating.mood_after || rating.would_repeat === null}
                            className={`w-full py-3 rounded-lg text-base font-semibold transition-all ${rating.success_score && rating.mood_after && rating.would_repeat !== null ? 'bg-green-600 hover:bg-green-700 text-white shadow-sm' : 'bg-gray-200 text-gray-400 cursor-not-allowed'}`}
                        >Submit & Return to Dashboard</button>
                    </div>
                </div>
            )}

        </div>
    );
};

export default SessionTimer;

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const SessionTimer: React.FC = () => {
    const navigate = useNavigate();
    // 90 minutes in seconds = 90 * 60 = 5400
    const [timeLeft, setTimeLeft] = useState(5400);
    const [isActive, setIsActive] = useState(true);
    const [showEndSessionAlert, setShowEndSessionAlert] = useState(false);
    const [showDistractionAlert, setShowDistractionAlert] = useState(false);
    const [showUnfinishedAlert, setShowUnfinishedAlert] = useState(false);
    const [distractionTimeLeft, setDistractionTimeLeft] = useState(300); // 5 mins

    // Prevent back navigation
    useEffect(() => {
        const handlePopState = () => {
            if (timeLeft > 0) {
                // Prevent actual navigation
                window.history.pushState(null, '', window.location.pathname);
                setIsActive(false);
                setShowUnfinishedAlert(true);
            }
        };

        // Push initial state to allow popping it
        window.history.pushState(null, '', window.location.pathname);
        window.addEventListener('popstate', handlePopState);

        return () => {
            window.removeEventListener('popstate', handlePopState);
        };
    }, [timeLeft]); // Depend on timeLeft to know if we should intercept

    // Timer Logic
    useEffect(() => {
        let interval: ReturnType<typeof setInterval> | null = null;
        if (isActive && timeLeft > 0) {
            interval = setInterval(() => {
                setTimeLeft((prev) => prev - 1);
            }, 1000);
        } else if (timeLeft === 0) {
            if (interval) clearInterval(interval);
            setIsActive(false);
        }
        return () => {
            if (interval) clearInterval(interval);
        };
    }, [isActive, timeLeft]);

    // Distraction Timer Logic (Only runs when distraction alert is open)
    useEffect(() => {
        let interval: ReturnType<typeof setInterval> | null = null;
        if (showDistractionAlert && distractionTimeLeft > 0) {
            interval = setInterval(() => {
                setDistractionTimeLeft((prev) => prev - 1);
            }, 1000);
        } else if (distractionTimeLeft === 0 && showDistractionAlert) {
            // Auto resume or handle distraction end?
            // For now, let's just stop decrementing.
        }
        return () => {
            if (interval) clearInterval(interval);
        };
    }, [showDistractionAlert, distractionTimeLeft]);


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

    const handleEndSessionClick = () => {
        if (timeLeft > 0) {
            // Pause timer and show alert
            setIsActive(false);
            setShowEndSessionAlert(true);
        } else {
            // Session naturally finished
            navigate('/dashboard');
        }
    };

    const handleLogDistractionClick = () => {
        setIsActive(false); // Pause main timer
        setShowDistractionAlert(true);
        setDistractionTimeLeft(300); // Reset to 5 mins
    };

    const handleResume = () => {
        setShowEndSessionAlert(false);
        setShowDistractionAlert(false);
        setShowUnfinishedAlert(false);
        setIsActive(true);
    };

    const handleEndAnyway = () => {
        navigate('/dashboard');
    };

    const time = formatTime(timeLeft);
    const distractionTime = formatTime(distractionTimeLeft);

    return (
        <div className="min-h-screen bg-white flex flex-col items-center justify-center font-sans">

            {/* Header / Info */}
            <div className="w-full max-w-4xl px-8 flex justify-between items-start mb-24 text-center">
                <div className="flex-1 text-center">
                    <p className="text-sm font-semibold text-blue-800 mb-1">Currently Studying</p>
                    <p className="text-lg text-gray-700 font-medium">
                        <span className="font-bold text-gray-900">MTH202</span> – Mathematical Models II
                    </p>
                </div>
                <div className="flex-1 text-center">
                    <p className="text-sm font-semibold text-blue-800 mb-1">Objective</p>
                    <p className="text-lg text-gray-500 font-light">Finish reading Week 6</p>
                </div>
            </div>

            {/* Timer Display */}
            <div className="flex items-center space-x-8 text-gray-900 mb-24">
                <div className="flex flex-col items-center">
                    <span className="text-[128px] font-light font-josefin leading-none">{time.h}</span>
                    <span className="text-gray-400 text-lg mt-2 font-dm-sans">Hours</span>
                </div>
                <span className="text-[128px] font-light font-josefin text-gray-900 relative -top-8">:</span>
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
                    onClick={handleLogDistractionClick}
                    className="bg-blue-800 hover:bg-blue-900 text-white font-semibold py-4 px-10 rounded-lg text-base shadow-sm transition-transform active:scale-95"
                >
                    Log Distraction
                </button>
                <button
                    onClick={handleEndSessionClick}
                    className="bg-red-700 hover:bg-red-800 text-white font-semibold py-4 px-10 rounded-lg text-base shadow-sm transition-transform active:scale-95"
                >
                    End Session
                </button>
            </div>

            {/* Completion View (Shown when timer is 00:00:00) */}
            {timeLeft === 0 && (
                <div className="absolute inset-0 bg-white flex flex-col items-center justify-center z-20">
                    <div className="text-center mb-12">
                        <p className="text-pink-600 font-bold mb-2">90 Minutes: Elite Performance</p>
                        <h2 className="text-gray-600 text-sm max-w-lg mx-auto leading-relaxed">
                            You pushed through the friction and stayed in the zone. That's a full deep work cycle completed.
                            You're literally re-wiring your brain for better concentration right now.
                        </h2>
                    </div>

                    <div className="w-full max-w-4xl px-8 flex justify-between items-start mb-24 text-center">
                        <div className="flex-1 text-center">
                            <p className="text-sm font-semibold text-blue-800 mb-1">Currently Studying</p>
                            <p className="text-lg text-gray-700 font-medium">
                                <span className="font-bold text-gray-900">MTH202</span> – Mathematical Models II
                            </p>
                        </div>
                        <div className="flex-1 text-center">
                            <p className="text-sm font-semibold text-blue-800 mb-1">Objective</p>
                            <p className="text-lg text-gray-500 font-light">Finish reading Week 6</p>
                        </div>
                    </div>
                    {/* Timer at 0 */}
                    <div className="flex items-center space-x-8 text-gray-900 mb-24">
                        <div className="flex flex-col items-center">
                            <span className="text-[120px] font-thin leading-none">00</span>
                            <span className="text-gray-400 text-lg mt-2">Hours</span>
                        </div>
                        <span className="text-[80px] font-thin text-gray-900 relative -top-8">:</span>
                        <div className="flex flex-col items-center">
                            <span className="text-[120px] font-thin leading-none">00</span>
                            <span className="text-gray-400 text-lg mt-2">Minutes</span>
                        </div>
                        <span className="text-[80px] font-thin text-gray-900 relative -top-8">:</span>
                        <div className="flex flex-col items-center">
                            <span className="text-[120px] font-thin leading-none">00</span>
                            <span className="text-gray-400 text-lg mt-2">Seconds</span>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex space-x-8">
                        <button
                            onClick={() => { }} // Log Distraction usually disabled/different here? Figma shows same buttons.
                            className="bg-blue-800 hover:bg-blue-900 text-white font-semibold py-4 px-10 rounded-lg text-base shadow-sm transition-transform active:scale-95"
                        >
                            Log Distraction
                        </button>
                        <button
                            onClick={handleEndAnyway}
                            className="bg-green-600 hover:bg-green-700 text-white font-semibold py-4 px-10 rounded-lg text-base shadow-sm transition-transform active:scale-95"
                        >
                            End Session
                        </button>
                    </div>
                </div>
            )}


            {/* End Session Alert Overlay */}
            {showEndSessionAlert && (
                <div className="absolute inset-0 z-50 bg-gray-900/20 backdrop-blur-sm flex items-center justify-center">
                    <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full animate-in fade-in zoom-in-95 duration-200">
                        <h3 className="text-lg font-bold text-gray-900 mb-3">Session Incomplete</h3>
                        <p className="text-gray-600 text-sm mb-6 leading-relaxed">
                            If you end now, this will be logged as an <span className="font-bold">incomplete</span> session. Your goal was 90 minutes of focus. Can you find one more small thing to work on to finish the block?
                        </p>
                        <div className="flex justify-end space-x-3">
                            <button
                                onClick={handleResume}
                                className="bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-2 px-6 rounded-lg text-sm transition-colors"
                            >
                                Continue Studying
                            </button>
                            <button
                                onClick={handleEndAnyway}
                                className="bg-red-700 hover:bg-red-800 text-white font-semibold py-2 px-6 rounded-lg text-sm shadow-sm transition-colors"
                            >
                                End Anyway
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Back Navigation Intercept Alert */}
            {showUnfinishedAlert && (
                <div className="absolute inset-0 z-50 bg-gray-900/20 backdrop-blur-sm flex items-center justify-center">
                    <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full animate-in fade-in zoom-in-95 duration-200">
                        <h3 className="text-lg font-bold text-gray-900 mb-3">End Active Session?</h3>
                        <p className="text-gray-600 text-sm mb-6 leading-relaxed">
                            Your timer is still running. If you leave this page, your current progress will be lost.
                        </p>
                        <div className="flex justify-end space-x-3">
                            <button
                                onClick={handleResume}
                                className="bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-2 px-6 rounded-lg text-sm transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleEndAnyway}
                                className="bg-red-700 hover:bg-red-800 text-white font-semibold py-2 px-6 rounded-lg text-sm shadow-sm transition-colors"
                            >
                                End Anyway
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Distraction Alert Overlay */}
            {showDistractionAlert && (
                <div className="absolute inset-0 z-50 bg-gray-900/20 backdrop-blur-sm flex items-center justify-center">
                    <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full animate-in fade-in zoom-in-95 duration-200 text-center">
                        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Automatically resuming in <span className="text-pink-600 font-bold">{distractionTime.m}:{distractionTime.s}</span> </p>
                        <h3 className="text-lg font-bold text-gray-900 mb-3">Quick Interruption?</h3>
                        <p className="text-gray-600 text-sm mb-6 leading-relaxed">
                            We've paused the clock for 5 minutes. Handle the distraction and get back into the zone before your "focus engine" cools down.
                        </p>
                        <button
                            onClick={handleResume}
                            className="bg-blue-800 hover:bg-blue-900 text-white font-semibold py-2.5 px-8 rounded-lg text-sm shadow-sm transition-colors"
                        >
                            Resume
                        </button>
                    </div>
                </div>
            )}

        </div>
    );
};

export default SessionTimer;

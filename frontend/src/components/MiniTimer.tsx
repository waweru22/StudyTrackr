import React, { useState, useEffect } from 'react';
import { ArrowLeft, Timer } from 'lucide-react';

interface MiniTimerProps {
    courseName: string;
    onBackToTimer: () => void;
}

const phaseLabel = (phase: string): string => {
    if (phase === 'work') return 'Focus Time';
    if (phase === 'break') return 'Break Time';
    if (phase === 'complete') return 'Complete';
    return 'Deep Work';
};

const MiniTimer: React.FC<MiniTimerProps> = ({ courseName, onBackToTimer }) => {
    const [display, setDisplay] = useState<{ mm: string; ss: string; phase: string; rep: string } | null>(null);

    useEffect(() => {
        const tick = () => {
            const endTime = parseInt(localStorage.getItem('session_end_time') || '0');
            const phase = localStorage.getItem('session_phase') || '';
            const rep = parseInt(localStorage.getItem('session_rep_current') || '0');
            const totalReps = parseInt(localStorage.getItem('session_rep_total') || '0');

            if (!endTime || endTime <= Date.now()) {
                setDisplay(null);
                return;
            }

            const remaining = Math.max(0, endTime - Date.now());
            const totalSec = Math.ceil(remaining / 1000);
            const mm = Math.floor(totalSec / 60).toString().padStart(2, '0');
            const ss = (totalSec % 60).toString().padStart(2, '0');
            const repStr = totalReps > 1 ? `Rep ${rep} of ${totalReps}` : '';

            setDisplay({ mm, ss, phase, rep: repStr });
        };

        tick();
        const id = setInterval(tick, 500);
        return () => clearInterval(id);
    }, []);

    if (!display) return null;

    return (
        <div
            style={{
                position: 'fixed',
                top: '16px',
                left: '50%',
                transform: 'translateX(-50%)',
                zIndex: 9999,
            }}
            className="flex items-center gap-3 bg-white border border-gray-200 shadow-lg rounded-full px-4 py-2.5 text-sm"
        >
            {/* Pulsing dot */}
            <span className="relative flex h-2.5 w-2.5 shrink-0">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500" />
            </span>

            <Timer size={14} className="text-blue-800 shrink-0" />

            {/* Course */}
            <span className="font-semibold text-gray-800 max-w-[140px] truncate">{courseName}</span>

            {/* Phase */}
            <span className="text-gray-400">·</span>
            <span className="text-gray-600 font-medium">{phaseLabel(display.phase)}</span>

            {/* Time */}
            <span className="font-mono font-bold text-blue-800 tabular-nums">{display.mm}:{display.ss}</span>

            {/* Rep */}
            {display.rep && (
                <>
                    <span className="text-gray-300">|</span>
                    <span className="text-xs text-gray-500">{display.rep}</span>
                </>
            )}

            {/* Back button */}
            <button
                onClick={onBackToTimer}
                className="flex items-center gap-1 ml-1 bg-blue-800 hover:bg-blue-900 text-white text-xs font-semibold px-3 py-1.5 rounded-full transition-colors"
            >
                <ArrowLeft size={12} />
                Back to Timer
            </button>
        </div>
    );
};

export default MiniTimer;

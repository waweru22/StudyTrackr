import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, Battery, BatteryMedium, BatteryLow, User, Users, Eye, Ear, NotebookPen, Book, Laptop, Tablet, Smartphone, LayoutGrid } from 'lucide-react';

interface SessionModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const SessionModal: React.FC<SessionModalProps> = ({ isOpen, onClose }) => {
    const navigate = useNavigate();
    const [vibe, setVibe] = useState('');
    const [social, setSocial] = useState('');
    const [learningMode, setLearningMode] = useState('');
    const [learningMedium, setLearningMedium] = useState('');
    const [environment, setEnvironment] = useState('');
    const [otherEnvironment, setOtherEnvironment] = useState('');
    const [goal, setGoal] = useState('');
    const [error, setError] = useState('');

    const handleStart = () => {
        if (!vibe) {
            setError('Please select your current vibe.');
            return;
        }
        if (!social) {
            setError('Please select a social setting.');
            return;
        }
        if (!learningMode) {
            setError('Please select a learning mode.');
            return;
        }
        if (!learningMedium) {
            setError('Please select a learning medium.');
            return;
        }
        if (!environment) {
            setError('Please select an environment.');
            return;
        }
        if (environment === 'Other' && !otherEnvironment.trim()) {
            setError('Please specify your environment.');
            return;
        }
        // Proceed with session start
        onClose();
        navigate('/session-timer');
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-3xl w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-2xl relative animate-in fade-in zoom-in-95 duration-200">
                {/* Header */}
                <div className="p-6 pb-2 sticky top-0 bg-white z-10 border-b border-gray-50">
                    <div className="flex justify-between items-start">
                        <div>
                            <h2 className="text-xl font-bold text-gray-900">Set the Scene</h2>
                            <p className="text-sm text-gray-500 mt-1">
                                Help the AI understand your current conditions to optimize your next session.
                            </p>
                        </div>
                        <button onClick={onClose} className="text-gray-400 hover:text-gray-600 p-1 rounded-full hover:bg-gray-100 transition-colors">
                            <X size={20} />
                        </button>
                    </div>
                </div>

                {/* Scrollable Content */}
                <div className="p-6 space-y-6">

                    {/* Current Vibe */}
                    <div>
                        <h3 className="text-sm font-bold text-gray-700 mb-3">Current Vibe</h3>
                        <div className="flex space-x-3">
                            {[
                                { label: 'High Energy', icon: Battery, color: 'text-green-500', fill: 'fill-green-500' },
                                { label: 'Normal', icon: BatteryMedium, color: 'text-yellow-500', fill: 'fill-yellow-500' },
                                { label: 'Low Energy', icon: BatteryLow, color: 'text-red-500', fill: 'fill-red-500' }
                            ].map((option) => (
                                <button
                                    key={option.label}
                                    onClick={() => setVibe(option.label)}
                                    className={`flex-1 flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all ${vibe === option.label ? 'border-blue-600 bg-blue-50' : 'border-gray-100 hover:border-gray-200'}`}
                                >
                                    <option.icon className={`mb-2 ${option.color} ${option.fill}`} size={24} />
                                    <span className={`text-xs font-semibold ${vibe === option.label ? 'text-blue-900' : 'text-gray-600'}`}>{option.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Social Setting */}
                    <div>
                        <h3 className="text-sm font-bold text-gray-700 mb-3">Social Setting</h3>
                        <div className="flex space-x-3 w-2/3">
                            {[
                                { label: 'Solo', icon: User, color: 'text-purple-600' },
                                { label: 'Group', icon: Users, color: 'text-pink-600' }
                            ].map((option) => (
                                <button
                                    key={option.label}
                                    onClick={() => setSocial(option.label)}
                                    className={`flex-1 flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all ${social === option.label ? 'border-blue-600 bg-blue-50' : 'border-gray-100 hover:border-gray-200'}`}
                                >
                                    <option.icon className={`mb-2 ${option.color} fill-current`} size={24} />
                                    <span className={`text-xs font-semibold ${social === option.label ? 'text-blue-900' : 'text-gray-600'}`}>{option.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Learning Mode */}
                    <div>
                        <h3 className="text-sm font-bold text-gray-700 mb-3">Learning Mode</h3>
                        <div className="grid grid-cols-4 gap-3">
                            {[
                                { id: 'Visual', label: 'Solo', icon: Eye, color: 'text-blue-400' }, // Label per image is 'Solo'
                                { id: 'Aural', label: 'Aural', icon: Ear, color: 'text-amber-700' },
                                { id: 'Read/Write', label: 'Read/Write', icon: NotebookPen, color: 'text-blue-700' },
                                { id: 'Kinesthetic', label: 'Kinesthetic', icon: LayoutGrid, color: 'text-green-500' } // Using LayoutGrid for blocks/shapes
                            ].map((option) => (
                                <button
                                    key={option.id}
                                    onClick={() => setLearningMode(option.id)}
                                    className={`flex flex-col items-center justify-center p-3 rounded-xl border-2 transition-all ${learningMode === option.id ? 'border-blue-600 bg-blue-50' : 'border-gray-100 hover:border-gray-200'}`}
                                >
                                    <option.icon className={`mb-2 ${option.color}`} size={24} />
                                    <span className={`text-[10px] font-semibold text-center ${learningMode === option.id ? 'text-blue-900' : 'text-gray-600'}`}>{option.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Learning Medium */}
                    <div>
                        <h3 className="text-sm font-bold text-gray-700 mb-3">Learning Medium</h3>
                        <div className="grid grid-cols-4 gap-3">
                            {[
                                { id: 'Laptop', label: 'Solo', icon: Laptop, color: 'text-cyan-500' }, // Label per image is 'Solo'
                                { id: 'Tablet', label: 'Aural', icon: Tablet, color: 'text-slate-500' }, // Label per image is 'Aural'
                                { id: 'Phone', label: 'Read/Write', icon: Smartphone, color: 'text-blue-600' }, // Label per image is 'Read/Write'
                                { id: 'Books', label: 'Paper/Books', icon: Book, color: 'text-indigo-600' }
                            ].map((option) => (
                                <button
                                    key={option.id}
                                    onClick={() => setLearningMedium(option.id)}
                                    className={`flex flex-col items-center justify-center p-3 rounded-xl border-2 transition-all ${learningMedium === option.id ? 'border-blue-600 bg-blue-50' : 'border-gray-100 hover:border-gray-200'}`}
                                >
                                    <option.icon className={`mb-2 ${option.color}`} size={24} />
                                    <span className={`text-[10px] font-semibold text-center ${learningMedium === option.id ? 'text-blue-900' : 'text-gray-600'}`}>{option.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Environment */}
                    <div>
                        <h3 className="text-sm font-bold text-gray-700 mb-3">Environment</h3>
                        <div className="flex flex-wrap gap-4 mb-4">
                            {['Home', 'Hostel', 'Library', 'Class', 'Other'].map((env) => (
                                <label key={env} className="flex items-center space-x-2 cursor-pointer group">
                                    <div className={`w-5 h-5 rounded-full border flex items-center justify-center ${environment === env ? 'border-blue-600' : 'border-gray-300 group-hover:border-blue-400'}`}>
                                        {environment === env && <div className="w-2.5 h-2.5 rounded-full bg-blue-600" />}
                                    </div>
                                    <input
                                        type="radio"
                                        name="environment"
                                        value={env}
                                        checked={environment === env}
                                        onChange={() => {
                                            setEnvironment(env);
                                            setError('');
                                        }}
                                        className="hidden"
                                    />
                                    <span className={`text-sm ${environment === env ? 'text-gray-900 font-medium' : 'text-gray-500'}`}>{env}</span>
                                </label>
                            ))}
                        </div>

                        {/* Specify here */}
                        <div className="space-y-1">
                            <label className={`text-sm font-medium ${environment === 'Other' ? 'text-gray-700' : 'text-gray-400 opacity-50'}`}>Specify here:</label>
                            <input
                                type="text"
                                disabled={environment !== 'Other'}
                                value={otherEnvironment}
                                onChange={(e) => {
                                    setOtherEnvironment(e.target.value);
                                    if (error) setError('');
                                }}
                                placeholder="e.g. Cafe"
                                className={`w-full px-4 py-3 rounded-lg border focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm transition-all ${environment === 'Other' ? (error ? 'border-red-500 bg-red-50' : 'bg-white border-gray-300 shadow-sm') : 'bg-gray-50 border-gray-200 text-gray-400 opacity-50 cursor-not-allowed'}`}
                            />
                            {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
                        </div>
                    </div>

                    {/* Session Goal */}
                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">Session Goal (Optional)</label>
                        <input
                            type="text"
                            value={goal}
                            onChange={(e) => setGoal(e.target.value)}
                            placeholder="e.g. Finish Week 6"
                            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm shadow-sm"
                        />
                    </div>
                </div>

                {/* Footer */}
                <div className="p-6 pt-2 border-t border-gray-50 sticky bottom-0 bg-white z-10">
                    <button
                        onClick={handleStart}
                        className="w-full bg-blue-800 hover:bg-blue-900 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-blue-200 transition-all transform active:scale-[0.99]"
                    >
                        Start
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SessionModal;

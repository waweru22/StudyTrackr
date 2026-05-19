import React, { useState } from 'react';
import { ArrowLeft, ArrowRight } from 'lucide-react';
import logo from '../assets/logo.png';
import sprinterImg from '../assets/blueprint_sprinter_v2.png';
import deepworkImg from '../assets/blueprint_deepwork_v2.png';
import recallImg from '../assets/blueprint_recall_v2.png';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';

interface BlueprintOption {
    id: string;
    title: string;
    image: string;
    techniques: string;
    description: string;
}

const BLUEPRINTS: BlueprintOption[] = [
    {
        id: 'sprinter',
        title: 'The "Balanced Sprinter"',
        image: sprinterImg,
        techniques: 'Techniques: Pomodoro & Interleaving',
        description: 'Keeps your brain engaged by rotating 3-4 different subjects across your day in 25-minute bursts. Expect a high-variety pace that ensures no course gets left behind.'
    },
    {
        id: 'deepwork',
        title: 'The "Deep-Work Specialist"',
        image: deepworkImg,
        techniques: 'Techniques: Flow State & Time Blocking',
        description: "We'll reserve your peak energy hours for 90-minute deep blocks dedicated to your toughest courses. Expect a calmer calendar with fewer transitions and more room for problem-solving."
    },
    {
        id: 'recall',
        title: 'The "Active Recaller"',
        image: recallImg,
        techniques: 'Techniques: Active Recall & Spaced Repetition',
        description: 'Your schedule will prioritize frequent, short review blocks for every course. This routine constantly challenges you to "recall" what you learned days ago, ensuring you never forget before exam day.'
    }
];

const OnboardingStep3: React.FC = () => {
    const navigate = useNavigate();
    const { step3Data, setStep3Data } = useUser();
    const [selectedBlueprint, setSelectedBlueprint] = useState<string | null>(step3Data.selectedBlueprint || null);

    const handleContinue = () => {
        if (selectedBlueprint) {
            setStep3Data({ selectedBlueprint });
            navigate('/onboarding/step-4');
        }
    };

    return (
        <div className="min-h-screen bg-white font-sans text-gray-900 flex flex-col items-center">
            {/* Header */}
            <header className="w-full max-w-5xl mx-auto px-6 py-6 flex items-center justify-between">
                <div className="flex items-center">
                    <img src={logo} alt="StudyTrackr Logo" className="h-10 w-auto" />
                </div>
                <button
                    onClick={() => navigate(-1)}
                    className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                    <ArrowLeft size={16} />
                    <span>Back</span>
                </button>
            </header>

            {/* Main Content */}
            <main className="w-full max-w-5xl px-6 py-8 flex-grow flex flex-col items-center">
                <div className="space-y-2 mb-10 w-full max-w-3xl">
                    <p className="text-sm font-medium text-gray-500 uppercase tracking-wider">3 of 4</p>
                    <h2 className="text-xl font-bold font-dm-sans text-gray-900">Choose Your Blueprint</h2>
                    <p className="text-gray-500 text-sm font-light font-dm-sans max-w-2xl">
                        Pick a starting template based on world-class study techniques. These provide the initial rules for our AI, which will refine and personalize them as you log your sessions.
                    </p>
                </div>

                {/* Blueprint Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-3xl mb-10">
                    {BLUEPRINTS.map((blueprint) => {
                        const isSelected = selectedBlueprint === blueprint.id;
                        return (
                            <div
                                key={blueprint.id}
                                onClick={() => setSelectedBlueprint(blueprint.id)}
                                className={`cursor-pointer rounded-xl border transition-all duration-200 p-6 flex flex-col items-center text-center h-full hover:shadow-lg ${isSelected ? 'border-blue-600 ring-2 ring-blue-600 ring-opacity-50 bg-blue-50/10' : 'border-gray-200 hover:border-blue-300'}`}
                            >
                                <div className="h-40 w-full flex items-end justify-center mb-6">
                                    <img src={blueprint.image} alt={blueprint.title} className="max-h-full w-auto object-contain" />
                                </div>
                                <h3 className="text-sm font-medium font-dm-sans text-gray-900 mb-1">{blueprint.title}</h3>
                                <p className="text-xs font-medium font-dm-sans text-blue-600 mb-1">{blueprint.techniques}</p>
                                <p className="text-xs font-light font-dm-sans text-gray-500 leading-relaxed text-left">
                                    {blueprint.description}
                                </p>
                            </div>
                        );
                    })}
                </div>

                {/* Continue Button */}
                <div className="w-full max-w-3xl">
                    <button
                        onClick={handleContinue}
                        disabled={!selectedBlueprint}
                        className={`w-full flex items-center justify-center space-x-2 font-semibold py-3.5 rounded-lg shadow-sm transition-all transform text-sm ${selectedBlueprint ? 'bg-blue-800 hover:bg-blue-900 text-white active:scale-[0.99]' : 'bg-blue-800/60 text-white/50 cursor-not-allowed'}`}
                    >
                        <span>Continue</span>
                        <ArrowRight size={18} />
                    </button>
                </div>

            </main>
        </div>
    );
};

export default OnboardingStep3;

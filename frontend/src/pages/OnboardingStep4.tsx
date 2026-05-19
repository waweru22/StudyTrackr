import React, { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import logo from '../assets/logo.png';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';

interface Step4FormData {
    peakTime: string;
    focusDuration: string;
    learningStyle: string;
    environment: string;
    approach: string;
}

const OnboardingStep4: React.FC = () => {
    const navigate = useNavigate();
    const { step1Data, step4Data, setStep4Data, registerUser } = useUser();
    const [formData, setFormData] = useState<Step4FormData>({
        peakTime: step4Data.peakTime || '',
        focusDuration: step4Data.focusDuration || '',
        learningStyle: step4Data.learningStyle || '',
        environment: step4Data.environment || '',
        approach: step4Data.approach || ''
    });

    const [errors, setErrors] = useState<Partial<Record<keyof Step4FormData, boolean>>>({});
    const [loading, setLoading] = useState(false);

    const handleSelection = (field: keyof Step4FormData, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
        // Clear error for this field when user selects something
        if (errors[field]) {
            setErrors(prev => ({ ...prev, [field]: false }));
        }
    };

    const validateAndSubmit = async () => {
        const newErrors: Partial<Record<keyof Step4FormData, boolean>> = {};
        let isValid = true;

        (Object.keys(formData) as Array<keyof Step4FormData>).forEach(key => {
            if (!formData[key]) {
                newErrors[key] = true;
                isValid = false;
            }
        });

        setErrors(newErrors);

        if (isValid) {
            setLoading(true); // Set loading true before API call
            // Update context first
            setStep4Data(formData);

            // Trigger Registration
            try {
                // For robustness, passing formData directly is better if registerUser supports it.
                // If registerUser relies solely on context state, there might be a slight delay.
                // For this edit, we assume registerUser can be called after setStep4Data.
                await registerUser(formData);
                console.log('Registration complete.');
                navigate('/check-email', { state: { email: step1Data.email } });
            } catch (e) {
                console.error("Registration failed:", e);
                // Optionally, display an error message to the user
                alert("Registration failed. Please try again.");
            }
        }
    };

    // Helper component for radio groups to reduce repetition
    const RadioGroup = ({
        label,
        field,
        options
    }: {
        label: string,
        field: keyof Step4FormData,
        options: { value: string, label: string }[]
    }) => (
        <div className={`space-y-2 ${errors[field] ? 'p-4 bg-red-50 rounded-lg border border-red-200' : ''}`}>
            <h3 className={`text-sm font-medium font-dm-sans text-gray-900 ${errors[field] ? 'text-red-700' : ''}`}>
                {label} {errors[field] && <span className="text-red-600 text-sm font-normal ml-2">* Required</span>}
            </h3>
            <div className="flex flex-wrap gap-4 md:gap-6">
                {options.map((option) => (
                    <label key={option.value} className="flex items-center space-x-2 cursor-pointer group">
                        <div className="relative flex items-center justify-center">
                            <input
                                type="radio"
                                name={field}
                                value={option.value}
                                checked={formData[field] === option.value}
                                onChange={() => handleSelection(field, option.value)}
                                className="peer appearance-none h-5 w-5 border-2 border-gray-300 rounded-full cursor-pointer checked:border-blue-800 transition-colors"
                            />
                            <div className="absolute h-2.5 w-2.5 rounded-full bg-blue-800 opacity-0 peer-checked:opacity-100 transition-opacity"></div>
                        </div>
                        <span className="text-sm font-light font-dm-sans text-gray-600 group-hover:text-gray-900">{option.label}</span>
                    </label>
                ))}
            </div>
        </div>
    );

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
            <main className="w-full max-w-3xl px-6 py-8 flex-grow">
                <div className="space-y-2 mb-4 pb-4 border-b border-gray-200">
                    <p className="text-sm font-medium text-gray-500 uppercase tracking-wider">4 of 4</p>
                    <h2 className="text-xl font-bold font-dm-sans text-gray-900">You're Almost There!</h2>
                    <p className="text-gray-500 text-sm font-light font-dm-sans max-w-2xl">
                        Every student is different. We're calibrating your schedule to match your natural focus peaks, so you can spend less time planning and more time mastering.
                    </p>
                </div>

                <div className="space-y-4">
                    <RadioGroup
                        label="When is your brain at 100%?"
                        field="peakTime"
                        options={[
                            { value: 'morning', label: '9am - 12pm' },
                            { value: 'afternoon', label: '1pm - 5pm' },
                            { value: 'evening', label: '8pm - 12am' },
                            { value: 'night', label: '1am - 4am' },
                            { value: 'early_morning', label: '4am - 8am' },
                        ]}
                    />

                    <RadioGroup
                        label="How long can you stay 'in the zone' before you need a breather?"
                        field="focusDuration"
                        options={[
                            { value: 'short', label: '< 30m (Fast-paced)' },
                            { value: 'medium', label: '45m - 1hr (Balanced)' },
                            { value: 'long', label: '90m - 2hrs (Intense)' },
                        ]}
                    />

                    <RadioGroup
                        label="What is your preferred learning style?"
                        field="learningStyle"
                        options={[
                            { value: 'visual', label: 'Visual' },
                            { value: 'aural', label: 'Aural' },
                            { value: 'read_write', label: 'Read/Write' },
                            { value: 'kinesthetic', label: 'Kinesthetic' },
                        ]}
                    />

                    <RadioGroup
                        label="In what environment do you get your best work done?"
                        field="environment"
                        options={[
                            { value: 'silent', label: 'Silent (Library/Private Room)' },
                            { value: 'ambient', label: 'Ambient (Cafe/Lounge)' },
                            { value: 'flexible', label: 'Flexible (I study anywhere)' },
                        ]}
                    />

                    <RadioGroup
                        label="How do you handle complex topics?"
                        field="approach"
                        options={[
                            { value: 'alone', label: 'I prefer to figure it out alone' },
                            { value: 'others', label: 'I learn better with others' },
                        ]}
                    />
                </div>

                <div className="pt-8 pb-12">
                    <button
                        onClick={validateAndSubmit}
                        disabled={loading}
                        className={`w-full text-white font-semibold py-3.5 rounded-lg shadow-sm transition-all transform active:scale-[0.99] text-sm ${loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-800 hover:bg-blue-900'}`}
                    >
                        {loading ? 'Finalizing...' : 'Done'}
                    </button>
                </div>

            </main>
        </div>
    );
};

export default OnboardingStep4;

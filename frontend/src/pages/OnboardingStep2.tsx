import React, { useState } from 'react';
import { ArrowLeft, ArrowRight, Plus, Minus, AlertCircle } from 'lucide-react';
import logo from '../assets/logo.png';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';

interface Course {
    id: string;
    code: string;
    name: string;
    credits: number;
}

const INITIAL_COURSES: Course[] = [
    { id: '1', code: 'SEN301', name: 'Software Construction', credits: 3 },
    { id: '2', code: 'NUN-DTS 304', name: 'Database Management', credits: 3 },
    { id: '3', code: 'NUN-ICT 306', name: 'Data Communications and Network', credits: 3 },
    { id: '4', code: 'NUN-IFT 311', name: 'Web Application Development', credits: 3 },
    { id: '5', code: 'NUN-SEN 331', name: 'Engineering Mobile Application', credits: 3 },
    { id: '6', code: 'CSC301', name: 'Data Structures', credits: 3 },
    { id: '7', code: 'NUN-COS 305', name: 'Remote Work and Virtual Collaboration', credits: 3 },
];

const OnboardingStep2: React.FC = () => {
    const navigate = useNavigate();
    const { level, step2Data, setStep2Data, setSemester } = useUser();

    // Initialize from Context or Defaults
    const [selectedSemester, setSelectedSemester] = useState<'harmattan' | 'rain'>(step2Data.selectedSemester || 'harmattan');
    const [selectedCourses, setSelectedCourses] = useState<string[]>(step2Data.selectedCourses || []);
    const [additionalCourse, setAdditionalCourse] = useState(step2Data.additionalCourse || '');
    const [error, setError] = useState<string>('');

    const toggleCourse = (courseId: string) => {
        // ... (this logic is fine, depends on state)
        setSelectedCourses(prev => {
            if (prev.includes(courseId)) {
                return prev.filter(id => id !== courseId);
            } else {
                if (prev.length >= 12) return prev; // Max 12 limit
                // Clear error if user selects a course and reaches 6
                if (prev.length + 1 >= 6) setError('');
                return [...prev, courseId];
            }
        });
    };

    const handleContinue = () => {
        if (selectedCourses.length < 6) {
            setError('Please select at least 6 courses to continue.');
            return;
        }
        setStep2Data({ selectedSemester, selectedCourses, additionalCourse });
        setSemester(selectedSemester === 'harmattan' ? '1 (Harmattan)' : '2 (Rain)');
        navigate('/onboarding/step-3');
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
            <main className="w-full max-w-3xl px-6 py-8 flex-grow">
                <div className="space-y-0 mb-6">
                    <p className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">2 of 4</p>
                    <h2 className="text-2xl font-bold font-dm-sans text-gray-900 mb-2">Define Your Semester</h2>
                    <p className="text-gray-500 text-base font-light font-dm-sans mb-4">
                        Select your core courses. You can add up to 12 courses for your schedule.
                    </p>
                </div>

                {/* Semester Selection */}
                <div className="flex items-center space-x-8 mb-6 text-base font-light font-dm-sans text-gray-700">
                    <label className="flex items-center space-x-2 cursor-pointer">
                        <input
                            type="radio"
                            name="semester"
                            checked={selectedSemester === 'harmattan'}
                            onChange={() => setSelectedSemester('harmattan')}
                            className="option-input radio w-4 h-4 text-blue-800 focus:ring-blue-500 border-gray-300"
                        />
                        <span>Harmattan Semester – 1</span>
                    </label>
                    <label className="flex items-center space-x-2 cursor-pointer">
                        <input
                            type="radio"
                            name="semester"
                            checked={selectedSemester === 'rain'}
                            onChange={() => setSelectedSemester('rain')}
                            className="option-input radio w-4 h-4 text-blue-800 focus:ring-blue-500 border-gray-300"
                        />
                        <span>Rain Semester – 2</span>
                    </label>
                </div>

                {/* Info Bar */}
                <div className="flex items-center justify-between border-b-2 border-gray-200 pb-2 mb-4 text-base font-semibold font-dm-sans text-gray-600">
                    <span>Level: <span className="font-light font-dm-sans text-gray-500">{level || '300'}</span></span>
                    <span className="text-gray-500">Courses Selected: <span className="text-blue-600 font-bold">{selectedCourses.length}</span> of 12</span>
                </div>

                {/* Course List */}
                <div className="space-y-3 mb-6">
                    {INITIAL_COURSES.map((course, index) => {
                        const isSelected = selectedCourses.includes(course.id);
                        return (
                            <div key={course.id} className="grid grid-cols-12 gap-4 items-center py-3 border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors rounded-lg px-2">
                                <div className="col-span-1 text-gray-400 text-sm">{index + 1}</div>
                                <div className="col-span-2 text-base font-medium font-dm-sans text-gray-700">{course.code}</div>
                                <div className="col-span-6 text-base font-light font-dm-sans text-gray-500">{course.name}</div>
                                <div className="col-span-2 text-base text-gray-400 text-right">
                                    <span className="font-medium font-dm-sans text-gray-700">{course.credits}</span> <span className="font-light font-dm-sans">Credits</span>
                                </div>
                                <div className="col-span-1 flex justify-end">
                                    <button
                                        onClick={() => toggleCourse(course.id)}
                                        className="focus:outline-none transition-transform active:scale-90"
                                    >
                                        {isSelected ? (
                                            <div className="w-6 h-6 rounded-full bg-red-700 text-white flex items-center justify-center">
                                                <Minus size={14} strokeWidth={4} />
                                            </div>
                                        ) : (
                                            <div className="w-6 h-6 rounded-full bg-blue-900 text-white flex items-center justify-center">
                                                <Plus size={14} strokeWidth={4} />
                                            </div>
                                        )}
                                    </button>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Missing Something Section */}
                <div className="mb-6 pt-6 border-t-2 border-gray-100">
                    <h3 className="text-base font-medium font-dm-sans text-gray-900 mb-2">Missing something?</h3>
                    <p className="text-base font-light font-dm-sans text-gray-500 mb-4">If you have carryovers, electives, or special units not listed above, add them manually here.</p>

                    <div className="flex items-center space-x-3">
                        <span className="text-base font-medium font-dm-sans text-gray-600 w-auto shrink-0 mr-4">Additional Courses:</span>
                        <div className="flex-grow relative">
                            <input
                                type="text"
                                value={additionalCourse}
                                onChange={(e) => setAdditionalCourse(e.target.value)}
                                placeholder="e.g. NUN-SEN304 or Software Engineering Process"
                                className="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                            />
                        </div>
                        <button className="text-blue-800 hover:text-blue-900">
                            <div className="w-6 h-6 rounded-full bg-blue-800 text-white flex items-center justify-center">
                                <Plus size={14} strokeWidth={3} />
                            </div>
                        </button>
                    </div>
                </div>

                <div className="space-y-4 pt-6">
                    {error && (
                        <div className="flex items-center justify-center text-red-600 text-sm font-medium bg-red-50 p-3 rounded-lg border border-red-100">
                            <AlertCircle size={16} className="mr-2" />
                            {error}
                        </div>
                    )}
                    <button
                        onClick={handleContinue}
                        className="w-full flex items-center justify-center space-x-2 bg-blue-800 hover:bg-blue-900 text-white font-semibold py-3.5 rounded-lg shadow-sm transition-all transform active:scale-[0.99] text-sm"
                    >
                        <span>Continue</span>
                        <ArrowRight size={18} />
                    </button>
                </div>

            </main >
        </div >
    );
};

export default OnboardingStep2;

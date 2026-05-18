import React, { useState, useEffect } from 'react';
import { ArrowLeft, ArrowRight, Plus, Minus, AlertCircle, RefreshCw } from 'lucide-react';
import logo from '../assets/logo.png';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { api } from '../api/client';

interface Course {
    id: number; // Backend uses int ID
    code: string;
    name: string;
    credits: number;
    level: number;
    semester: number;
}

const OnboardingStep2: React.FC = () => {
    const navigate = useNavigate();
    const { level, step1Data, step2Data, setStep2Data, setSemester } = useUser();

    // Local State
    const [selectedSemester, setSelectedSemester] = useState<'harmattan' | 'rain'>(step2Data.selectedSemester || 'harmattan');
    const [selectedCourses, setSelectedCourses] = useState<string[]>(step2Data.selectedCourses || []);
    const [additionalCourse, setAdditionalCourse] = useState(step2Data.additionalCourse || '');
    const [error, setError] = useState<string>('');
    const [availableCourses, setAvailableCourses] = useState<Course[]>([]);
    const [loading, setLoading] = useState(false);
    const [allCourses, setAllCourses] = useState<Course[]>([]);
    const [carryoverError, setCarryoverError] = useState('');
    const [addedCarryovers, setAddedCarryovers] = useState<Course[]>([]);
    const [loadingCarryover, setLoadingCarryover] = useState(false);

    // Fix: Use step1Data.level (fresh form data) instead of legacy 'level' context
    const userLevel = parseInt(step1Data.level) || parseInt(level) || 100;

    // Fetch Courses from API
    useEffect(() => {
        const fetchCourses = async () => {
            setLoading(true);
            try {
                const semInt = selectedSemester === 'harmattan' ? 1 : 2;
                const courses = await api.get<Course[]>(`/courses/filter?level=${userLevel}&semester=${semInt}`);
                setAvailableCourses(courses);
            } catch (err) {
                console.error("Failed to fetch courses", err);
                setError("Failed to load courses. Please try refreshing.");
            } finally {
                setLoading(false);
            }
        };
        fetchCourses();
    }, [userLevel, selectedSemester]);

    // Fetch ALL courses from all levels for carryover validation
    useEffect(() => {
        const fetchAll = async () => {
            setLoadingCarryover(true);
            try {
                const semInt = selectedSemester === 'harmattan' ? 1 : 2;
                const levels = [100, 200, 300, 400, 500];
                const results = await Promise.all(
                    levels.map(lvl =>
                        api.get<Course[]>(`/courses/filter?level=${lvl}&semester=${semInt}`)
                            .catch(() => [] as Course[])
                    )
                );
                const map = new Map<number, Course>();
                results.flat().forEach(c => map.set(c.id, c));
                setAllCourses(Array.from(map.values()));
            } catch { /* silent */ } finally {
                setLoadingCarryover(false);
            }
        };
        fetchAll();
    }, [selectedSemester]);

    const normalise = (str: string) => str.trim().toLowerCase().replace(/\s+/g, '');

    const handleAddCarryover = () => {
        const input = normalise(additionalCourse);
        if (!input) return;
        setCarryoverError('');

        if (loadingCarryover) {
            setCarryoverError('Still loading course list. Please wait a moment.');
            return;
        }

        // Match by code OR name, case-insensitive, spaces ignored
        const match = allCourses.find(
            c => normalise(c.code) === input || normalise(c.name) === input
        );

        if (!match) {
            setCarryoverError(
                'Course not found. Enter a valid course code (e.g. SEN306) or full course name.'
            );
            return;
        }

        // Duplicate check by ID
        const alreadyAdded = selectedCourses.includes(String(match.id));
        if (alreadyAdded) {
            setCarryoverError('You have already added this course.');
            return;
        }

        // Course limit
        if (selectedCourses.length >= 12) {
            setCarryoverError('Maximum 12 courses allowed.');
            return;
        }

        setAddedCarryovers(prev => [...prev, match]);
        setSelectedCourses(prev => [...prev, String(match.id)]);
        setAdditionalCourse('');
        setCarryoverError('');
        if (error) setError('');
    };

    // Effect: Clear selections when Semester changes (Mutual Exclusivity)
    // Only if the selections don't match the new semester (handled by user action, but let's reinforce)
    const handleSemesterChange = (newSemester: 'harmattan' | 'rain') => {
        if (newSemester !== selectedSemester) {
            setSelectedSemester(newSemester);
            setSelectedCourses([]); // Clear selections on switch
            setError(''); // Clear errors
        }
    };

    const toggleCourse = (courseId: number) => {
        const strId = String(courseId); // Normalize to string for storage if needed, or stick to number? 
        // Context expects string[] for selectedCourses (from step2Data interface), but backend IDs are ints.
        // Let's use string for state to match context Interface.

        setSelectedCourses(prev => {
            if (prev.includes(strId)) {
                return prev.filter(id => id !== strId);
            } else {
                if (prev.length >= 12) {
                    setError('Maximum 12 courses allowed.');
                    return prev;
                }
                const newSelection = [...prev, strId];
                // Clear validation error if count reached (5)
                if (newSelection.length >= 5) setError('');
                return newSelection;
            }
        });
    };

    const handleContinue = () => {
        // Validation: Min 5
        if (selectedCourses.length < 5) {
            setError('Please select at least 5 courses to continue.');
            return;
        }

        // Save to Context (Atomic, deferred commit)
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
                        Select your core courses. You can select between 5 and 12 courses.
                    </p>
                </div>

                {/* Semester Selection (Radio) */}
                <div className="flex items-center space-x-8 mb-6 text-base font-light font-dm-sans text-gray-700 bg-gray-50 p-4 rounded-xl border border-gray-100">
                    <label className="flex items-center space-x-3 cursor-pointer group">
                        <input
                            type="radio"
                            name="semester"
                            checked={selectedSemester === 'harmattan'}
                            onChange={() => handleSemesterChange('harmattan')}
                            className="w-5 h-5 text-blue-800 focus:ring-blue-500 border-gray-300"
                        />
                        <span className={`group-hover:text-blue-800 transition-colors ${selectedSemester === 'harmattan' ? 'font-bold text-gray-900' : ''}`}>Harmattan Semester – 1</span>
                    </label>
                    <div className="h-6 w-px bg-gray-300"></div>
                    <label className="flex items-center space-x-3 cursor-pointer group">
                        <input
                            type="radio"
                            name="semester"
                            checked={selectedSemester === 'rain'}
                            onChange={() => handleSemesterChange('rain')}
                            className="w-5 h-5 text-blue-800 focus:ring-blue-500 border-gray-300"
                        />
                        <span className={`group-hover:text-blue-800 transition-colors ${selectedSemester === 'rain' ? 'font-bold text-gray-900' : ''}`}>Rain Semester – 2</span>
                    </label>
                </div>

                {/* Info Bar */}
                <div className="flex items-center justify-between border-b-2 border-gray-200 pb-2 mb-4 text-base font-semibold font-dm-sans text-gray-600">
                    <span>Level: <span className="font-bold text-blue-800">{userLevel}</span></span>
                    <span className="text-gray-500">Selected: <span className={`${selectedCourses.length < 5 ? 'text-orange-500' : 'text-green-600'} font-bold`}>{selectedCourses.length}</span> / 12</span>
                </div>

                {/* Course List */}
                <div className="space-y-3 mb-6">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                            <RefreshCw className="animate-spin mb-2" />
                            <p>Loading your curriculum...</p>
                        </div>
                    ) : availableCourses.length === 0 ? (
                        <div className="text-center py-10 text-gray-400">
                            No courses found for Level {userLevel} ({selectedSemester}).
                            <br /><span className="text-xs">Try switching semesters or check your level.</span>
                        </div>
                    ) : (
                        availableCourses.map((course, index) => {
                            const isSelected = selectedCourses.includes(String(course.id));
                            return (
                                <div key={course.id} className={`grid grid-cols-12 gap-4 items-center py-3 border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors rounded-lg px-2 ${isSelected ? 'bg-blue-50/50' : ''}`}>
                                    <div className="col-span-1 text-gray-400 text-sm">{index + 1}</div>
                                    <div className="col-span-2 text-base font-medium font-dm-sans text-gray-700">{course.code}</div>
                                    <div className="col-span-6 text-base font-light font-dm-sans text-gray-500">{course.name}</div>
                                    <div className="col-span-2 text-base text-gray-400 text-right">
                                        <span className="font-medium font-dm-sans text-gray-700">{course.credits}</span> Unit{course.credits !== 1 && 's'}
                                    </div>
                                    <div className="col-span-1 flex justify-end">
                                        <button
                                            onClick={() => toggleCourse(course.id)}
                                            className="focus:outline-none transition-transform active:scale-90"
                                        >
                                            {isSelected ? (
                                                <div className="w-6 h-6 rounded-full bg-red-700 text-white flex items-center justify-center shadow-sm">
                                                    <Minus size={14} strokeWidth={3} />
                                                </div>
                                            ) : (
                                                <div className="w-6 h-6 rounded-full bg-blue-900 text-white flex items-center justify-center shadow-sm hover:bg-blue-800">
                                                    <Plus size={14} strokeWidth={3} />
                                                </div>
                                            )}
                                        </button>
                                    </div>
                                </div>
                            );
                        })
                    )}
                </div>

                {/* Missing Something Section */}
                <div className="mb-6 pt-6 border-t-2 border-gray-100">
                    <h3 className="text-base font-medium font-dm-sans text-gray-900 mb-2">Missing something?</h3>
                    <p className="text-base font-light font-dm-sans text-gray-500 mb-4">If you have carryovers or electives, add them manually here.</p>

                    <div className="flex items-center space-x-3">
                        <span className="text-base font-medium font-dm-sans text-gray-600 w-auto shrink-0 mr-4">Add Course:</span>
                        <div className="flex-grow relative">
                            <input
                                type="text"
                                value={additionalCourse}
                                onChange={(e) => { setAdditionalCourse(e.target.value); setCarryoverError(''); }}
                                onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAddCarryover(); } }}
                                placeholder={loadingCarryover ? 'Loading courses…' : 'e.g. GNS101 or General Studies'}
                                disabled={loadingCarryover}
                                className={`w-full px-4 py-2.5 rounded-lg border focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm ${carryoverError ? 'border-red-400' : 'border-gray-300'} ${loadingCarryover ? 'bg-gray-50 text-gray-400' : ''}`}
                            />
                        </div>
                        <button
                            onClick={handleAddCarryover}
                            disabled={loadingCarryover}
                            className={`transition-colors ${loadingCarryover ? 'opacity-40 cursor-not-allowed' : ''}`}
                        >
                            <div className="w-8 h-8 rounded-full bg-blue-800 text-white flex items-center justify-center hover:bg-blue-900">
                                <Plus size={16} strokeWidth={3} />
                            </div>
                        </button>
                    </div>
                    {carryoverError && (
                        <p className="text-xs text-red-500 mt-2 flex items-center"><AlertCircle size={12} className="mr-1" />{carryoverError}</p>
                    )}
                    {addedCarryovers.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-3">
                            {addedCarryovers.map(c => (
                                <span key={c.id} className="inline-flex items-center bg-blue-50 text-blue-800 text-xs font-semibold px-3 py-1.5 rounded-full border border-blue-100">
                                    {c.code} — {c.name}
                                    <button onClick={() => {
                                        setAddedCarryovers(prev => prev.filter(x => x.id !== c.id));
                                        setSelectedCourses(prev => prev.filter(id => id !== String(c.id)));
                                    }} className="ml-2 text-blue-400 hover:text-red-500"><Minus size={12} /></button>
                                </span>
                            ))}
                        </div>
                    )}
                </div>

                <div className="space-y-4 pt-4">
                    {error && (
                        <div className="flex items-center justify-center text-red-600 text-sm font-medium bg-red-50 p-3 rounded-lg border border-red-100">
                            <AlertCircle size={16} className="mr-2" />
                            {error}
                        </div>
                    )}
                    <button
                        onClick={handleContinue}
                        disabled={selectedCourses.length < 5}
                        className={`w-full flex items-center justify-center space-x-2 font-semibold py-3.5 rounded-lg shadow-sm transition-all transform active:scale-[0.99] text-sm ${selectedCourses.length < 5 ? 'bg-gray-300 cursor-not-allowed text-gray-500' : 'bg-blue-800 hover:bg-blue-900 text-white'}`}
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

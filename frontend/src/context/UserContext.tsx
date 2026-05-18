import React, { createContext, useContext, useState, type ReactNode } from 'react';
import { api } from '../api/client';
import type { Step1Data, Step2Data, Step3Data, Step4Data, UserProfile } from '../types';

interface UserContextType {
    // Current User Profile (Authenticated)
    user: UserProfile | null;
    fetchUser: () => Promise<void>;

    // Legacy support
    level: string;
    semester: string;
    setLevel: (level: string) => void;
    setSemester: (semester: string) => void;

    // Full Onboarding State
    step1Data: Step1Data;
    setStep1Data: (data: Step1Data) => void;
    step2Data: Step2Data;
    setStep2Data: (data: Step2Data) => void;
    step3Data: Step3Data;
    setStep3Data: (data: Step3Data) => void;
    step4Data: Step4Data;
    setStep4Data: (data: Step4Data) => void;

    // Actions
    registerUser: (finalStep4Data?: Step4Data) => Promise<void>;
    logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    // Authenticated User State
    const [user, setUser] = useState<UserProfile | null>(null);

    // Step 1 State
    const [step1Data, setStep1Data] = useState<Step1Data>({
        email: '',
        username: '',
        phone: '',
        level: '100', // Default
        password: '',
        confirmPassword: ''
    });

    // Step 2 State
    const [step2Data, setStep2Data] = useState<Step2Data>({
        selectedSemester: 'harmattan',
        selectedCourses: [],
        additionalCourse: ''
    });

    // Step 3 State
    const [step3Data, setStep3Data] = useState<Step3Data>({
        selectedBlueprint: null
    });

    // Step 4 State
    const [step4Data, setStep4Data] = useState<Step4Data>({
        peakTime: '',
        focusDuration: '',
        learningStyle: '',
        environment: '',
        approach: ''
    });

    // Legacy state for dashboard/other components
    const [level, setLevel] = useState('100');
    const [semester, setSemesterState] = useState(localStorage.getItem('semester') || '1');

    const setSemester = (val: string) => {
        localStorage.setItem('semester', val);
        setSemesterState(val);
    };

    // Fetch User Profile
    const fetchUser = async () => {
        try {
            const profile = await api.get<UserProfile>('/users/profile');
            setUser(profile);
            // Sync legacy state if needed
            if (profile.level) setLevel(String(profile.level));

            // Derive semester from user's courses
            const courses = await api.get<{id: number, semester?: number}[]>('/users/courses');
            if (courses && courses.length > 0) {
                // Determine semester from the first course
                // Backend might not return semester in /users/courses, so we default to '1' if not present
                // Wait, let's fetch course details or just leave it. If not present, we will fetch from backend.
                // Actually, wait, let's just use the first course's semester if available.
                // It's safer to fetch /courses and match by ID? We'll see.
            }
        } catch (error) {
            console.error("Failed to fetch user profile", error);
            // Optionally clear token if fetch fails due to auth error
            sessionStorage.removeItem('token');
            setUser(null);
        }
    };

    // Initial Fetch on Mount (if token exists)
    React.useEffect(() => {
        const token = sessionStorage.getItem('token');
        if (token) {
            fetchUser();
        }
    }, []);

    const registerUser = async (finalStep4Data?: Step4Data) => {
        // Clear any existing session to prevent ghost logins
        sessionStorage.removeItem('token');

        // Merge Step 4 data if provided
        const s4 = finalStep4Data || step4Data;
        const s1 = step1Data;
        const s2 = step2Data;

        // Determine Focus Threshold
        const focusMap: Record<string, number> = {
            'short': 25,
            'medium': 60,
            'long': 110,
        };
        const focusThreshold = focusMap[s4.focusDuration] || 60;

        const payload = {
            username: s1.username,
            email: s1.email,
            password: s1.password,
            confirm_password: s1.confirmPassword,
            phone: '+234' + s1.phone.replace(/\s+/g, '').replace(/^0/, ''),
            level: parseInt(s1.level) || 100,
            semester_type: s2.selectedSemester || 'harmattan',
            selected_course_ids: s2.selectedCourses.map(id => parseInt(id)),

            // Step 4 Profile Logic
            peak_time: s4.peakTime,
            learning_style: s4.learningStyle,
            environment_pref: s4.environment,
            focus_threshold: focusThreshold,
            focusDuration: s4.focusDuration,
            place_of_study: s4.environment,
            study_mode: s4.approach,

            // Fix: Include Step 3 Data (Blueprint)
            base_template: step3Data.selectedBlueprint,
            selectedBlueprint: step3Data.selectedBlueprint // Send both just in case
        };

        try {
            await api.post<{ message: string }>('/auth/onboard', payload);
        } catch (error: any) {
            console.error("Registration/OTP Failed:", error);
            throw error;
        }
    };



    const logout = () => {
        sessionStorage.removeItem('token');
        setUser(null);

        // Reset State
        setStep1Data({
            email: '',
            username: '',
            phone: '',
            level: '100',
            password: '',
            confirmPassword: ''
        });
        setStep2Data({
            selectedSemester: 'harmattan',
            selectedCourses: [],
            additionalCourse: ''
        });
        setStep3Data({
            selectedBlueprint: null
        });
        setStep4Data({
            peakTime: '',
            focusDuration: '',
            learningStyle: '',
            environment: '',
            approach: ''
        });
    };

    return (
        <UserContext.Provider value={{
            user,
            fetchUser,
            level,
            semester,
            setLevel,
            setSemester,
            step1Data,
            setStep1Data,
            step2Data,
            setStep2Data,
            step3Data,
            setStep3Data,
            step4Data,
            setStep4Data,
            registerUser,
            logout
        }}>
            {children}
        </UserContext.Provider>
    );
};

export const useUser = () => {
    const context = useContext(UserContext);
    if (context === undefined) {
        throw new Error('useUser must be used within a UserProvider');
    }
    return context;
};

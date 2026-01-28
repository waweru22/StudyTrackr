import React, { createContext, useContext, useState, type ReactNode } from 'react';

// Step 1 Data
interface Step1Data {
    email: string;
    phone: string;
    level: string;
    password: string;
    confirmPassword: string;
}

// Step 2 Data
interface Step2Data {
    selectedSemester: 'harmattan' | 'rain';
    selectedCourses: string[];
    additionalCourse: string;
}

// Step 3 Data
interface Step3Data {
    selectedBlueprint: string | null;
}

// Step 4 Data
interface Step4Data {
    peakTime: string;
    focusDuration: string;
    learningStyle: string;
    environment: string;
    approach: string;
}

interface UserContextType {
    // Legacy support (to avoid breaking Dashboard immediately, though I'll sync them)
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
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    // Step 1 State
    const [step1Data, setStep1Data] = useState<Step1Data>({
        email: '',
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

    // Derived setters for compatibility (syncing with new state structure if needed, or just allow independent update)
    // Actually, `level` is part of Step 1. `semester` is part of Step 2 (derived from 'harmattan'/'rain').
    // Let's implement setLevel and setSemester to update the respective Step data to keep sync.
    const setLevel = (lvl: string) => setStep1Data(prev => ({ ...prev, level: lvl }));

    // setSemester in Dashboard/Onboarding was accepting string '1 (Harmattan)'. 
    // Step2Data uses 'harmattan' | 'rain'.
    // I need to map if I want to keep full compatibility, or just store the string in Step 2.
    // The previous implementation of setSemester passed '1 (Harmattan)'.
    // Let's rely on Step2Data logic mainly. Use a separate state for semantic semester string if needed, or derive it.
    // Dashboard users `semester` string.
    const [dashboardSemester, setDashboardSemester] = useState('1 (Harmattan)');

    const setSemester = (sem: string) => {
        setDashboardSemester(sem);
        // Also try to sync step 2 if possible? 
        if (sem.includes('Harmattan')) setStep2Data(prev => ({ ...prev, selectedSemester: 'harmattan' }));
        if (sem.includes('Rain')) setStep2Data(prev => ({ ...prev, selectedSemester: 'rain' }));
    };

    return (
        <UserContext.Provider value={{
            level: step1Data.level,
            semester: dashboardSemester, // Use the string version for Dashboard
            setLevel,
            setSemester,
            step1Data,
            setStep1Data,
            step2Data,
            setStep2Data,
            step3Data,
            setStep3Data,
            step4Data,
            setStep4Data
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

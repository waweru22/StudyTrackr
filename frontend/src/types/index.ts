export interface Step1Data {
    email: string;
    username: string;
    phone: string;
    level: string;
    password: string;
    confirmPassword: string;
}

export interface Step2Data {
    selectedSemester: 'harmattan' | 'rain';
    selectedCourses: string[];
    additionalCourse: string;
}

export interface Step3Data {
    selectedBlueprint: string | null;
}

export interface Step4Data {
    peakTime: string;
    focusDuration: string;
    learningStyle: string;
    environment: string;
    approach: string;
}

export interface FeedItem {
    id: number;
    type: 'alert' | 'broadcast' | 'tip';
    message: string;
    timestamp: string;
    priority?: string;
    title?: string;
}

// Schedule Types
export interface SessionBlock {
    id: number;
    course_code: string;
    course_title: string;
    start_time: string;
    end_time: string;
    block_type: string;
    color_theme: string;
    status?: 'pending' | 'completed' | 'missed' | 'active';
    technique_name?: string;
    technique_details?: string;
    refinement_reason?: string;
    academic_citation?: string;
    duration_minutes: number;
    suggested_environment?: string;
    suggested_social_setting?: string;
    suggested_medium?: string;
}

export interface WeeklyBlock {
    id: number;
    course_code: string;
    start_time: string;
    technique_name?: string;
    color_theme?: string;
    end_time?: string;
}

export interface ScheduleData {
    today_blocks: SessionBlock[];
    weekly_summary: Record<string, WeeklyBlock[]>;
}

export interface DashboardData {
    feed: FeedItem[];
    streak: number;
    badge: string;
    xp: number;
    quote?: {
        text: string;
        author: string;
    };
    user?: {
        username: string;
        level: number;
    };
    next_session?: {
        id: number | null;
        course: string;
        course_title: string;
        time: string;
        technique: string;
        technique_details: string;
        duration_minutes: number;
        status: string;
    };
}

export interface UserProfile {
    id: number;
    username: string;
    email: string;
    level: number;
    xp_points: number;
    badge: string;
    streak_count: number;
    base_template?: string;
}

export interface Material {
    id: number;
    title: string;
    url: string;
    type: 'video' | 'article' | 'journal' | 'textbook';
    tag?: string;
    difficulty?: number;
}

export interface EnrolledCourse {
    id: number;
    code: string;
    name: string;
    level: number;
    weight: number;
    credits: number;
}

export interface SearchResult {
    title: string;
    url: string;
    type: 'video' | 'textbook';
    learning_style_tag: string;
}

export interface SavedResource {
    id: number;
    title: string;
    url: string;
    type: string;
    saved_at: string;
}

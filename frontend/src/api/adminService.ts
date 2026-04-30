import { api } from './client';
import type {
    AdminDashboardData,
    AdminCourse,
    CourseAnalyticsItem,
    TechniqueItem,
    UnverifiedStudent,
    BroadcastRecord
} from '../types';

// ─── Auth ───────────────────────────────────────────────────────

export const adminAuth = {
    register: (data: { email: string; password: string; confirm_password: string; staff_id: string; admin_key: string; username?: string }) =>
        api.post<{ access_token: string; user: any; message: string }>('/auth/admin/register', data),

    login: (data: { email: string; password: string }) =>
        api.post<{ access_token: string; user: any; message: string }>('/auth/admin/login', data),
};

// ─── Dashboard ──────────────────────────────────────────────────

export const adminDashboard = {
    getMetrics: (weeks = 1) =>
        api.get<AdminDashboardData>(`/admin/dashboard?weeks=${weeks}`),
};

// ─── Courses ────────────────────────────────────────────────────

export const adminCourses = {
    list: () => api.get<AdminCourse[]>('/admin/courses'),

    create: (data: { code: string; name: string; level: number; semester: number; credits: number; weight: number }) =>
        api.post<{ message: string; course: AdminCourse }>('/admin/courses', data),

    update: (id: number, data: Partial<AdminCourse>) =>
        api.patch<{ message: string }>(`/admin/courses/${id}`, data),

    remove: (id: number) =>
        api.delete<{ message: string }>(`/admin/courses/${id}`),
};

// ─── Verification ───────────────────────────────────────────────

export const adminVerification = {
    listUnverified: () => api.get<UnverifiedStudent[]>('/admin/verification'),

    approve: (studentId: number) =>
        api.post<{ message: string }>(`/admin/verification/${studentId}/approve`, {}),

    reject: (studentId: number) =>
        api.post<{ message: string }>(`/admin/verification/${studentId}/reject`, {}),
};

// ─── Analytics ──────────────────────────────────────────────────

export const adminAnalytics = {
    courses: (params?: { level?: number; weeks?: number }) => {
        const query = new URLSearchParams();
        if (params?.level) query.set('level', String(params.level));
        if (params?.weeks) query.set('weeks', String(params.weeks));
        const qs = query.toString();
        return api.get<CourseAnalyticsItem[]>(`/admin/analytics/courses${qs ? '?' + qs : ''}`);
    },

    techniques: () => api.get<TechniqueItem[]>('/admin/analytics/techniques'),
};

// ─── Broadcast ──────────────────────────────────────────────────

export const adminBroadcast = {
    send: (data: { title: string; message: string; target_level?: number | null }) =>
        api.post<{ message: string; broadcast_id: number; notifications_created: number }>('/admin/broadcast', data),

    history: () => api.get<BroadcastRecord[]>('/admin/broadcasts'),
};

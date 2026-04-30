import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useUser } from '../context/UserContext';

const AdminRoute: React.FC = () => {
    const token = sessionStorage.getItem('token');
    const { user } = useUser();

    if (!token) {
        return <Navigate to="/admin/login" replace />;
    }

    // While user profile is loading, show nothing (avoid flash)
    if (!user) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-900">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
            </div>
        );
    }

    if (user.role !== 'admin') {
        return <Navigate to="/dashboard" replace />;
    }

    return <Outlet />;
};

export default AdminRoute;

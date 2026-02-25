import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

const ProtectedRoute: React.FC = () => {
    // Check local storage directly for token to avoid flash if context is loading
    const token = sessionStorage.getItem('token');

    // If no token, redirect to login
    if (!token) {
        return <Navigate to="/login" replace />;
    }

    return <Outlet />;
};

export default ProtectedRoute;

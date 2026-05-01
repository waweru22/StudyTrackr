import React, { useState } from 'react';
import { ArrowRight, AlertCircle, Eye, EyeOff } from 'lucide-react';
import logo from '../assets/logo.png';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useUser } from '../context/UserContext';
import type { UserProfile } from '../types';

const Login: React.FC = () => {
    const navigate = useNavigate();
    const { fetchUser } = useUser();
    const [identifier, setIdentifier] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // Try student login first
            const response = await api.post<{ access_token: string, message: string }>('/auth/login', {
                identifier,
                password
            });

            if (response.access_token) {
                sessionStorage.setItem('token', response.access_token);
                await fetchUser();
                // Check role and redirect accordingly
                const profile = await api.get<UserProfile>('/users/profile');
                navigate(profile.role === 'admin' ? '/admin/dashboard' : '/dashboard');
                return;
            }
        } catch {
            // Student login failed — try admin login
            try {
                const adminResponse = await api.post<{ access_token: string, message: string }>('/auth/admin/login', {
                    email: identifier,
                    password
                });

                if (adminResponse.access_token) {
                    sessionStorage.setItem('token', adminResponse.access_token);
                    await fetchUser();
                    navigate('/admin/dashboard');
                    return;
                }
            } catch (adminErr: any) {
                console.error("Login failed", adminErr);
                setError(adminErr.message || "Invalid credentials.");
                setLoading(false);
                return;
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-white font-sans text-gray-900 flex flex-col items-center justify-center">
            {/* Header/Logo */}
            <div className="mb-8">
                <img src={logo} alt="StudyTrackr Logo" className="h-12 w-auto" />
            </div>

            {/* Main Content */}
            <main className="w-full max-w-md px-6">
                <div className="space-y-2 mb-8 text-center">
                    <h2 className="text-3xl font-bold font-dm-sans text-gray-900">Welcome Back</h2>
                    <p className="text-gray-500 text-base font-light font-dm-sans">
                        Sign in to continue your learning journey.
                    </p>
                </div>

                {/* Form */}
                <form className="space-y-6" onSubmit={handleLogin}>
                    {/* Identifier */}
                    <div className="space-y-1.5">
                        <label className="block text-sm font-medium font-dm-sans text-gray-700">
                            Username or Email
                        </label>
                        <input
                            type="text"
                            value={identifier}
                            onChange={(e) => setIdentifier(e.target.value)}
                            required
                            placeholder="e.g. waweru22 or name@email.com"
                            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-400 text-sm transition-shadow shadow-sm"
                        />
                    </div>

                    {/* Password */}
                    <div className="space-y-1.5">
                        <label className="block text-sm font-medium font-dm-sans text-gray-700">
                            Password
                        </label>
                        <div className="relative">
                            <input
                                type={showPassword ? "text" : "password"}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow shadow-sm pr-10"
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute inset-y-0 right-0 flex items-center px-3 text-gray-500 hover:text-gray-700 focus:outline-none"
                            >
                                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>
                        </div>
                    </div>

                    {error && (
                        <div className="flex items-center text-red-600 text-sm font-medium bg-red-50 p-3 rounded-lg border border-red-100">
                            <AlertCircle size={16} className="mr-2" />
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full flex items-center justify-center space-x-2 font-semibold py-3.5 rounded-lg shadow-sm transition-all transform active:scale-[0.99] text-sm text-white ${loading ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-800 hover:bg-blue-900'}`}
                    >
                        {loading ? 'Signing in...' : 'Log In'}
                        {!loading && <ArrowRight size={18} />}
                    </button>
                </form>

                <div className="mt-8 text-center">
                    <p className="text-sm text-gray-500">
                        Don't have an account?{' '}
                        <Link to="/onboarding" className="font-semibold text-blue-600 hover:text-blue-800 transition-colors">
                            Sign Up
                        </Link>
                    </p>
                </div>
            </main>
        </div>
    );
};

export default Login;

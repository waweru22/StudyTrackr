import React, { useState } from 'react';
import { ArrowRight, AlertCircle, Eye, EyeOff } from 'lucide-react';
import logo from '../assets/logo.png';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';

const Login: React.FC = () => {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await api.post<{ access_token: string, message: string }>('/auth/login', {
                email,
                password
            });

            // Store token
            if (response.access_token) {
                localStorage.setItem('token', response.access_token);
                // navigate to dashboard
                navigate('/dashboard');
            }
        } catch (err: any) {
            console.error("Login failed", err);
            setError(err.response?.data?.error || "Invalid email or password.");
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
                    {/* Email */}
                    <div className="space-y-1.5">
                        <label className="block text-sm font-medium font-dm-sans text-gray-700">
                            Email address
                        </label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            placeholder="e.g. name@nileuniversity.edu.ng"
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

                    <div className="pt-2">
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full flex items-center justify-center space-x-2 bg-blue-800 hover:bg-blue-900 text-white font-semibold font-dm-sans text-base py-3.5 rounded-lg shadow-sm transition-all transform active:scale-[0.99] disabled:opacity-70 disabled:cursor-not-allowed"
                        >
                            {loading ? (
                                <span>Signing In...</span>
                            ) : (
                                <>
                                    <span>Sign In</span>
                                    <ArrowRight size={18} />
                                </>
                            )}
                        </button>
                    </div>
                </form>

                <p className="mt-8 text-center text-sm font-light font-dm-sans text-gray-500">
                    Don't have an account? <Link to="/onboarding" className="text-blue-700 font-medium font-dm-sans hover:underline">Create Account</Link>
                </p>
            </main>
        </div>
    );
};

export default Login;

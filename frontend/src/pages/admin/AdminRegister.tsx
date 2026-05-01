import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Shield, Eye, EyeOff, AlertCircle, ArrowRight, GraduationCap, ArrowLeft } from 'lucide-react';
import { adminAuth } from '../../api/adminService';
import { useUser } from '../../context/UserContext';

const AdminRegister: React.FC = () => {
    const navigate = useNavigate();
    const { fetchUser } = useUser();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Register fields
    const [email, setEmail] = useState('');
    const [staffId, setStaffId] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [adminKey, setAdminKey] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [showAdminKey, setShowAdminKey] = useState(false);

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            setLoading(false);
            return;
        }

        try {
            const res = await adminAuth.register({
                email,
                password,
                confirm_password: confirmPassword,
                staff_id: staffId,
                admin_key: adminKey,
                username: username || staffId,
            });
            if (res.access_token) {
                sessionStorage.setItem('token', res.access_token);
                await fetchUser();
                navigate('/admin/dashboard');
            }
        } catch (err: any) {
            setError(err.message || 'Registration failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center px-4 py-12">
            {/* Decorative background */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl"></div>
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl"></div>
            </div>

            <div className="relative w-full max-w-md">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-600/20 border border-blue-500/30 mb-4">
                        <Shield size={32} className="text-blue-400" />
                    </div>
                    <h1 className="text-2xl font-bold text-white">Create Admin Account</h1>
                    <p className="text-sm text-slate-400 mt-1">University Administration Portal</p>
                </div>

                {/* Role Toggle — I'm a Student / I'm an Administrator */}
                <div className="flex bg-slate-800/50 rounded-xl p-1 mb-6 border border-slate-700/50">
                    <button
                        onClick={() => navigate('/onboarding')}
                        className="flex-1 flex items-center justify-center space-x-2 py-2.5 rounded-lg text-sm font-semibold transition-all text-slate-400 hover:text-slate-300"
                    >
                        <GraduationCap size={16} />
                        <span>I'm a Student</span>
                    </button>
                    <button
                        className="flex-1 flex items-center justify-center space-x-2 py-2.5 rounded-lg text-sm font-semibold transition-all bg-blue-600 text-white shadow-lg shadow-blue-500/25"
                    >
                        <Shield size={16} />
                        <span>I'm an Administrator</span>
                    </button>
                </div>

                {/* Form Card */}
                <div className="bg-slate-800/60 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-8 shadow-2xl">
                    <form onSubmit={handleRegister} className="space-y-5">
                        {/* Email */}
                        <div>
                            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Email</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                placeholder="admin@nileuni.edu.ng"
                                className="w-full px-4 py-3 rounded-xl bg-slate-700/50 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-sm transition-all"
                            />
                        </div>

                        {/* Staff ID */}
                        <div>
                            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Staff ID</label>
                            <input
                                type="text"
                                value={staffId}
                                onChange={(e) => setStaffId(e.target.value)}
                                required
                                placeholder="e.g. STF-2024-001"
                                className="w-full px-4 py-3 rounded-xl bg-slate-700/50 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-sm transition-all"
                            />
                        </div>

                        {/* Username */}
                        <div>
                            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Username</label>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                placeholder="Display name (optional, defaults to Staff ID)"
                                className="w-full px-4 py-3 rounded-xl bg-slate-700/50 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-sm transition-all"
                            />
                        </div>

                        {/* Password */}
                        <div>
                            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Password</label>
                            <div className="relative">
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    className="w-full px-4 py-3 rounded-xl bg-slate-700/50 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-sm transition-all pr-10"
                                />
                                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute inset-y-0 right-0 flex items-center px-3 text-slate-400 hover:text-slate-300">
                                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                </button>
                            </div>
                        </div>

                        {/* Confirm Password */}
                        <div>
                            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Confirm Password</label>
                            <input
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                                className="w-full px-4 py-3 rounded-xl bg-slate-700/50 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-sm transition-all"
                            />
                        </div>

                        {/* Admin Key */}
                        <div>
                            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                                Admin Key <span className="text-red-400">*</span>
                            </label>
                            <div className="relative">
                                <input
                                    type={showAdminKey ? 'text' : 'password'}
                                    value={adminKey}
                                    onChange={(e) => setAdminKey(e.target.value)}
                                    required
                                    placeholder="Contact your department head for the admin key"
                                    className="w-full px-4 py-3 rounded-xl bg-slate-700/50 border border-amber-500/30 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500/50 text-sm transition-all pr-10"
                                />
                                <button type="button" onClick={() => setShowAdminKey(!showAdminKey)} className="absolute inset-y-0 right-0 flex items-center px-3 text-slate-400 hover:text-slate-300">
                                    {showAdminKey ? <EyeOff size={18} /> : <Eye size={18} />}
                                </button>
                            </div>
                            <p className="text-[11px] text-amber-400/70 mt-1.5 flex items-center">
                                <Shield size={12} className="mr-1" />
                                Required for security verification
                            </p>
                        </div>

                        {/* Error */}
                        {error && (
                            <div className="flex items-center text-red-300 text-sm bg-red-500/10 border border-red-500/20 p-3 rounded-xl">
                                <AlertCircle size={16} className="mr-2 flex-shrink-0" />
                                {error}
                            </div>
                        )}

                        {/* Submit */}
                        <button
                            type="submit"
                            disabled={loading}
                            className={`w-full flex items-center justify-center space-x-2 font-bold py-3.5 rounded-xl text-sm transition-all ${loading
                                ? 'bg-blue-600/50 cursor-not-allowed text-blue-200'
                                : 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 active:scale-[0.98]'
                                }`}
                        >
                            <span>{loading ? 'Registering...' : 'Create Admin Account'}</span>
                            {!loading && <ArrowRight size={18} />}
                        </button>
                    </form>
                </div>

                {/* Footer */}
                <div className="mt-6 text-center space-y-2">
                    <Link to="/login" className="text-xs text-slate-500 hover:text-slate-400 transition-colors block">
                        Already have an account? Sign in
                    </Link>
                    {/* <Link to="/login" className="text-xs text-slate-500 hover:text-slate-400 transition-colors flex items-center justify-center">
                        <ArrowLeft size={12} className="mr-1" />
                        Back to Student Login
                    </Link> */}
                </div>
            </div>
        </div>
    );
};

export default AdminRegister;

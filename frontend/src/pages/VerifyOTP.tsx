import React, { useState, useEffect } from 'react';
import { ArrowRight, AlertCircle, RefreshCw } from 'lucide-react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import logo from '../assets/logo.png';
import { useUser } from '../context/UserContext';
import { api } from '../api/client';

const VerifyOTP: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { verifyUserOtp } = useUser();

    // Email passed from Onboarding
    const email = location.state?.email || '';

    const [otp, setOtp] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [resendLoading, setResendLoading] = useState(false);
    const [resendMessage, setResendMessage] = useState('');

    useEffect(() => {
        if (!email) {
            // If accessed directly without state, redirect to login
            navigate('/login');
        }
    }, [email, navigate]);

    const handleVerify = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            if (otp.length !== 6) {
                throw new Error("Please enter a valid 6-digit code.");
            }

            await verifyUserOtp(email, otp);
            // On success, token is stored by context
            navigate('/dashboard');
        } catch (err: any) {
            console.error("Verification failed", err);
            setError(err.response?.data?.message || err.message || "Invalid OTP code.");
        } finally {
            setLoading(false);
        }
    };

    const handleResend = async () => {
        setResendLoading(true);
        setResendMessage('');
        setError('');
        try {
            await api.post('/auth/resend-otp', { email });
            setResendMessage("New code sent! Check your inbox.");
        } catch (err: any) {
            setError("Failed to resend OTP. Try again.");
        } finally {
            setResendLoading(false);
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
                    <h2 className="text-3xl font-bold font-dm-sans text-gray-900">Verify Your Email</h2>
                    <p className="text-gray-500 text-base font-light font-dm-sans">
                        We've sent a 6-digit code to <span className="font-medium text-gray-800">{email}</span>
                    </p>
                </div>

                {/* Form */}
                <form className="space-y-8" onSubmit={handleVerify}>
                    {/* OTP 6-Box Input */}
                    <div className="space-y-2">
                        <label className="block text-sm font-medium font-dm-sans text-gray-700 text-center mb-4">
                            Enter Verification Code
                        </label>
                        <div className="relative w-full max-w-[320px] mx-auto h-14">
                            {/* Visual Boxes */}
                            <div className="absolute inset-0 flex justify-between pointer-events-none">
                                {[0, 1, 2, 3, 4, 5].map((idx) => (
                                    <div
                                        key={idx}
                                        className={`w-12 h-14 border-2 rounded-lg flex items-center justify-center text-2xl font-bold font-dm-sans transition-all
                                            ${otp.length === idx ? 'border-blue-600 ring-4 ring-blue-50/50 z-10' : 'border-gray-200'}
                                            ${otp[idx] ? 'bg-white text-gray-900 border-gray-300' : 'bg-gray-50 text-gray-400'}
                                        `}
                                    >
                                        {otp[idx] || ''}
                                    </div>
                                ))}
                            </div>
                            {/* Actual Hidden Input */}
                            <input
                                type="text"
                                inputMode="numeric"
                                maxLength={6}
                                value={otp}
                                onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                                className="absolute inset-0 w-full h-full opacity-0 cursor-text font-mono tracking-widest"
                                autoFocus
                                required
                            />
                        </div>
                    </div>

                    {error && (
                        <div className="flex items-center text-red-600 text-sm font-medium bg-red-50 p-3 rounded-lg border border-red-100 justify-center">
                            <AlertCircle size={16} className="mr-2" />
                            {error}
                        </div>
                    )}

                    {resendMessage && (
                        <div className="flex items-center text-green-600 text-sm font-medium bg-green-50 p-3 rounded-lg border border-green-100 justify-center">
                            {resendMessage}
                        </div>
                    )}

                    <div className="pt-2">
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full flex items-center justify-center space-x-2 bg-blue-800 hover:bg-blue-900 text-white font-semibold font-dm-sans text-base py-3.5 rounded-lg shadow-sm transition-all transform active:scale-[0.99] disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none"
                        >
                            {loading ? (
                                <span>Verifying...</span>
                            ) : (
                                <>
                                    <span>Verify & Generate Schedule</span>
                                    <ArrowRight size={18} />
                                </>
                            )}
                        </button>
                    </div>
                </form>

                <div className="mt-6 text-center">
                    <button
                        onClick={handleResend}
                        disabled={resendLoading}
                        className="text-sm font-medium text-gray-500 hover:text-blue-700 flex items-center justify-center mx-auto space-x-1"
                    >
                        {resendLoading ? <RefreshCw className="animate-spin h-3 w-3" /> : null}
                        <span>Didn't receive code? Resend</span>
                    </button>
                </div>

                <p className="mt-8 text-center text-sm font-light font-dm-sans text-gray-400">
                    <Link to="/login" className="hover:text-blue-700">Back to Login</Link>
                </p>
            </main>
        </div>
    );
};

export default VerifyOTP;

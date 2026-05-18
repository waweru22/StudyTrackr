import React, { useState, useEffect } from 'react';
import { RefreshCw, Mail, AlertCircle } from 'lucide-react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import logo from '../assets/logo.png';
import { api } from '../api/client';

const CheckEmail: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();

    // Email passed from OnboardingStep4
    const email = location.state?.email || '';

    const [resendLoading, setResendLoading] = useState(false);
    const [resendMessage, setResendMessage] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        if (!email) {
            navigate('/login');
        }
    }, [email, navigate]);

    const handleResend = async () => {
        setResendLoading(true);
        setResendMessage('');
        setError('');
        try {
            await api.post('/auth/resend-verification', { email });
            setResendMessage("New verification link sent! Check your inbox.");
        } catch (err: any) {
            setError("Failed to resend verification email. Try again.");
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
                <div className="space-y-4 mb-8 text-center">
                    <div className="mx-auto w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mb-4">
                        <Mail size={32} className="text-blue-700" />
                    </div>
                    <h2 className="text-3xl font-bold font-dm-sans text-gray-900">Verify your email</h2>
                    <p className="text-gray-500 text-base font-light font-dm-sans">
                        We sent a verification link to{' '}
                        <span className="font-medium text-gray-800">{email}</span>
                    </p>
                    <p className="text-gray-500 text-base font-light font-dm-sans">
                        Click the link in the email to activate your account.
                    </p>
                </div>

                <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 text-center mb-6">
                    <p className="text-sm text-blue-700 font-medium">
                        Link expires in 24 hours
                    </p>
                </div>

                {error && (
                    <div className="flex items-center text-red-600 text-sm font-medium bg-red-50 p-3 rounded-lg border border-red-100 justify-center mb-4">
                        <AlertCircle size={16} className="mr-2" />
                        {error}
                    </div>
                )}

                {resendMessage && (
                    <div className="flex items-center text-green-600 text-sm font-medium bg-green-50 p-3 rounded-lg border border-green-100 justify-center mb-4">
                        {resendMessage}
                    </div>
                )}

                <div className="text-center">
                    <button
                        onClick={handleResend}
                        disabled={resendLoading}
                        className="text-sm font-medium text-gray-500 hover:text-blue-700 flex items-center justify-center mx-auto space-x-1"
                    >
                        {resendLoading ? <RefreshCw className="animate-spin h-3 w-3 mr-1" /> : null}
                        <span>Didn't receive it? Resend verification email</span>
                    </button>
                </div>

                <p className="mt-8 text-center text-sm font-light font-dm-sans text-gray-400">
                    <Link to="/login" className="hover:text-blue-700">Back to Login</Link>
                </p>
            </main>
        </div>
    );
};

export default CheckEmail;

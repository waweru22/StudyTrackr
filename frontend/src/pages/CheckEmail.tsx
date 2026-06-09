import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Mail, ArrowLeft, RefreshCw } from 'lucide-react';
import logo from '../assets/logo.png';
import { api } from '../api/client';

const CheckEmail: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const email: string = (location.state as any)?.email || '';
    const [resent, setResent] = React.useState(false);
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState('');

    const handleResend = async () => {
        if (!email) return;
        setLoading(true);
        setError('');
        try {
            await api.post('/auth/resend-verification', { email });
            setResent(true);
        } catch (e: any) {
            setError(e?.response?.data?.error || 'Failed to resend. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-white flex flex-col items-center font-sans">
            {/* Header */}
            <header className="w-full max-w-5xl mx-auto px-6 py-6 flex items-center justify-between">
                <img src={logo} alt="StudyTrackr Logo" className="h-10 w-auto" />
                <button
                    onClick={() => navigate('/onboarding')}
                    className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                    <ArrowLeft size={16} />
                    <span>Back to sign up</span>
                </button>
            </header>

            {/* Card */}
            <main className="flex-grow flex items-center justify-center px-6 pb-16">
                <div className="w-full max-w-md text-center space-y-6">

                    {/* Icon */}
                    <div className="flex justify-center">
                        <div className="w-20 h-20 rounded-full bg-blue-50 flex items-center justify-center">
                            <Mail size={40} className="text-blue-800" />
                        </div>
                    </div>

                    {/* Heading */}
                    <div className="space-y-2">
                        <h1 className="text-2xl font-bold font-dm-sans text-gray-900">Check your email</h1>
                        <p className="text-gray-500 text-sm font-dm-sans leading-relaxed">
                            We sent a verification link to{' '}
                            {email
                                ? <span className="font-semibold text-gray-800">{email}</span>
                                : 'your email address'
                            }.
                            <br />
                            Click it to activate your account.
                        </p>
                    </div>

                    {/* Steps */}
                    <div className="bg-gray-50 rounded-xl p-5 text-left space-y-3">
                        {[
                            'Open your Nile University student email',
                            'Find the email from StudyTrackr',
                            'Click the "Verify my email" button',
                        ].map((step, i) => (
                            <div key={i} className="flex items-start gap-3">
                                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-800 text-white text-xs font-bold flex items-center justify-center mt-0.5">
                                    {i + 1}
                                </span>
                                <p className="text-sm text-gray-600 font-dm-sans">{step}</p>
                            </div>
                        ))}
                    </div>

                    {/* Resend */}
                    <div className="space-y-2">
                        {resent ? (
                            <p className="text-sm text-green-600 font-medium">
                                ✓ Verification email resent!
                            </p>
                        ) : (
                            <>
                                <p className="text-xs text-gray-400">Didn't receive it? Check your spam folder, or</p>
                                <button
                                    onClick={handleResend}
                                    disabled={loading}
                                    className="inline-flex items-center gap-2 text-sm font-semibold text-blue-800 hover:text-blue-900 disabled:opacity-50 transition-colors"
                                >
                                    <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
                                    {loading ? 'Sending...' : 'Resend verification email'}
                                </button>
                            </>
                        )}
                        {error && <p className="text-xs text-red-500">{error}</p>}
                    </div>

                    {/* Login link */}
                    <p className="text-xs text-gray-400">
                        Already verified?{' '}
                        <button
                            onClick={() => navigate('/login')}
                            className="text-blue-800 font-semibold hover:underline"
                        >
                            Log in
                        </button>
                    </p>
                </div>
            </main>
        </div>
    );
};

export default CheckEmail;

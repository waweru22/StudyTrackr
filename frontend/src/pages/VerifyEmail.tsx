import React, { useEffect, useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import logo from '../assets/logo.png';
import { api } from '../api/client';
import { useUser } from '../context/UserContext';

type VerifyState = 'loading' | 'success' | 'error';

const VerifyEmail: React.FC = () => {
    const navigate = useNavigate();
    const { fetchUser } = useUser();
    const [state, setState] = useState<VerifyState>('loading');
    const [errorMessage, setErrorMessage] = useState('');
    const hasRun = useRef(false);

    useEffect(() => {
        // Guard against React Strict Mode double-mount
        if (hasRun.current) return;
        hasRun.current = true;

        const params = new URLSearchParams(window.location.search);
        const token = params.get('token');

        if (!token) {
            setState('error');
            setErrorMessage('No verification token found in the URL.');
            return;
        }

        const verifyToken = async () => {
            try {
                const response = await api.get<{
                    access_token: string;
                    user: { id: number; username: string; email: string };
                    message: string;
                }>(`/auth/verify-email?token=${token}`);

                if (response.access_token) {
                    sessionStorage.setItem('token', response.access_token);
                    await fetchUser();
                }

                setState('success');

                // Redirect to dashboard after 2 seconds
                setTimeout(() => {
                    navigate('/dashboard');
                }, 2000);
            } catch (err: any) {
                setState('error');
                setErrorMessage(
                    err.message || 'Verification failed. The link may be invalid or expired.'
                );
            }
        };

        verifyToken();
    }, [navigate]);

    return (
        <div className="min-h-screen bg-white font-sans text-gray-900 flex flex-col items-center justify-center">
            {/* Header/Logo */}
            <div className="mb-8">
                <img src={logo} alt="StudyTrackr Logo" className="h-12 w-auto" />
            </div>

            <main className="w-full max-w-md px-6 text-center">
                {state === 'loading' && (
                    <div className="space-y-4">
                        <div className="mx-auto w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center">
                            <Loader2 size={32} className="text-blue-700 animate-spin" />
                        </div>
                        <h2 className="text-2xl font-bold font-dm-sans text-gray-900">
                            Verifying your account...
                        </h2>
                        <p className="text-gray-500 text-base font-light font-dm-sans">
                            Please wait while we confirm your email.
                        </p>
                    </div>
                )}

                {state === 'success' && (
                    <div className="space-y-4">
                        <div className="mx-auto w-16 h-16 bg-green-50 rounded-full flex items-center justify-center">
                            <CheckCircle size={32} className="text-green-600" />
                        </div>
                        <h2 className="text-2xl font-bold font-dm-sans text-gray-900">
                            Email verified!
                        </h2>
                        <p className="text-gray-500 text-base font-light font-dm-sans">
                            Redirecting you to your dashboard...
                        </p>
                    </div>
                )}

                {state === 'error' && (
                    <div className="space-y-4">
                        <div className="mx-auto w-16 h-16 bg-red-50 rounded-full flex items-center justify-center">
                            <XCircle size={32} className="text-red-600" />
                        </div>
                        <h2 className="text-2xl font-bold font-dm-sans text-gray-900">
                            Verification failed
                        </h2>
                        <p className="text-red-600 text-base font-medium bg-red-50 p-3 rounded-lg border border-red-100">
                            {errorMessage}
                        </p>
                        <p className="text-gray-500 text-sm font-light font-dm-sans">
                            If your link expired, log in and request a new one.
                        </p>
                        <Link
                            to="/login"
                            className="inline-block mt-4 bg-blue-800 hover:bg-blue-900 text-white font-semibold font-dm-sans text-sm py-3 px-8 rounded-lg shadow-sm transition-all"
                        >
                            Go to Login
                        </Link>
                    </div>
                )}
            </main>
        </div>
    );
};

export default VerifyEmail;

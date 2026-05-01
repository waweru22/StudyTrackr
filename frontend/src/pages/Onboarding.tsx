import React, { useState, useEffect } from 'react';
import { ArrowLeft, ArrowRight, Check, AlertCircle, Eye, EyeOff, GraduationCap, Shield } from 'lucide-react';
import logo from '../assets/logo.png';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useUser } from '../context/UserContext';

const Onboarding: React.FC = () => {
    const navigate = useNavigate();
    const { step1Data, setStep1Data } = useUser();

    const [formData, setFormData] = useState({
        email: step1Data.email,
        username: step1Data.username,
        phone: step1Data.phone,
        level: step1Data.level || '100', // Ensure default if empty
        password: step1Data.password,
        confirmPassword: step1Data.confirmPassword
    });

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    const [errors, setErrors] = useState<Record<string, string>>({});

    const validateEmail = (email: string) => {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    };

    const getPasswordRequirements = (password: string) => [
        { met: password.length >= 8, text: "At least 8 characters" },
        { met: /[A-Z]/.test(password), text: "At least one uppercase letter" },
        { met: /[a-z]/.test(password), text: "At least one lowercase letter" },
        { met: /[0-9]/.test(password), text: "At least one number" },
    ];

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        let { name, value } = e.target;

        if (name === 'phone') {
            // Remove non-numeric characters
            value = value.replace(/\D/g, '');
            // Limit to 11 digits
            if (value.length > 11) {
                value = value.slice(0, 11);
            }
        }

        setFormData(prev => ({ ...prev, [name]: value }));

        // Clear specific error if it exists
        if (errors[name]) {
            setErrors(prev => {
                const newErrors = { ...prev };
                delete newErrors[name];
                return newErrors;
            });
        }
    };

    // Check for error from redirect (e.g. duplicate email)
    const location = useLocation();
    useEffect(() => {
        if (location.state?.error) {
            setErrors(prev => ({ ...prev, email: location.state.error }));
            // Clear state so refresh doesn't show it again? 
            // window.history.replaceState({}, document.title) // proper cleanup might be needed
        }
    }, [location.state]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        const newErrors: Record<string, string> = {};
        const passwordReqs = getPasswordRequirements(formData.password);
        const isPasswordValid = passwordReqs.every(req => req.met);

        if (!formData.email.trim()) {
            newErrors.email = "Email is required";
        } else if (!validateEmail(formData.email)) {
            newErrors.email = "Please enter a valid email address";
        }

        if (!formData.username.trim()) {
            newErrors.username = "Username is required";
        }

        if (!formData.phone.trim()) {
            newErrors.phone = "Phone number is required";
        } else if (formData.phone.length !== 11) {
            newErrors.phone = "Phone number must be exactly 11 digits";
        }

        if (!formData.level) {
            newErrors.level = "Level is required";
        }

        if (!formData.password) {
            newErrors.password = "Password is required";
        } else if (!isPasswordValid) {
            newErrors.password = "Password does not meet all requirements";
        }

        if (!formData.confirmPassword) {
            newErrors.confirmPassword = "Confirm Password is required";
        } else if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = "Passwords do not match";
        }

        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            return;
        }

        // Save step 1 data to context
        setStep1Data(formData);
        navigate('/onboarding/step-2');
    };

    const passwordRequirements = getPasswordRequirements(formData.password);

    return (
        <div className="min-h-screen bg-white font-sans text-gray-900 flex flex-col items-center">
            {/* Header */}
            <header className="w-full max-w-5xl mx-auto px-6 py-6 flex items-center justify-between">
                <div className="flex items-center">
                    <img src={logo} alt="StudyTrackr Logo" className="h-10 w-auto" />
                </div>
                <button
                    onClick={() => navigate(-1)}
                    className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                    <ArrowLeft size={16} />
                    <span>Back</span>
                </button>
            </header>

            {/* Main Content */}
            <main className="w-full max-w-xl px-6 py-8 flex-grow">
                {/* Role Selector Tabs */}
                <div className="flex bg-gray-100 rounded-lg p-1 mb-8 border border-gray-200">
                    <button
                        className="flex-1 flex items-center justify-center space-x-2 py-2.5 rounded-md text-sm font-semibold transition-all bg-blue-800 text-white shadow-sm"
                    >
                        <GraduationCap size={16} />
                        <span>I'm a Student</span>
                    </button>
                    <button
                        onClick={() => navigate('/admin/register')}
                        className="flex-1 flex items-center justify-center space-x-2 py-2.5 rounded-md text-sm font-semibold transition-all text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                    >
                        <Shield size={16} />
                        <span>I'm an Administrator</span>
                    </button>
                </div>

                <div className="space-y-2 mb-6">
                    <p className="text-sm font-medium text-gray-500 uppercase tracking-wider">1 of 4</p>
                    <h2 className="text-2xl font-bold font-dm-sans text-gray-900">Secure Your Progress</h2>
                    <p className="text-gray-500 text-base font-light font-dm-sans">
                        Create your account to save your AI-optimized routines and track your growth.
                    </p>
                </div>

                {/* Form */}
                <form className="space-y-4" onSubmit={handleSubmit}>
                    {/* Email */}
                    <div className="space-y-1.5">
                        <label className="block text-base font-medium font-dm-sans text-gray-700">
                            Email <span className="text-red-600">*</span>
                        </label>
                        <input
                            name="email"
                            type="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="e.g. xxxxxxxx@nileuniversity.edu.ng"
                            className={`w-full px-4 py-3 rounded-lg border ${errors.email ? 'border-red-500 ring-1 ring-red-500' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-400 text-sm transition-shadow shadow-sm`}
                        />
                        {errors.email && (
                            <p className="text-red-600 text-sm font-medium mt-1 flex items-center">
                                <AlertCircle size={14} className="mr-1" />
                                {errors.email}
                            </p>
                        )}
                    </div>

                    {/* Username */}
                    <div className="space-y-1.5">
                        <label className="block text-base font-medium font-dm-sans text-gray-700">
                            Username <span className="text-red-600">*</span>
                        </label>
                        <input
                            name="username"
                            type="text"
                            value={formData.username}
                            onChange={handleChange}
                            placeholder=""
                            className={`w-full px-4 py-3 rounded-lg border ${errors.username ? 'border-red-500 ring-1 ring-red-500' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-400 text-sm transition-shadow shadow-sm`}
                        />
                        {errors.username && (
                            <p className="text-red-600 text-sm font-medium mt-1 flex items-center">
                                <AlertCircle size={14} className="mr-1" />
                                {errors.username}
                            </p>
                        )}
                    </div>

                    {/* Phone & Level */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                            <label className="block text-base font-medium font-dm-sans text-gray-700">
                                Phone Number <span className="text-red-600">*</span>
                            </label>
                            <input
                                name="phone"
                                type="tel"
                                value={formData.phone}
                                onChange={handleChange}
                                placeholder="e.g. 0802 xxx 1234"
                                className={`w-full px-4 py-3 rounded-lg border ${errors.phone ? 'border-red-500 ring-1 ring-red-500' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-400 text-sm transition-shadow shadow-sm`}
                            />
                            {errors.phone && (
                                <p className="text-red-600 text-sm font-medium mt-1 flex items-center">
                                    <AlertCircle size={14} className="mr-1" />
                                    {errors.phone}
                                </p>
                            )}
                        </div>
                        <div className="space-y-1.5">
                            <label className="block text-base font-medium font-dm-sans text-gray-700">
                                Level <span className="text-red-600">*</span>
                            </label>
                            <div className="relative">
                                <select
                                    name="level"
                                    value={formData.level}
                                    onChange={handleChange}
                                    className={`w-full px-4 py-3 rounded-lg border ${errors.level ? 'border-red-500 ring-1 ring-red-500' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm transition-shadow shadow-sm appearance-none bg-white text-gray-700`}
                                >
                                    <option value="" disabled>Select Level</option>
                                    <option value="100">100</option>
                                    <option value="200">200</option>
                                    <option value="300">300</option>
                                    <option value="400">400</option>
                                </select>
                                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                                    <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                                        <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                                    </svg>
                                </div>
                            </div>
                            {errors.level && (
                                <p className="text-red-600 text-sm font-medium mt-1 flex items-center">
                                    <AlertCircle size={14} className="mr-1" />
                                    {errors.level}
                                </p>
                            )}
                        </div>
                    </div>

                    {/* Password */}
                    <div className="space-y-1.5">
                        <label className="block text-base font-medium font-dm-sans text-gray-700">
                            Password <span className="text-red-600">*</span>
                        </label>
                        <div className="relative">
                            <input
                                name="password"
                                type={showPassword ? "text" : "password"}
                                value={formData.password}
                                onChange={handleChange}
                                className={`w-full px-4 py-3 rounded-lg border ${errors.password ? 'border-red-500 ring-1 ring-red-500' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow shadow-sm pr-10`}
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute inset-y-0 right-0 flex items-center px-3 text-gray-500 hover:text-gray-700 focus:outline-none"
                            >
                                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>
                        </div>
                        {/* Password Constraints */}
                        <div className="mt-2 space-y-1">
                            {passwordRequirements.map((req, index) => (
                                <div key={index} className="flex items-center space-x-2 text-xs">
                                    <div className={`flex-shrink-0 w-4 h-4 rounded-full flex items-center justify-center ${req.met ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'}`}>
                                        {req.met ? <Check size={10} /> : <div className="w-1.5 h-1.5 rounded-full bg-gray-400" />}
                                    </div>
                                    <span className={`${req.met ? 'text-green-700 font-medium' : 'text-gray-500'}`}>{req.text}</span>
                                </div>
                            ))}
                        </div>
                        {errors.password && (
                            <p className="text-red-600 text-sm font-medium mt-1 flex items-center">
                                <AlertCircle size={14} className="mr-1" />
                                {errors.password}
                            </p>
                        )}
                    </div>

                    {/* Confirm Password */}
                    <div className="space-y-1.5">
                        <label className="block text-base font-medium font-dm-sans text-gray-700">
                            Confirm Password <span className="text-red-600">*</span>
                        </label>
                        <div className="relative">
                            <input
                                name="confirmPassword"
                                type={showConfirmPassword ? "text" : "password"}
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                className={`w-full px-4 py-3 rounded-lg border ${errors.confirmPassword ? 'border-red-500 ring-1 ring-red-500' : 'border-gray-300'} focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow shadow-sm pr-10`}
                            />
                            <button
                                type="button"
                                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                className="absolute inset-y-0 right-0 flex items-center px-3 text-gray-500 hover:text-gray-700 focus:outline-none"
                            >
                                {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>
                        </div>
                        {errors.confirmPassword && (
                            <p className="text-red-600 text-sm font-medium mt-1 flex items-center">
                                <AlertCircle size={14} className="mr-1" />
                                {errors.confirmPassword}
                            </p>
                        )}
                    </div>

                    <div className="pt-2">
                        <button
                            type="submit"
                            className="w-full flex items-center justify-center space-x-2 bg-blue-800 hover:bg-blue-900 text-white font-semibold font-dm-sans text-base py-3.5 rounded-lg shadow-sm transition-all transform active:scale-[0.99]"
                        >
                            <span>Continue</span>
                            <ArrowRight size={18} />
                        </button>
                    </div>
                </form>

                <p className="mt-6 text-base font-light font-dm-sans text-gray-500">
                    Already have an account? <Link to="/login" className="text-blue-700 font-medium font-dm-sans hover:underline">Sign in</Link>
                </p>
            </main>
        </div>
    );
};

export default Onboarding;

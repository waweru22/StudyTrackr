import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Calendar, BookOpen, FileText, Lightbulb, User, Bell, Settings, HelpCircle, LogOut, Shield, Menu } from 'lucide-react';
import logo from '../assets/logo.png';
import { useUser } from '../context/UserContext';

const Sidebar: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);
    const navigate = useNavigate();
    const { user } = useUser();

    const navItems = [
        { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
        { icon: Calendar, label: 'Schedule', path: '/schedule' },
        { icon: BookOpen, label: 'Materials', path: '/materials' },
        { icon: FileText, label: 'Notes', path: '/notes' },
        { icon: Lightbulb, label: 'Study Tips', path: '/study-tips' },
    ];

    const manageItems = [
        { icon: User, label: 'Profile', path: '/profile' },
        { icon: Bell, label: 'Notifications', path: '/notifications' },
    ];

    const handleSignOut = () => {
        // Clear auth state
        sessionStorage.removeItem('token');
        navigate('/');
    };

    return (
        <>
            {/* Hamburger Button */}
            <button 
                className="md:hidden fixed top-4 left-4 z-[60] p-2 bg-white rounded-md shadow-md border border-gray-200 text-gray-700"
                onClick={() => setIsOpen(!isOpen)}
            >
                <Menu size={24} />  
            </button>

            {/* Mobile Overlay */}
            {isOpen && (
                <div 
                    className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
                    onClick={() => setIsOpen(false)}
                />
            )}

            <aside className={`
                fixed inset-y-0 left-0 z-50 w-64 bg-[#EDEFF4] border-r border-gray-200 flex flex-col pt-6 pb-6 shadow-sidebar
                transform transition-transform duration-300
                md:relative md:translate-x-0
                ${isOpen ? 'translate-x-0' : '-translate-x-full'}
                md:flex md:flex-col
            `}>
            {/* Logo */}
            <div className="px-6 mb-8">
                <img src={logo} alt="StudyTrackr" className="h-8 w-auto" />
            </div>

            {/* Main Menu */}
            <div className="flex-1 px-4 space-y-8 overflow-y-auto">
                <div>
                    <div className="space-y-1">
                        {navItems.map((item) => (
                            <NavLink
                                key={item.path}
                                to={item.path}
                                onClick={() => setIsOpen(false)}
                                className={({ isActive }) => `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive ? 'text-gray-900 font-bold' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100/50'}`}
                            >
                                {({ isActive }) => (
                                    <>
                                        <item.icon size={18} className={isActive ? 'text-gray-900' : 'text-gray-400'} />
                                        <span>{item.label}</span>
                                    </>
                                )}
                            </NavLink>
                        ))}
                    </div>
                </div>

                {/* Manage Section */}
                <div>
                    <h3 className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Manage</h3>
                    <div className="space-y-1">
                        {manageItems.map((item) => (
                            <NavLink
                                key={item.path}
                                to={item.path}
                                onClick={() => setIsOpen(false)}
                                className={({ isActive }) => `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive ? 'text-gray-900 font-bold' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100/50'}`}
                            >
                                <item.icon size={18} />
                                <span>{item.label}</span>
                            </NavLink>
                        ))}
                    </div>
                </div>

                {/* Admin Panel Link (conditional) */}
                {user?.role === 'admin' && (
                    <div>
                        <h3 className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Admin</h3>
                        <NavLink
                            to="/admin/dashboard"
                            className={({ isActive }) => `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive ? 'text-blue-800 font-bold bg-blue-50' : 'text-blue-600 hover:text-blue-800 hover:bg-blue-50/50'}`}
                        >
                            <Shield size={18} />
                            <span>Admin Panel</span>
                        </NavLink>
                    </div>
                )}

                {/* Help Section */}
                <div>
                    <h3 className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Help & Settings</h3>
                    <div className="space-y-1">
                        <NavLink
                            to="/help"
                            onClick={() => setIsOpen(false)}
                            className={({ isActive }) => `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive ? 'text-gray-900 font-bold' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100/50'}`}
                        >
                            <HelpCircle size={18} />
                            <span>Help</span>
                        </NavLink>
                        <NavLink
                            to="/settings"
                            onClick={() => setIsOpen(false)}
                            className={({ isActive }) => `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive ? 'text-gray-900 font-bold' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100/50'}`}
                        >
                            <Settings size={18} />
                            <span>Settings</span>
                        </NavLink>
                    </div>
                </div>
            </div>

            {/* Sign Out Button */}
            <div className="px-4 mt-auto border-t border-gray-200 pt-4">
                <button
                    onClick={handleSignOut}
                    className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
                >
                    <LogOut size={18} />
                    <span>Sign Out</span>
                </button>
            </div>
        </aside>
        </>
    );
};

export default Sidebar;

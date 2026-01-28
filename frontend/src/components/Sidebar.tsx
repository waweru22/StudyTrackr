import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Calendar, BookOpen, FileText, Lightbulb, User, Bell, Settings, HelpCircle, LogOut } from 'lucide-react';
import logo from '../assets/logo.png';

const Sidebar: React.FC = () => {
    const navigate = useNavigate();

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
        { icon: Settings, label: 'Settings', path: '/settings' },
    ];

    const handleSignOut = () => {
        // Clear auth state here (e.g., localStorage.clear())
        // For now, simple navigation back to landing page
        navigate('/');
    };

    return (
        <aside className="w-64 h-screen bg-[#EDEFF4] border-r border-gray-200 fixed left-0 top-0 flex flex-col pt-6 pb-6 shadow-sidebar z-50">
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
                                className={({ isActive }) => `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive || item.label === 'Dashboard' ? 'text-gray-900 font-bold' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100/50'}`}
                            >
                                {({ isActive }) => (
                                    <>
                                        <item.icon size={18} className={isActive || item.label === 'Dashboard' ? 'text-gray-900' : 'text-gray-400'} />
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
                                className={({ isActive }) => `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive ? 'text-gray-900 font-bold' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100/50'}`}
                            >
                                <item.icon size={18} />
                                <span>{item.label}</span>
                            </NavLink>
                        ))}
                    </div>
                </div>

                {/* Help Section */}
                <div>
                    <h3 className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Help</h3>
                    <NavLink
                        to="/help"
                        className="flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-500 hover:text-gray-900 hover:bg-gray-100/50 transition-colors"
                    >
                        <HelpCircle size={18} />
                        <span>Help Center</span>
                    </NavLink>
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
    );
};

export default Sidebar;

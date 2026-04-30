import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
    LayoutDashboard, BookOpen, BarChart3, FlaskConical,
    ShieldCheck, Megaphone, LogOut, Shield
} from 'lucide-react';
import logo from '../assets/logo.png';

const AdminSidebar: React.FC = () => {
    const navigate = useNavigate();

    const mainItems = [
        { icon: LayoutDashboard, label: 'Dashboard', path: '/admin/dashboard' },
        { icon: BookOpen, label: 'Courses', path: '/admin/courses' },
        { icon: ShieldCheck, label: 'Verification', path: '/admin/verification' },
    ];

    const analyticsItems = [
        { icon: BarChart3, label: 'Course Analytics', path: '/admin/analytics/courses' },
        { icon: FlaskConical, label: 'Techniques', path: '/admin/analytics/techniques' },
    ];

    const communicationItems = [
        { icon: Megaphone, label: 'Broadcast', path: '/admin/broadcast' },
    ];

    const handleSignOut = () => {
        sessionStorage.removeItem('token');
        navigate('/admin/login');
    };

    const linkClass = ({ isActive }: { isActive: boolean }) =>
        `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${isActive
            ? 'bg-blue-600/20 text-blue-300 font-bold'
            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
        }`;

    return (
        <aside className="w-64 h-screen bg-slate-900 border-r border-slate-700/50 fixed left-0 top-0 flex flex-col pt-6 pb-6 z-50">
            {/* Logo + Badge */}
            <div className="px-6 mb-8">
                <div className="flex items-center space-x-3">
                    <img src={logo} alt="StudyTrackr" className="h-7 w-auto brightness-0 invert" />
                </div>
                <div className="mt-3 flex items-center space-x-2 px-1">
                    <Shield size={14} className="text-blue-400" />
                    <span className="text-xs font-bold text-blue-400 uppercase tracking-wider">Admin Panel</span>
                </div>
            </div>

            {/* Navigation */}
            <div className="flex-1 px-4 space-y-6 overflow-y-auto">
                {/* Main */}
                <div>
                    <h3 className="px-3 text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Main</h3>
                    <div className="space-y-1">
                        {mainItems.map((item) => (
                            <NavLink key={item.path} to={item.path} className={linkClass}>
                                <item.icon size={18} />
                                <span>{item.label}</span>
                            </NavLink>
                        ))}
                    </div>
                </div>

                {/* Analytics */}
                <div>
                    <h3 className="px-3 text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Analytics</h3>
                    <div className="space-y-1">
                        {analyticsItems.map((item) => (
                            <NavLink key={item.path} to={item.path} className={linkClass}>
                                <item.icon size={18} />
                                <span>{item.label}</span>
                            </NavLink>
                        ))}
                    </div>
                </div>

                {/* Communication */}
                <div>
                    <h3 className="px-3 text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Communication</h3>
                    <div className="space-y-1">
                        {communicationItems.map((item) => (
                            <NavLink key={item.path} to={item.path} className={linkClass}>
                                <item.icon size={18} />
                                <span>{item.label}</span>
                            </NavLink>
                        ))}
                    </div>
                </div>
            </div>

            {/* Sign Out */}
            <div className="px-4 mt-auto border-t border-slate-700/50 pt-4">
                <button
                    onClick={handleSignOut}
                    className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium text-red-400 hover:bg-red-500/10 transition-colors"
                >
                    <LogOut size={18} />
                    <span>Sign Out</span>
                </button>
            </div>
        </aside>
    );
};

export default AdminSidebar;

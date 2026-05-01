import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import Onboarding from './pages/Onboarding';
import OnboardingStep2 from './pages/OnboardingStep2';
import OnboardingStep3 from './pages/OnboardingStep3';
import OnboardingStep4 from './pages/OnboardingStep4';
import Dashboard from './pages/Dashboard';
import Schedule from './pages/Schedule';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import StudyTips from './pages/StudyTips';
import Materials from './pages/Materials';
import Notes from './pages/Notes';
import Help from './pages/Help';
import Login from './pages/Login';
import VerifyOTP from './pages/VerifyOTP';
import SessionTimer from './pages/SessionTimer';
import { UserProvider } from './context/UserContext';
import NotificationsPage from './pages/NotificationsPage';
import ProtectedRoute from './components/ProtectedRoute';

// Admin imports
import AdminRoute from './components/AdminRoute';
import AdminRegister from './pages/admin/AdminRegister';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminCourses from './pages/admin/AdminCourses';
import CourseAnalytics from './pages/admin/CourseAnalytics';
import TechniqueAnalytics from './pages/admin/TechniqueAnalytics';
import Verification from './pages/admin/Verification';
import AdminBroadcast from './pages/admin/AdminBroadcast';

function App() {
  return (
    <UserProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/onboarding/step-2" element={<OnboardingStep2 />} />
          <Route path="/onboarding/step-3" element={<OnboardingStep3 />} />
          <Route path="/onboarding/step-4" element={<OnboardingStep4 />} />
          <Route path="/verify-otp" element={<VerifyOTP />} />
          <Route path="/help" element={<Help />} />

          {/* Admin Public Route */}
          <Route path="/admin/register" element={<AdminRegister />} />

          {/* Protected Student Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/schedule" element={<Schedule />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/tips" element={<StudyTips />} />
            <Route path="/materials" element={<Materials />} />
            <Route path="/notes" element={<Notes />} />
            <Route path="/session-timer" element={<SessionTimer />} />
            <Route path="/notifications" element={<NotificationsPage />} />
          </Route>

          {/* Protected Admin Routes */}
          <Route element={<AdminRoute />}>
            <Route path="/admin/dashboard" element={<AdminDashboard />} />
            <Route path="/admin/courses" element={<AdminCourses />} />
            <Route path="/admin/analytics/courses" element={<CourseAnalytics />} />
            <Route path="/admin/analytics/techniques" element={<TechniqueAnalytics />} />
            <Route path="/admin/verification" element={<Verification />} />
            <Route path="/admin/broadcast" element={<AdminBroadcast />} />
          </Route>
        </Routes>
      </Router>
    </UserProvider>
  );
}

export default App;

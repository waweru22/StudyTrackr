import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import Onboarding from './pages/Onboarding';
import OnboardingStep2 from './pages/OnboardingStep2';
import OnboardingStep3 from './pages/OnboardingStep3';
import OnboardingStep4 from './pages/OnboardingStep4';
import Dashboard from './pages/Dashboard';

import { UserProvider } from './context/UserContext';
import SessionTimer from './pages/SessionTimer';

function App() {
  return (
    <UserProvider>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/onboarding/step-2" element={<OnboardingStep2 />} />
          <Route path="/onboarding/step-3" element={<OnboardingStep3 />} />
          <Route path="/onboarding/step-4" element={<OnboardingStep4 />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/session-timer" element={<SessionTimer />} />
          {/* Placeholder for future routes */}
          <Route path="/login" element={<div className="p-8 text-center text-xl">Login Page (Coming Soon)</div>} />
        </Routes>
      </Router>
    </UserProvider>
  );
}

export default App;

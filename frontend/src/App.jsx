// File: frontend/src/App.jsx

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

// Pages
import LandingPage from './pages/LandingPage';
import CheckReferencePage from './pages/CheckReferencePage';
import ReportPage from './pages/ReportPage';
import HistoryPage from './pages/HistoryPage';
import ProfilePage from './pages/ProfilePage';

// Navigation
import Navigation from './components/Navigation';

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        
        <Routes>
          {/* Public route */}
          <Route path="/" element={<LandingPage />} />
          
          {/* Protected routes */}
          <Route 
            path="/check" 
            element={isAuthenticated ? <CheckReferencePage /> : <Navigate to="/" />} 
          />
          <Route 
            path="/report/:id" 
            element={isAuthenticated ? <ReportPage /> : <Navigate to="/" />} 
          />
          <Route 
            path="/history" 
            element={isAuthenticated ? <HistoryPage /> : <Navigate to="/" />} 
          />
          <Route 
            path="/profile" 
            element={isAuthenticated ? <ProfilePage /> : <Navigate to="/" />} 
          />
          
          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
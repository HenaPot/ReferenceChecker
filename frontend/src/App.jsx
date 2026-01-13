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
          {/* Public route - redirect authenticated users to /check */}
          <Route 
            path="/" 
            element={isAuthenticated ? <Navigate to="/check" replace /> : <LandingPage />} 
          />
          
          {/* Protected routes */}
          <Route 
            path="/check" 
            element={isAuthenticated ? <CheckReferencePage /> : <Navigate to="/" replace />} 
          />
          <Route 
            path="/report/:id" 
            element={isAuthenticated ? <ReportPage /> : <Navigate to="/" replace />} 
          />
          <Route 
            path="/history" 
            element={isAuthenticated ? <HistoryPage /> : <Navigate to="/" replace />} 
          />
          <Route 
            path="/profile" 
            element={isAuthenticated ? <ProfilePage /> : <Navigate to="/" replace />} 
          />
          
          {/* Catch all - redirect to appropriate page based on auth */}
          <Route 
            path="*" 
            element={<Navigate to={isAuthenticated ? "/check" : "/"} replace />} 
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
// File: frontend/src/components/Navigation.jsx

import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Home, History, User, LogOut, CheckCircle } from 'lucide-react';

export default function Navigation() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <CheckCircle className="h-8 w-8 text-primary-600" />
              <span className="text-xl font-bold text-gray-900">
                Reference Checker
              </span>
            </Link>
          </div>

          {/* Navigation Links */}
          {isAuthenticated && (
            <div className="flex items-center space-x-4">
              <Link
                to="/check"
                className="flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-100"
              >
                <Home className="h-4 w-4" />
                <span>Check Reference</span>
              </Link>
              
              <Link
                to="/history"
                className="flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-100"
              >
                <History className="h-4 w-4" />
                <span>History</span>
              </Link>
              
              <Link
                to="/profile"
                className="flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-100"
              >
                <User className="h-4 w-4" />
                <span>{user?.email?.split('@')[0]}</span>
              </Link>
              
              <button
                onClick={handleLogout}
                className="flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium text-red-600 hover:bg-red-50"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
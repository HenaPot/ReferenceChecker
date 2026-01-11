// File: frontend/src/pages/LandingPage.jsx

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { CheckCircle, Shield, TrendingUp, Users } from 'lucide-react';

export default function LandingPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login, register, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Redirect if already logged in
  if (isAuthenticated) {
    navigate('/check');
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = isLogin 
      ? await login(email, password)
      : await register(email, password);

    setLoading(false);

    if (result.success) {
      navigate('/check');
    } else {
      let errorMessage = 'An error occurred';
      
      if (typeof result.error === 'string') {
        errorMessage = result.error;
      } else if (result.error?.message) {
        errorMessage = result.error.message;
      } else if (result.error?.detail) {
        if (typeof result.error.detail === 'string') {
          errorMessage = result.error.detail;
        } else if (Array.isArray(result.error.detail)) {
          const firstError = result.error.detail[0];
          errorMessage = firstError?.msg || 'Validation error';
        } else if (typeof result.error.detail === 'object') {
          errorMessage = JSON.stringify(result.error.detail);
        }
      }
      
      setError(errorMessage);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-100">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Left side - Marketing */}
          <div className="space-y-8">
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-12 w-12 text-primary-600" />
                <h1 className="text-5xl font-bold text-gray-900">
                  Reference Checker
                </h1>
              </div>
              <p className="text-xl text-gray-600">
                Verify academic sources instantly with AI-powered credibility analysis
              </p>
            </div>

            {/* Features */}
            <div className="space-y-4">
              <Feature
                icon={<Shield className="h-6 w-6" />}
                title="Domain Reputation"
                description="Verify sources from trusted academic and research institutions"
              />
              <Feature
                icon={<TrendingUp className="h-6 w-6" />}
                title="AI Analysis"
                description="Advanced AI evaluates content quality and credibility"
              />
              <Feature
                icon={<Users className="h-6 w-6" />}
                title="Cross-References"
                description="Find similar sources and corroborating evidence"
              />
            </div>
          </div>

          {/* Right side - Auth Form */}
          <div className="bg-white rounded-2xl shadow-2xl p-8">
            <div className="mb-6">
              <div className="flex space-x-2 mb-4">
                <button
                  onClick={() => { setIsLogin(true); setError(''); }}
                  className={`flex-1 py-2 px-4 rounded-lg font-medium ${
                    isLogin
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  Login
                </button>
                <button
                  onClick={() => { setIsLogin(false); setError(''); }}
                  className={`flex-1 py-2 px-4 rounded-lg font-medium ${
                    !isLogin
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  Register
                </button>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="student@university.edu"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="••••••••"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Please wait...' : isLogin ? 'Login' : 'Create Account'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

function Feature({ icon, title, description }) {
  return (
    <div className="flex items-start space-x-3">
      <div className="flex-shrink-0 text-primary-600">{icon}</div>
      <div>
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <p className="text-gray-600 text-sm">{description}</p>
      </div>
    </div>
  );
}
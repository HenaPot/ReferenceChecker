// File: frontend/src/pages/CheckReferencePage.jsx

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { referenceAPI } from '../services/api';
import { Search, Loader } from 'lucide-react';

export default function CheckReferencePage() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await referenceAPI.checkReference(url);
      const referenceId = response.data.reference_id;
      
      // Wait a moment for analysis to start
      setTimeout(() => {
        navigate(`/report/${referenceId}`);
      }, 1000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to check reference');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Check Reference Credibility
        </h1>
        <p className="text-lg text-gray-600">
          Enter a URL to analyze its credibility using our AI-powered system
        </p>
      </div>

      <div className="bg-white rounded-2xl shadow-xl p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reference URL
            </label>
            <div className="relative">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
                disabled={loading}
                className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-lg"
                placeholder="https://www.nature.com/articles/..."
              />
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            </div>
            <p className="mt-2 text-sm text-gray-500">
              Supported: Academic journals, news articles, research papers, and more
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary-600 text-white py-4 px-6 rounded-lg font-medium text-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <Loader className="h-5 w-5 animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <span>Check Credibility</span>
            )}
          </button>
        </form>

        {/* Examples */}
        <div className="mt-8 pt-8 border-t border-gray-200">
          <p className="text-sm font-medium text-gray-700 mb-3">Try these examples:</p>
          <div className="space-y-2">
            {[
              'https://www.nature.com/articles/s41586-024-12345',
              'https://arxiv.org/abs/2401.12345',
              'https://www.sciencedirect.com/science/article/...'
            ].map((example, i) => (
              <button
                key={i}
                type="button"
                onClick={() => setUrl(example)}
                className="block w-full text-left px-4 py-2 text-sm text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
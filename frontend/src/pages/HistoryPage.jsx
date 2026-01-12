// File: frontend/src/pages/HistoryPage.jsx

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { referenceAPI } from '../services/api';
import { ExternalLink, Trash2, Loader, AlertTriangle } from 'lucide-react';

export default function HistoryPage() {
  const [references, setReferences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await referenceAPI.getHistory();
      console.log('History API response:', response.data); // Debug log
      
      const data = Array.isArray(response.data) 
        ? response.data 
        : response.data.references || [];
      
      setReferences(data);
      setError('');
    } catch (err) {
      console.error('Failed to load history', err);
      setError('Failed to load reference history');
      setReferences([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this reference?')) return;
    
    try {
      await referenceAPI.deleteReference(id);
      setReferences(references.filter(ref => ref.reference_id !== id));
    } catch (err) {
      alert('Failed to delete reference');
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-50';
    if (score >= 60) return 'text-blue-600 bg-blue-50';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="flex items-center justify-center h-64">
          <Loader className="h-12 w-12 text-primary-600 animate-spin" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
          <AlertTriangle className="h-12 w-12 text-red-600 mx-auto mb-4" />
          <p className="text-red-600 font-medium mb-4">{error}</p>
          <button
            onClick={fetchHistory}
            className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Reference History</h1>
        <p className="text-gray-600">View all your analyzed references</p>
      </div>

      {references.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-500 mb-4">No references checked yet</p>
          <Link
            to="/check"
            className="inline-block bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
          >
            Check Your First Reference
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  URL
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Domain
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {references.map((ref) => (
                <tr key={ref.reference_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <a
                      href={ref.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary-600 hover:underline flex items-center space-x-1 max-w-md truncate"
                    >
                      <span className="truncate">{ref.url}</span>
                      <ExternalLink className="h-3 w-3 flex-shrink-0" />
                    </a>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {ref.domain}
                  </td>
                  <td className="px-6 py-4">
                    {ref.credibility_score !== null ? (
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(ref.credibility_score)}`}>
                        {ref.credibility_score}/100
                      </span>
                    ) : (
                      <span className="text-gray-400 text-sm">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      ref.status === 'completed' ? 'bg-green-100 text-green-800' :
                      ref.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {ref.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(ref.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    {ref.status === 'completed' && (
                      <Link
                        to={`/report/${ref.reference_id}`}
                        className="text-primary-600 hover:text-primary-700 font-medium text-sm"
                      >
                        View Report
                      </Link>
                    )}
                    <button
                      onClick={() => handleDelete(ref.reference_id)}
                      className="text-red-600 hover:text-red-700 ml-4"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
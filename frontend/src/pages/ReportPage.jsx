// File: frontend/src/pages/ReportPage.jsx

import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { referenceAPI } from '../services/api';
import { ArrowLeft, RefreshCw, Loader, AlertTriangle, CheckCircle } from 'lucide-react';

import CredibilityGauge from '../components/CredibilityGauge';
import ScoreBreakdown from '../components/ScoreBreakdown';
import SimilarSources from '../components/SimilarSources';

export default function ReportPage() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [reanalyzing, setReanalyzing] = useState(false);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  
  const isMounted = useRef(true);
  const successTimeoutRef = useRef(null);

  useEffect(() => {
    isMounted.current = true;
    fetchReport();
    
    const interval = setInterval(() => {
      if (data?.reference?.status === 'processing') {
        fetchReport();
      }
    }, 3000);

    return () => {
      isMounted.current = false;
      clearInterval(interval);
      if (successTimeoutRef.current) {
        clearTimeout(successTimeoutRef.current);
      }
    };
  }, [id]);

  const fetchReport = async () => {
    try {
      const response = await referenceAPI.getReference(id);
      if (isMounted.current) {
        setData(response.data);
        setLoading(false);
      }
    } catch (err) {
      if (isMounted.current) {
        setError('Failed to load report');
        setLoading(false);
      }
    }
  };

  const handleReanalyze = async () => {
    setReanalyzing(true);
    setError('');
    setShowSuccessMessage(false);
    
    try {
      await referenceAPI.reanalyze(id);
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      let attempts = 0;
      const maxAttempts = 15;
      
      const pollForResults = async () => {
        try {
          const response = await referenceAPI.getReference(id);
          
          if (response.data.reference.status === 'processing' && attempts < maxAttempts) {
            attempts++;
            await new Promise(resolve => setTimeout(resolve, 1000));
            return pollForResults();
          }
          
          if (isMounted.current) {
            setData(response.data);
          }
          
        } catch (pollError) {
          console.error('Polling error:', pollError);
          if (isMounted.current) {
            setError('Analysis may still be in progress. Please refresh.');
          }
        }
      };
      
      await pollForResults();
      
      if (isMounted.current) {
        setShowSuccessMessage(true);
        successTimeoutRef.current = setTimeout(() => {
          if (isMounted.current) {
            setShowSuccessMessage(false);
          }
        }, 3000);
      }
      
    } catch (err) {
      if (isMounted.current) {
        setError('Failed to reanalyze. Please try again.');
        console.error('Reanalyze error:', err);
      }
    } finally {
      if (isMounted.current) {
        setReanalyzing(false);
      }
    }
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

  if (error && !data) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <AlertTriangle className="h-12 w-12 text-red-600 mx-auto mb-4" />
          <p className="text-red-600 font-medium">{error}</p>
        </div>
      </div>
    );
  }

  const { reference, report } = data;

  if (reference.status === 'processing' || reanalyzing) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
          <Loader className="h-16 w-16 text-blue-600 mx-auto mb-4 animate-spin" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {reanalyzing ? 'Reanalyzing Reference...' : 'Analysis in Progress'}
          </h2>
          <p className="text-gray-600 mb-4">
            {reanalyzing 
              ? 'Running fresh credibility analysis. This usually takes 10-15 seconds...'
              : 'We\'re analyzing this reference. This usually takes 10-15 seconds...'}
          </p>
          
          {/* Progress indicator - indeterminate */}
          <div className="max-w-md mx-auto mt-6">
            <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
              <span>Analyzing domain</span>
              <span>Extracting metadata</span>
              <span>AI analysis</span>
            </div>
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full w-full animate-pulse"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (reference.status === 'failed') {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
          <AlertTriangle className="h-16 w-16 text-red-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Analysis Failed</h2>
          <p className="text-gray-600 mb-4">
            Something went wrong during analysis. Please try again.
          </p>
          <button
            onClick={handleReanalyze}
            disabled={reanalyzing}
            className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50 inline-flex items-center space-x-2"
          >
            {reanalyzing ? (
              <>
                <Loader className="h-4 w-4 animate-spin" />
                <span>Retrying...</span>
              </>
            ) : (
              <span>Retry Analysis</span>
            )}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Success message after reanalysis */}
      {showSuccessMessage && (
        <div className="fixed top-20 right-4 z-50 bg-green-50 border border-green-200 rounded-lg p-4 shadow-lg flex items-center space-x-3 animate-fade-in">
          <CheckCircle className="h-5 w-5 text-green-600" />
          <span className="text-green-800 font-medium">Analysis complete!</span>
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
          <AlertTriangle className="h-5 w-5 text-red-600" />
          <span className="text-red-800">{error}</span>
        </div>
      )}

      {/* Header */}
      <div className="mb-8">
        <Link to="/history" className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to History
        </Link>
        
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Credibility Report</h1>
            <p className="text-gray-600 break-all">{reference.url}</p>
            <p className="text-sm text-gray-500 mt-1">
              Analyzed on {new Date(reference.created_at).toLocaleDateString()}
            </p>
          </div>
          
          <button
            onClick={handleReanalyze}
            disabled={reanalyzing}
            className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <RefreshCw className={`h-4 w-4 ${reanalyzing ? 'animate-spin' : ''}`} />
            <span>{reanalyzing ? 'Analyzing...' : 'Reanalyze'}</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left column - Gauge */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-lg p-8 sticky top-20">
            <CredibilityGauge score={report.total_score} total={100} />
            
            {/* Red Flags */}
            {report.red_flags && report.red_flags.length > 0 && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-3">⚠️ Red Flags</h4>
                <ul className="space-y-2">
                  {report.red_flags.map((flag, i) => (
                    <li key={i} className="text-sm text-red-600 flex items-start">
                      <span className="mr-2">•</span>
                      <span>{flag}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* Right column - Details */}
        <div className="lg:col-span-2 space-y-6">
          <ScoreBreakdown report={report} />
          {/* <SimilarSources sources={report.similar_sources || []} /> */}
        </div>
      </div>
    </div>
  );
}
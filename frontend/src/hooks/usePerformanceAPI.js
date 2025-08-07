import { useState, useEffect } from 'react';
import axios from 'axios';

// Get backend URL from environment variable
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: BACKEND_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const usePerformanceAPI = () => {
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Check backend connection on mount
  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      setConnectionStatus('checking');
      const response = await api.get('/health');
      if (response.data.status === 'healthy') {
        setConnectionStatus('connected');
      } else {
        setConnectionStatus('error');
      }
    } catch (err) {
      console.error('Backend connection failed:', err);
      setConnectionStatus('disconnected');
    }
  };

  const startTest = async (testConfig) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/test/start', testConfig);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to start test';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getTestStatus = async (testId) => {
    try {
      const response = await api.get(`/test/${testId}/status`);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to get test status';
      throw new Error(errorMessage);
    }
  };

  const analyzeResults = async (testData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/analyze', testData);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to analyze results';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const analyzeResultsWithImage = async (testData, imageUrl) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/analyze/image', {
        test_data: testData,
        image_url: imageUrl
      });
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to analyze results with image';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const listTests = async () => {
    try {
      const response = await api.get('/tests');
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to list tests';
      throw new Error(errorMessage);
    }
  };

  const getTestHistory = async () => {
    try {
      const response = await api.get('/tests/history');
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to get test history';
      throw new Error(errorMessage);
    }
  };

  const getAgentMemory = async () => {
    try {
      const response = await api.get('/agent/memory');
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to get agent memory';
      throw new Error(errorMessage);
    }
  };

  const getAgentStatus = async () => {
    try {
      const response = await api.get('/agent/status');
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to get agent status';
      throw new Error(errorMessage);
    }
  };

  return {
    // API functions
    startTest,
    getTestStatus,
    analyzeResults,
    analyzeResultsWithImage,
    listTests,
    getTestHistory,
    getAgentMemory,
    getAgentStatus,
    
    // State
    connectionStatus,
    loading,
    error,
    
    // Utilities
    checkConnection,
    backendUrl: BACKEND_URL,
  };
}; 
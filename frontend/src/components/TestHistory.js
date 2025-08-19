import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Clock, Eye, Download, Trash2, Calendar, Users, Target } from 'lucide-react';

const TestHistory = () => {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);

  // Mock test history data
  useEffect(() => {
    const mockTests = [
      {
        id: 'test_1',
        name: 'Load Test - 100 Users',
        status: 'completed',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        config: {
          numUsers: 100,
          duration: 60,
          targetURL: 'http://localhost:3000'
        },
        results: {
          totalRequests: 1000,
          successfulRequests: 920,
          failedRequests: 80,
          successRate: 92,
          avgResponseTime: 367,
          peakRPS: 55
        }
      },
      {
        id: 'test_2',
        name: 'Stress Test - 500 Users',
        status: 'completed',
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        config: {
          numUsers: 500,
          duration: 120,
          targetURL: 'http://localhost:3000'
        },
        results: {
          totalRequests: 5000,
          successfulRequests: 4800,
          failedRequests: 200,
          successRate: 96,
          avgResponseTime: 445,
          peakRPS: 78
        }
      },
      {
        id: 'test_3',
        name: 'Spike Test - 200 Users',
        status: 'failed',
        timestamp: new Date(Date.now() - 10800000).toISOString(),
        config: {
          numUsers: 200,
          duration: 30,
          targetURL: 'http://localhost:3000'
        },
        results: {
          totalRequests: 800,
          successfulRequests: 600,
          failedRequests: 200,
          successRate: 75,
          avgResponseTime: 1200,
          peakRPS: 45
        }
      }
    ];

    setTimeout(() => {
      setTests(mockTests);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-success-100 text-success-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-danger-100 text-danger-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return '✓';
      case 'running':
        return '⟳';
      case 'failed':
        return '✗';
      default:
        return '?';
    }
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minutes ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-500">Loading test history...</p>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Clock className="h-5 w-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">Test History</h2>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">
              {tests.length} tests completed
            </span>
          </div>
        </div>
      </div>

      {/* Test List */}
      <div className="space-y-4">
        {tests.map((test, index) => (
          <motion.div
            key={test.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card hover:shadow-md transition-shadow duration-200"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h3 className="font-medium text-gray-900">{test.name}</h3>
                  <div className={`status-indicator ${getStatusColor(test.status)}`}>
                    {getStatusIcon(test.status)}
                    <span className="ml-1 capitalize">{test.status}</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div className="flex items-center space-x-2">
                    <Calendar className="h-4 w-4 text-gray-400" />
                    <span className="text-gray-600">{formatTimestamp(test.timestamp)}</span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Users className="h-4 w-4 text-gray-400" />
                    <span className="text-gray-600">{test.config.numUsers} users</span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Clock className="h-4 w-4 text-gray-400" />
                    <span className="text-gray-600">{formatDuration(test.config.duration)}</span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Target className="h-4 w-4 text-gray-400" />
                    <span className="text-gray-600">{test.results.successRate}% success</span>
                  </div>
                </div>
                
                {test.results && (
                  <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                    <div>
                      <span className="text-gray-500">Total Requests:</span>
                      <span className="ml-1 font-medium">{test.results.totalRequests.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Avg Response:</span>
                      <span className="ml-1 font-medium">{test.results.avgResponseTime}ms</span>
                    </div>
                    <div>
                                              <span className="text-gray-500">Transaction Per Second:</span>
                      <span className="ml-1 font-medium">{test.results.peakRPS}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Failed:</span>
                      <span className="ml-1 font-medium">{test.results.failedRequests}</span>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex items-center space-x-2 ml-4">
                <button className="p-2 text-gray-400 hover:text-primary-600 transition-colors">
                  <Eye className="h-4 w-4" />
                </button>
                <button className="p-2 text-gray-400 hover:text-success-600 transition-colors">
                  <Download className="h-4 w-4" />
                </button>
                <button className="p-2 text-gray-400 hover:text-danger-600 transition-colors">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Empty State */}
      {tests.length === 0 && (
        <div className="card">
          <div className="text-center py-12">
            <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Test History</h3>
            <p className="text-gray-500">
              Run your first performance test to see it appear here
            </p>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default TestHistory; 
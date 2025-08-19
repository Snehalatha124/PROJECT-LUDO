import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, BarChart3, Clock, Users, Target, CheckCircle, XCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const TestResults = ({ results }) => {
  if (!results) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <div className="text-center py-12">
          <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Test Results</h3>
          <p className="text-gray-500">
            Complete a performance test to view detailed results
          </p>
        </div>
      </motion.div>
    );
  }

  const successRate = results.successRate || 0;
  const failedRate = 100 - successRate;

  const pieData = [
    { name: 'Successful', value: results.successfulRequests || 0, color: '#22c55e' },
    { name: 'Failed', value: results.failedRequests || 0, color: '#ef4444' }
  ];

  const responseTimeData = [
    { range: '0-200ms', count: Math.floor((results.totalRequests || 0) * 0.3) },
    { range: '200-500ms', count: Math.floor((results.totalRequests || 0) * 0.4) },
    { range: '500-1000ms', count: Math.floor((results.totalRequests || 0) * 0.2) },
    { range: '1000ms+', count: Math.floor((results.totalRequests || 0) * 0.1) }
  ];

  const getPerformanceGrade = (successRate, avgResponse) => {
    if (successRate >= 95 && avgResponse < 300) return { grade: 'A', color: 'text-success-600' };
    if (successRate >= 90 && avgResponse < 500) return { grade: 'B', color: 'text-warning-600' };
    if (successRate >= 80) return { grade: 'C', color: 'text-orange-600' };
    return { grade: 'D', color: 'text-danger-600' };
  };

  const performanceGrade = getPerformanceGrade(successRate, results.avgResponseTime);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Test Summary */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <BarChart3 className="h-5 w-5 text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">Test Results</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="metric-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Requests</p>
                <p className="text-2xl font-bold text-primary-600">
                  {results.totalRequests?.toLocaleString() || 0}
                </p>
              </div>
              <Target className="h-8 w-8 text-primary-500" />
            </div>
          </div>

          <div className="metric-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Successful</p>
                <p className="text-2xl font-bold text-success-600">
                  {results.successfulRequests?.toLocaleString() || 0}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-success-500" />
            </div>
          </div>

          <div className="metric-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Failed</p>
                <p className="text-2xl font-bold text-danger-600">
                  {results.failedRequests?.toLocaleString() || 0}
                </p>
              </div>
              <XCircle className="h-8 w-8 text-danger-500" />
            </div>
          </div>

          <div className="metric-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold text-success-600">
                  {successRate.toFixed(1)}%
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-success-500" />
            </div>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Average Response Time</span>
              <span className="font-medium">{results.avgResponseTime?.toFixed(0)}ms</span>
            </div>
            
            <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600">Transaction Per Second</span>
              <span className="font-medium">{results.peakRPS?.toFixed(0)}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Test Duration</span>
              <span className="font-medium">{results.duration}s</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Performance Grade</span>
              <span className={`text-2xl font-bold ${performanceGrade.color}`}>
                {performanceGrade.grade}
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Request Distribution</h3>
          
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          
          <div className="flex justify-center space-x-4 mt-4">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-success-500 rounded-full"></div>
              <span className="text-sm text-gray-600">Successful</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-danger-500 rounded-full"></div>
              <span className="text-sm text-gray-600">Failed</span>
            </div>
          </div>
        </div>
      </div>

      {/* Response Time Distribution */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Response Time Distribution</h3>
        
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={responseTimeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Test Details */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Test Details</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Test ID</p>
            <p className="font-medium">{results.testId}</p>
          </div>
          
          <div>
            <p className="text-sm text-gray-600">Timestamp</p>
            <p className="font-medium">
              {new Date(results.timestamp).toLocaleString()}
            </p>
          </div>
          
          <div>
            <p className="text-sm text-gray-600">Target URL</p>
            <p className="font-medium">{results.targetURL || 'N/A'}</p>
          </div>
          
          <div>
            <p className="text-sm text-gray-600">Test Type</p>
            <p className="font-medium capitalize">{results.testType || 'N/A'}</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default TestResults; 
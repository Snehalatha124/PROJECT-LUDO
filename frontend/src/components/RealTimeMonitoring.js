import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Users, Clock, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const RealTimeMonitoring = ({ currentTest, testResults }) => {
  const [metrics, setMetrics] = useState({
    activeUsers: 0,
    avgResponseTime: 0,
    successRate: 0,
    requestsPerSec: 0
  });

  const [chartData, setChartData] = useState([]);

  // Simulate real-time metrics
  useEffect(() => {
    if (!currentTest) {
      setMetrics({
        activeUsers: 0,
        avgResponseTime: 0,
        successRate: 0,
        requestsPerSec: 0
      });
      return;
    }

    const interval = setInterval(() => {
      setMetrics(prev => ({
        activeUsers: Math.floor(Math.random() * 500) + 100,
        avgResponseTime: Math.floor(Math.random() * 300) + 100,
        successRate: Math.floor(Math.random() * 10) + 90,
        requestsPerSec: Math.floor(Math.random() * 50) + 20
      }));

      // Update chart data
      setChartData(prev => {
        const newData = [...prev, {
          time: new Date().toLocaleTimeString(),
          responseTime: Math.floor(Math.random() * 300) + 100,
          requests: Math.floor(Math.random() * 50) + 20
        }];
        
        // Keep only last 20 data points
        return newData.slice(-20);
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [currentTest]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return 'text-blue-600 bg-blue-100';
      case 'completed':
        return 'text-success-600 bg-success-100';
      case 'failed':
        return 'text-danger-600 bg-danger-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
        return <Activity className="h-4 w-4 animate-pulse" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4" />;
      case 'failed':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">Real-time Monitoring</h2>
        </div>
        
        {currentTest && (
          <div className={`status-indicator ${getStatusColor('running')}`}>
            {getStatusIcon('running')}
            <span className="ml-1">Running</span>
          </div>
        )}
      </div>

      {currentTest ? (
        <div className="space-y-6">
          {/* Live Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <motion.div 
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              className="metric-card"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Users</p>
                  <p className="text-2xl font-bold text-primary-600">
                    {metrics.activeUsers}
                  </p>
                </div>
                <Users className="h-8 w-8 text-primary-500" />
              </div>
            </motion.div>

            <motion.div 
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.1 }}
              className="metric-card"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Avg Response</p>
                  <p className="text-2xl font-bold text-warning-600">
                    {metrics.avgResponseTime}ms
                  </p>
                </div>
                <Clock className="h-8 w-8 text-warning-500" />
              </div>
            </motion.div>

            <motion.div 
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2 }}
              className="metric-card"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Success Rate</p>
                  <p className="text-2xl font-bold text-success-600">
                    {metrics.successRate}%
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-success-500" />
              </div>
            </motion.div>

            <motion.div 
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3 }}
              className="metric-card"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Requests/sec</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {metrics.requestsPerSec}
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-purple-500" />
              </div>
            </motion.div>
          </div>

          {/* Progress Bar */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Test Progress</span>
              <span className="text-sm text-gray-500">100% Complete</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <motion.div
                className="bg-primary-600 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: "100%" }}
                transition={{ duration: 2, ease: "easeInOut" }}
              />
            </div>
          </div>

          {/* Live Chart */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">Response Time Trend</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="responseTime" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Active Test</h3>
          <p className="text-gray-500">
            Start a performance test to see real-time monitoring data
          </p>
        </div>
      )}
    </motion.div>
  );
};

export default RealTimeMonitoring; 
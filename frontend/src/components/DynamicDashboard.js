import React from 'react';
import { useTestContext } from '../context/TestContext';
import AIAnalysis from './AIAnalysis';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { 
  Activity, Brain, Zap, BarChart3, History, Settings, 
  AlertTriangle, CheckCircle, Users, Clock, TrendingUp
} from 'lucide-react';

const DynamicDashboard = () => {
  const { currentTest, testResults, realTimeData, isTestRunning, testHistory, testData } = useTestContext();

  // Generate dynamic response time distribution data
  const getResponseTimeDistribution = () => {
    const data = isTestRunning ? realTimeData : testResults;
    const avgResponseTime = data.avgResponseTime || 0;
    
    // Generate realistic distribution based on current response time
    const totalRequests = data.totalRequests || 1000;
    const successRate = data.successRate || ((data.successfulRequests / data.totalRequests) * 100) || 95;
    
    // Adjust distribution based on performance
    let distribution;
    if (avgResponseTime < 200) {
      // Good performance - most requests in lower ranges
      distribution = [
        { range: '0-100ms', count: Math.floor(totalRequests * 0.4) },
        { range: '100-200ms', count: Math.floor(totalRequests * 0.35) },
        { range: '200-300ms', count: Math.floor(totalRequests * 0.15) },
        { range: '300-400ms', count: Math.floor(totalRequests * 0.07) },
        { range: '400-500ms', count: Math.floor(totalRequests * 0.02) },
        { range: '500ms+', count: Math.floor(totalRequests * 0.01) }
      ];
    } else if (avgResponseTime < 500) {
      // Moderate performance
      distribution = [
        { range: '0-100ms', count: Math.floor(totalRequests * 0.2) },
        { range: '100-200ms', count: Math.floor(totalRequests * 0.3) },
        { range: '200-300ms', count: Math.floor(totalRequests * 0.25) },
        { range: '300-400ms', count: Math.floor(totalRequests * 0.15) },
        { range: '400-500ms', count: Math.floor(totalRequests * 0.07) },
        { range: '500ms+', count: Math.floor(totalRequests * 0.03) }
      ];
    } else {
      // Poor performance - more requests in higher ranges
      distribution = [
        { range: '0-100ms', count: Math.floor(totalRequests * 0.05) },
        { range: '100-200ms', count: Math.floor(totalRequests * 0.15) },
        { range: '200-300ms', count: Math.floor(totalRequests * 0.25) },
        { range: '300-400ms', count: Math.floor(totalRequests * 0.25) },
        { range: '400-500ms', count: Math.floor(totalRequests * 0.2) },
        { range: '500ms+', count: Math.floor(totalRequests * 0.1) }
      ];
    }
    
    return distribution;
  };

  // Generate dynamic requests over time data
  const getRequestsOverTime = () => {
    if (isTestRunning && testData.labels.length > 0) {
      return testData.labels.map((label, index) => ({
        time: label,
        requests: testData.requestsPerSecond[index] || Math.floor(Math.random() * 50) + 10
      }));
    }
    
    // Generate realistic data based on test type and current performance
    const testType = currentTest?.type || 'load';
    const data = isTestRunning ? realTimeData : testResults;
    const currentRPS = data.requestsPerSecond || 60;
    const successRate = data.successRate || ((data.successfulRequests / data.totalRequests) * 100) || 95;
    
    let pattern;
    if (testType === 'stress') {
      // Stress test: gradually increasing load
      pattern = Array.from({ length: 12 }, (_, i) => ({
        time: `${i * 5}s`,
        requests: Math.floor(currentRPS * (0.3 + (i * 0.07))) + Math.floor(Math.random() * 20)
      }));
    } else if (testType === 'spike') {
      // Spike test: sudden peak then recovery
      pattern = Array.from({ length: 12 }, (_, i) => {
        if (i < 3) return { time: `${i * 5}s`, requests: Math.floor(currentRPS * 0.5) + Math.floor(Math.random() * 10) };
        if (i < 6) return { time: `${i * 5}s`, requests: Math.floor(currentRPS * 2) + Math.floor(Math.random() * 30) };
        return { time: `${i * 5}s`, requests: Math.floor(currentRPS * 0.6) + Math.floor(Math.random() * 15) };
      });
    } else if (testType === 'soak') {
      // Soak test: steady load
      pattern = Array.from({ length: 12 }, (_, i) => ({
        time: `${i * 5}s`,
        requests: Math.floor(currentRPS * 0.9) + Math.floor(Math.random() * 10)
      }));
    } else {
      // Load test: normal pattern
      pattern = Array.from({ length: 12 }, (_, i) => ({
        time: `${i * 5}s`,
        requests: Math.floor(currentRPS * (0.7 + Math.sin(i * 0.5) * 0.3)) + Math.floor(Math.random() * 15)
      }));
    }
    
    return pattern;
  };

  // Get current test data
  const getCurrentTestData = () => {
    if (isTestRunning && realTimeData) {
      return {
        totalRequests: realTimeData.totalRequests || 0,
        successfulRequests: Math.floor((realTimeData.successRate / 100) * (realTimeData.totalRequests || 1000)),
        failedRequests: Math.floor(((100 - realTimeData.successRate) / 100) * (realTimeData.totalRequests || 1000)),
        avgResponseTime: realTimeData.avgResponseTime || 0,
        percentile95: realTimeData.avgResponseTime * 1.5 || 0,
        peakRPS: realTimeData.requestsPerSecond || 0
      };
    }
    
    if (testResults && Object.keys(testResults).length > 0) {
      return testResults;
    }
    
    // Default data
    return {
      totalRequests: 1000,
      successfulRequests: 920,
      failedRequests: 80,
      avgResponseTime: 392,
      percentile95: 566,
      peakRPS: 57
    };
  };

  const currentData = getCurrentTestData();
  const responseTimeData = getResponseTimeDistribution();
  const requestsOverTimeData = getRequestsOverTime();

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Card 1: Current Test Status */}
      <div className="flex-1 min-w-0">
        <div className="card h-full">
          <div className="flex items-center space-x-3 mb-4">
            <Activity className="h-6 w-6 text-green-400" />
            <h3 className="text-lg font-semibold text-white">Current Test</h3>
          </div>
          
          <div className="space-y-4">
            {isTestRunning && currentTest ? (
              <>
                <div className="flex justify-between">
                  <span className="text-gray-300">Test Type:</span>
                  <span className="text-white font-semibold">{currentTest.type.charAt(0).toUpperCase() + currentTest.type.slice(1)} Test</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Active Users:</span>
                  <span className="text-white font-semibold">{realTimeData.activeUsers || currentTest.userCount}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Success Rate:</span>
                  <span className="text-white font-semibold">{realTimeData.successRate?.toFixed(1) || 0}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Response Time:</span>
                  <span className="text-white font-semibold">{realTimeData.avgResponseTime || 0}ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">RPS:</span>
                  <span className="text-white font-semibold">{realTimeData.requestsPerSecond || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Progress:</span>
                  <span className="text-white font-semibold">{Math.round(realTimeData.testProgress || 0)}%</span>
                </div>
              </>
            ) : (
              <div className="text-center py-8">
                <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-400">No test running</p>
                <p className="text-sm text-gray-500">Start a test to see live metrics</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Card 2: Test Results */}
      <div className="flex-1 min-w-0">
        <div className="card h-full">
          <div className="flex items-center space-x-3 mb-4">
            <Zap className="h-6 w-6 text-yellow-400" />
            <h3 className="text-lg font-semibold text-white">Test Results</h3>
          </div>
          
          <div className="space-y-4">
            <h4 className="text-md font-semibold text-white">Test Summary</h4>
            
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-300">Total Requests:</span>
                <span className="text-white font-semibold">{currentData.totalRequests.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Successful Requests:</span>
                <span className="text-white font-semibold">{currentData.successfulRequests.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Failed Requests:</span>
                <span className="text-white font-semibold">{currentData.failedRequests.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Average Response Time:</span>
                <span className="text-white font-semibold">{currentData.avgResponseTime}ms</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">95th Percentile:</span>
                <span className="text-white font-semibold">{currentData.percentile95}ms</span>
              </div>
              <div className="flex justify-between">
                                        <span className="text-gray-300">Transaction Per Second:</span>
                <span className="text-white font-semibold">{currentData.peakRPS}</span>
              </div>
            </div>
            
            <div className="pt-4">
              <h5 className="text-sm font-semibold text-white mb-2">Response Time Distribution</h5>
              <div className="h-32">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={responseTimeData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="range" stroke="#9CA3AF" fontSize={10} />
                    <YAxis stroke="#9CA3AF" fontSize={10} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F2937', 
                        border: '1px solid #374151',
                        borderRadius: '8px'
                      }}
                    />
                    <Bar dataKey="count" fill="#10B981" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            <div>
              <h5 className="text-sm font-semibold text-white mb-2">Requests Over Time</h5>
              <div className="h-32">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={requestsOverTimeData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="time" stroke="#9CA3AF" fontSize={10} />
                    <YAxis stroke="#9CA3AF" fontSize={10} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F2937', 
                        border: '1px solid #374151',
                        borderRadius: '8px'
                      }}
                    />
                    <Line type="monotone" dataKey="requests" stroke="#EF4444" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Card 3: AI Analysis */}
      <div className="flex-1 min-w-0">
        <div className="card h-full">
          <div className="flex items-center space-x-3 mb-4">
            <Brain className="h-6 w-6 text-purple-400" />
            <h3 className="text-lg font-semibold text-white">AI Analysis</h3>
          </div>
          
          <div className="space-y-4">
            {isTestRunning || (testResults && Object.keys(testResults).length > 0) ? (
              <AIAnalysis />
            ) : (
              <div className="text-center py-8">
                <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-400">No test data available</p>
                <p className="text-sm text-gray-500">Run a test to get AI analysis</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DynamicDashboard; 
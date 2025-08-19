import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { usePerformanceAPI } from './hooks/usePerformanceAPI';
import { TestProvider } from './context/TestContext';
import HomePage from './components/HomePage';
import PerformancePage from './components/PerformancePage';
import DashboardPage from './components/DashboardPage';
import DynamicDashboard from './components/DynamicDashboard';
import RecentTestHistory from './components/RecentTestHistory';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { 
  Activity, Brain, Zap, BarChart3, History, Settings, 
  Play, Square, RotateCcw, Target, Users, Clock, TrendingUp,
  AlertTriangle, CheckCircle, X, Plus, Download, Upload, Home
} from 'lucide-react';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [testConfig, setTestConfig] = useState({
    type: 'Stress Test',
    url: 'http://localhost:3000',
    users: 500,
    duration: 120,
    rampUp: 10,
    thinkTime: 1000
  });

  const { 
    connectionStatus, 
    loading, 
    error, 
    backendUrl,
    startTest,
    getTestStatus,
    analyzeResults,
    analyzeResultsWithImage,
    listTests,
    getAgentMemory,
    getAgentStatus,
    checkConnection
  } = usePerformanceAPI();



  const handleStartTest = async () => {
    if (!testConfig.url.trim()) {
      alert('Please enter a target URL');
      return;
    }
    
    try {
      const result = await startTest(testConfig);
      console.log('Test started:', result);
    } catch (error) {
      console.error('Failed to start test:', error);
    }
  };

  const handleStopTest = async () => {
    try {
      // Stop test logic would go here
      console.log('Test stopped');
    } catch (error) {
      console.error('Failed to stop test:', error);
    }
  };

  const handleReset = () => {
    setTestConfig({
      type: 'Stress Test',
      url: 'http://localhost:3000',
      users: 500,
      duration: 120,
      rampUp: 10,
      thinkTime: 1000
    });
  };

  const handleNavigate = (page) => {
    setCurrentPage(page);
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-green-500';
      case 'disconnected': return 'text-red-500';
      case 'checking': return 'text-yellow-500';
      default: return 'text-gray-500';
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'Connected';
      case 'disconnected': return 'Disconnected';
      case 'checking': return 'Checking...';
      default: return 'Unknown';
    }
  };

  // Render HomePage if currentPage is 'home'
  if (currentPage === 'home') {
    return <HomePage onNavigate={handleNavigate} />;
  }

  // Render PerformancePage if currentPage is 'performance'
  if (currentPage === 'performance') {
    return <PerformancePage onNavigate={handleNavigate} />;
  }

  // Render DashboardPage if currentPage is 'dashboard'
  if (currentPage === 'dashboard') {
    return <DashboardPage onNavigate={handleNavigate} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Brain className="h-8 w-8 text-purple-400" />
                <h1 className="text-xl font-bold text-white">Performance Testing Suite</h1>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${connectionStatus === 'connected' ? 'bg-green-400' : connectionStatus === 'checking' ? 'bg-yellow-400' : 'bg-red-400'}`}></div>
                <span className={`text-sm ${getConnectionStatusColor()}`}>
                  {getConnectionStatusText()}
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-xs text-gray-400">
                Backend: {backendUrl}
              </div>
              {error && (
                <div className="text-xs text-red-400 bg-red-900/20 px-2 py-1 rounded">
                  {error}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white/5 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button 
              onClick={() => handleNavigate('home')}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 ${currentPage === 'home' ? 'border-purple-400 text-purple-400' : 'border-transparent text-gray-300 hover:text-white'} transition-colors`}
            >
              <Home className="h-5 w-5" />
              <span>Home</span>
            </button>
            <button 
              onClick={() => handleNavigate('performance')}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 ${currentPage === 'performance' ? 'border-purple-400 text-purple-400' : 'border-transparent text-gray-300 hover:text-white'} transition-colors`}
            >
              <Settings className="h-5 w-5" />
              <span>Performance Testing</span>
            </button>
            <button 
              onClick={() => handleNavigate('dashboard')}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 ${currentPage === 'dashboard' ? 'border-purple-400 text-purple-400' : 'border-transparent text-gray-300 hover:text-white'} transition-colors`}
            >
              <BarChart3 className="h-5 w-5" />
              <span>Dashboard</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content - Horizontal Layout */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Main Title */}
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-white mb-4">
            AI-Powered Performance Testing
          </h2>
          <p className="text-gray-300 max-w-2xl mx-auto">
            Configure and execute comprehensive performance tests with real-time monitoring and intelligent analysis.
          </p>
        </div>

        {/* Horizontal Cards Layout */}
        <div className="flex flex-col lg:flex-row gap-6">
          
          {/* Card 1: Test Configuration */}
          <div className="flex-1 min-w-0">
            <div className="card h-full">
              <div className="flex items-center space-x-3 mb-4">
                <Settings className="h-6 w-6 text-blue-400" />
                <h3 className="text-lg font-semibold text-black">Test Configuration</h3>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-black-400 mb-2">Test Type:</label>
                  <div className="space-y-2">
                    {['Load Test', 'Stress Test', 'Spike Test', 'Soak Test'].map((testType) => (
                      <label key={testType} className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="radio"
                          name="testType"
                          value={testType}
                          checked={testConfig.type === testType}
                          onChange={(e) => setTestConfig(prev => ({ ...prev, type: e.target.value }))}
                          className="text-primary-600 focus:ring-primary-500"
                        />
                        <span className="text-gray-700 font-medium">{testType}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Target URL:</label>
                  <input
                    type="url"
                    value={testConfig.url}
                    onChange={(e) => setTestConfig(prev => ({ ...prev, url: e.target.value }))}
                    className="input-field w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Number of Users:</label>
                  <input
                    type="number"
                    value={testConfig.users}
                    onChange={(e) => setTestConfig(prev => ({ ...prev, users: parseInt(e.target.value) || 0 }))}
                    className="input-field w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Duration (seconds):</label>
                  <input
                    type="number"
                    value={testConfig.duration}
                    onChange={(e) => setTestConfig(prev => ({ ...prev, duration: parseInt(e.target.value) || 0 }))}
                    className="input-field w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Ramp-up Time (seconds):</label>
                  <input
                    type="number"
                    value={testConfig.rampUp}
                    onChange={(e) => setTestConfig(prev => ({ ...prev, rampUp: parseInt(e.target.value) || 0 }))}
                    className="input-field w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Think Time (ms):</label>
                  <input
                    type="number"
                    value={testConfig.thinkTime}
                    onChange={(e) => setTestConfig(prev => ({ ...prev, thinkTime: parseInt(e.target.value) || 0 }))}
                    className="input-field w-full"
                  />
                </div>

                <div className="flex space-x-2 pt-4">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleStartTest}
                    disabled={loading}
                    className="btn-primary flex-1"
                  >
                    <Play className="h-4 w-4 mr-2" />
                    Start Test
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleStopTest}
                    className="btn-secondary"
                  >
                    <Square className="h-4 w-4 mr-2" />
                    Stop Test
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleReset}
                    className="btn-secondary"
                  >
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Reset
                  </motion.button>
                </div>
              </div>
            </div>
          </div>

          <DynamicDashboard />

          <RecentTestHistory />
        </div>
      </main>
    </div>
  );
}

const AppWrapper = () => {
  return (
    <TestProvider>
      <App />
    </TestProvider>
  );
};

export default AppWrapper; 
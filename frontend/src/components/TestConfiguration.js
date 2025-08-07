import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Settings, Target, Users, Clock, Zap } from 'lucide-react';

const TestConfiguration = ({ onStartTest, loading }) => {
  const [testConfig, setTestConfig] = useState({
    type: 'Load Test',
    url: 'http://localhost:3000',
    users: 100,
    duration: 600, // 10 minutes in seconds
    rampUp: 10,
    thinkTime: 1000
  });

  const testTypes = [
    { value: 'Load Test', label: 'Load Test', description: 'Normal load testing with steady user count' },
    { value: 'Stress Test', label: 'Stress Test', description: 'High load testing to find breaking point' },
    { value: 'Spike Test', label: 'Spike Test', description: 'Sudden load spikes to test system resilience' },
    { value: 'Soak Test', label: 'Soak Test', description: 'Extended duration testing for stability' }
  ];

  const presetConfigs = [
    {
      name: 'Quick Load Test',
      config: { type: 'Load Test', users: 50, duration: 300, rampUp: 5, thinkTime: 500 }
    },
    {
      name: 'Standard Load Test',
      config: { type: 'Load Test', users: 100, duration: 600, rampUp: 10, thinkTime: 1000 }
    },
    {
      name: 'Stress Test',
      config: { type: 'Stress Test', users: 200, duration: 900, rampUp: 15, thinkTime: 500 }
    },
    {
      name: 'Spike Test',
      config: { type: 'Spike Test', users: 150, duration: 300, rampUp: 5, thinkTime: 100 }
    },
    {
      name: 'Soak Test',
      config: { type: 'Soak Test', users: 75, duration: 1800, rampUp: 15, thinkTime: 2000 }
    }
  ];

  const handleInputChange = (field, value) => {
    setTestConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handlePresetSelect = (preset) => {
    setTestConfig(prev => ({
      ...prev,
      ...preset.config
    }));
  };

  const handleStartTest = () => {
    if (!testConfig.url.trim()) {
      alert('Please enter a target URL');
      return;
    }
    onStartTest(testConfig);
  };

  const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const parseDuration = (durationStr) => {
    const parts = durationStr.split(' ');
    let totalSeconds = 0;
    parts.forEach(part => {
      if (part.includes('m')) {
        totalSeconds += parseInt(part) * 60;
      } else if (part.includes('s')) {
        totalSeconds += parseInt(part);
      }
    });
    return totalSeconds;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-center space-x-3">
          <Settings className="h-6 w-6 text-blue-400" />
          <div>
            <h2 className="text-xl font-semibold text-white">JMeter Test Configuration</h2>
            <p className="text-gray-400">Configure your performance test parameters</p>
          </div>
        </div>
      </div>

      {/* Test Type Selection */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Test Type</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {testTypes.map((testType) => (
            <motion.div
              key={testType.value}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                testConfig.type === testType.value
                  ? 'border-blue-400 bg-blue-900/20'
                  : 'border-gray-600 bg-gray-800/20 hover:border-gray-500'
              }`}
              onClick={() => handleInputChange('type', testType.value)}
            >
              <div className="flex items-center space-x-3">
                <Target className="h-5 w-5 text-blue-400" />
                <div>
                  <h4 className="font-semibold text-white">{testType.label}</h4>
                  <p className="text-sm text-gray-400">{testType.description}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Preset Configurations */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Quick Presets</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {presetConfigs.map((preset) => (
            <motion.button
              key={preset.name}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="p-3 rounded-lg border border-gray-600 bg-gray-800/20 hover:border-gray-500 text-left"
              onClick={() => handlePresetSelect(preset)}
            >
              <h4 className="font-semibold text-white text-sm">{preset.name}</h4>
              <p className="text-xs text-gray-400">
                {preset.config.users} users, {formatDuration(preset.config.duration)}
              </p>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Test Parameters */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Test Parameters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Target URL */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Target URL
            </label>
            <input
              type="url"
              value={testConfig.url}
              onChange={(e) => handleInputChange('url', e.target.value)}
              placeholder="https://example.com"
              className="input-field w-full"
            />
          </div>

          {/* Number of Users */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Number of Users
            </label>
            <div className="relative">
              <Users className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="number"
                value={testConfig.users}
                onChange={(e) => handleInputChange('users', parseInt(e.target.value) || 0)}
                min="1"
                max="1000"
                className="input-field w-full pl-10"
              />
            </div>
          </div>

          {/* Test Duration */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Test Duration
            </label>
            <div className="relative">
              <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={formatDuration(testConfig.duration)}
                onChange={(e) => handleInputChange('duration', parseDuration(e.target.value))}
                placeholder="10m 30s"
                className="input-field w-full pl-10"
              />
            </div>
            <p className="text-xs text-gray-400 mt-1">
              Format: 10m 30s (minutes and seconds)
            </p>
          </div>

          {/* Ramp-up Time */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Ramp-up Time (seconds)
            </label>
            <input
              type="number"
              value={testConfig.rampUp}
              onChange={(e) => handleInputChange('rampUp', parseInt(e.target.value) || 0)}
              min="1"
              max="300"
              className="input-field w-full"
            />
          </div>

          {/* Think Time */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Think Time (milliseconds)
            </label>
            <div className="relative">
              <Zap className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="number"
                value={testConfig.thinkTime}
                onChange={(e) => handleInputChange('thinkTime', parseInt(e.target.value) || 0)}
                min="0"
                max="10000"
                className="input-field w-full pl-10"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Test Summary */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Test Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">{testConfig.type}</div>
            <div className="text-sm text-gray-400">Test Type</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">{testConfig.users}</div>
            <div className="text-sm text-gray-400">Users</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-400">{formatDuration(testConfig.duration)}</div>
            <div className="text-sm text-gray-400">Duration</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-400">{testConfig.rampUp}s</div>
            <div className="text-sm text-gray-400">Ramp-up</div>
          </div>
        </div>
      </div>

      {/* Start Test Button */}
      <div className="flex justify-center">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleStartTest}
          disabled={loading || !testConfig.url.trim()}
          className="btn-primary text-lg px-8 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Starting Test...</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <Play className="h-5 w-5" />
              <span>Start JMeter Test</span>
            </div>
          )}
        </motion.button>
      </div>

      {/* Test Type Information */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Test Type Information</h3>
        <div className="space-y-3">
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <h4 className="font-semibold text-white">Load Test</h4>
              <p className="text-sm text-gray-400">
                Tests system performance under normal expected load. Good for baseline performance measurement.
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-red-400 rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <h4 className="font-semibold text-white">Stress Test</h4>
              <p className="text-sm text-gray-400">
                Tests system behavior beyond normal capacity to find breaking points and failure modes.
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-orange-400 rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <h4 className="font-semibold text-white">Spike Test</h4>
              <p className="text-sm text-gray-400">
                Tests system response to sudden, extreme load spikes to verify resilience and recovery.
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <h4 className="font-semibold text-white">Soak Test</h4>
              <p className="text-sm text-gray-400">
                Tests system stability over extended periods to identify memory leaks and degradation.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestConfiguration; 
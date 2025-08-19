import React from 'react';
import { motion } from 'framer-motion';
import { 
  Play, BarChart3, Users, Flame, Zap, Clock, 
  Brain, Rocket, Shield, Home, Settings, Activity
} from 'lucide-react';

const HomePage = ({ onNavigate }) => {
  const testTypes = [
    {
      icon: Users,
      title: "Load Testing",
      description: "Simulate normal user loads to verify your application's performance under expected conditions. Identify bottlenecks before they become problems.",
      color: "teal"
    },
    {
      icon: Flame,
      title: "Stress Testing", 
      description: "Push your application beyond its limits to find breaking points. Discover maximum capacity and failure thresholds.",
      color: "red"
    },
    {
      icon: Zap,
      title: "Spike Testing",
      description: "Test sudden traffic surges to ensure your system can handle unexpected load spikes without crashing.",
      color: "yellow"
    },
    {
      icon: Clock,
      title: "Soak Testing",
      description: "Run extended tests to identify memory leaks, resource exhaustion, and long-term stability issues.",
      color: "teal"
    }
  ];

  const features = [
    {
      icon: Brain,
      title: "AI-Powered",
      description: "Intelligent test scenario generation and analysis.",
      color: "light-green"
    },
    {
      icon: Rocket,
      title: "Fast & Efficient", 
      description: "Quick setup and rapid test execution.",
      color: "pink"
    },
    {
      icon: Shield,
      title: "Reliable",
      description: "Accurate results you can trust.",
      color: "light-blue"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-400 via-purple-500 to-purple-800">
      {/* Header */}
      <header className="relative z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                <Brain className="w-5 h-5 text-purple-600" />
              </div>
                              <h1 className="text-2xl font-bold text-white">Loadosaurus AI Agent</h1>
            </div>
            
            {/* Navigation */}
            <nav className="flex space-x-6">
              <button 
                onClick={() => onNavigate('home')}
                className="flex items-center space-x-2 text-white hover:text-purple-200 transition-colors"
              >
                <Home className="w-5 h-5" />
                <span>Home</span>
              </button>
              <button 
                onClick={() => onNavigate('performance')}
                className="flex items-center space-x-2 text-white hover:text-purple-200 transition-colors"
              >
                <Settings className="w-5 h-5" />
                <span>Performance Testing</span>
              </button>
              <button 
                onClick={() => onNavigate('dashboard')}
                className="flex items-center space-x-2 text-white hover:text-purple-200 transition-colors"
              >
                <BarChart3 className="w-5 h-5" />
                <span>Dashboard</span>
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 text-center py-20">
        <div className="container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
                         {/* AI Agent Picture */}
             <motion.div
               initial={{ scale: 0 }}
               animate={{ scale: 1 }}
               transition={{ duration: 0.8, delay: 0.2 }}
               className="mb-8"
             >
               <div className="relative inline-block">
                                                                                                                                               {/* AI Robot - Exact Match to Image */}
                    <div className="w-64 h-64 bg-blue-200 rounded-full flex items-center justify-center shadow-2xl relative">
                      {/* Main Body - Large White Sphere with Inner Shadow */}
                      <div className="w-48 h-48 bg-white rounded-full shadow-lg flex items-center justify-center relative">
                        {/* Inner Shadow Effect */}
                        <div className="absolute inset-2 bg-white rounded-full shadow-inner"></div>
                        
                        {/* AI Emblem - Blue Circle on Chest */}
                        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center shadow-lg">
                          <span className="text-white text-lg font-bold">AI</span>
                        </div>
                      </div>
                      
                      {/* Head - Small Rounded White Shape on Top */}
                      <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 w-20 h-20 bg-white rounded-full shadow-lg flex flex-col items-center justify-center">
                        {/* Eyes - Light Blue Ovals */}
                        <div className="flex space-x-3 mb-1">
                          <div className="w-5 h-3 bg-blue-300 rounded-full"></div>
                          <div className="w-5 h-3 bg-blue-300 rounded-full"></div>
                        </div>
                        
                        {/* Mouth/Sensor - Light Gray Horizontal Bar */}
                        <div className="w-8 h-1 bg-gray-300 rounded-full"></div>
                      </div>
                      
                      {/* Subtle Depth Effect */}
                      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-blue-300/20 rounded-full"></div>
                    </div>
                 
                 {/* Status Indicators */}
                 <div className="absolute -top-2 -right-2 w-8 h-8 bg-green-400 rounded-full flex items-center justify-center animate-pulse">
                   <div className="w-3 h-3 bg-white rounded-full"></div>
                 </div>
                 <div className="absolute -bottom-1 -left-1 w-6 h-6 bg-yellow-400 rounded-full animate-bounce"></div>
                 <div className="absolute top-1/2 -left-8 w-3 h-3 bg-blue-400 rounded-full animate-ping"></div>
                 <div className="absolute top-1/2 -right-8 w-3 h-3 bg-purple-400 rounded-full animate-pulse"></div>
               </div>
             </motion.div>
            
            <h1 className="text-6xl font-bold text-white mb-6">
              Welcome to Loadosaurus
            </h1>
            <p className="text-xl text-white/90 max-w-3xl mx-auto mb-12 leading-relaxed">
              Your intelligent AI companion for comprehensive performance testing. Simulate real-world scenarios with Load, Stress, Spike, and Soak testing to ensure your applications perform flawlessly under any conditions.
            </p>
            
            {/* Call to Action Buttons */}
            <div className="flex justify-center space-x-6 mb-16">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onNavigate('performance')}
                className="flex items-center space-x-3 bg-purple-600 hover:bg-purple-700 text-white px-8 py-4 rounded-lg font-semibold transition-colors"
              >
                <Play className="w-5 h-5" />
                <span>Start Testing</span>
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onNavigate('dashboard')}
                className="flex items-center space-x-3 bg-purple-600 hover:bg-purple-700 text-white px-8 py-4 rounded-lg font-semibold transition-colors"
              >
                <BarChart3 className="w-5 h-5" />
                <span>View Results</span>
              </motion.button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Test Type Cards */}
      <section className="relative z-10 pb-20">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {testTypes.map((test, index) => (
              <motion.div
                key={test.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300"
              >
                <div className="text-center">
                  <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full mb-4 ${
                    test.color === 'teal' ? 'bg-teal-500' :
                    test.color === 'red' ? 'bg-red-500' :
                    test.color === 'yellow' ? 'bg-yellow-500' : 'bg-teal-500'
                  }`}>
                    <test.icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3">{test.title}</h3>
                  <p className="text-white/80 text-sm leading-relaxed">{test.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 py-20">
        <div className="container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20"
          >
            <h2 className="text-3xl font-bold text-white text-center mb-12">Why Choose Loadosaurus?</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.6, delay: 0.6 + index * 0.1 }}
                  className="text-center"
                >
                  <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full mb-4 ${
                    feature.color === 'light-green' ? 'bg-green-400' :
                    feature.color === 'pink' ? 'bg-pink-400' :
                    feature.color === 'light-blue' ? 'bg-blue-400' : 'bg-green-400'
                  }`}>
                    <feature.icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                  <p className="text-white/80">{feature.description}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Call to Action Section */}
      <section className="relative z-10 py-20">
        <div className="container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20 text-center"
          >
            <h2 className="text-3xl font-bold text-white mb-6">Ready to Get Started?</h2>
            <p className="text-white/90 text-lg mb-8 max-w-2xl mx-auto">
              Join thousands of developers who trust Loadosaurus for their performance testing needs. Get started in minutes with our intuitive interface and powerful AI capabilities.
            </p>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onNavigate('performance')}
              className="flex items-center space-x-3 bg-green-600 hover:bg-green-700 text-white px-8 py-4 rounded-lg font-semibold transition-colors mx-auto"
            >
              <Play className="w-5 h-5" />
              <span>Launch Performance Tests</span>
            </motion.button>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default HomePage; 
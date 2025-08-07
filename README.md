# Ludo Performance Testing Suite

An AI-powered performance testing suite with intelligent analysis, real-time monitoring, and automated recommendations. Built with React frontend and Flask backend, designed for Vercel deployment. Now featuring **OpenRouter AI integration** with **Google Gemini 2.0 Flash** for enhanced text and image analysis capabilities.

## 🚀 Features

### AI-Powered Analysis
- **Intelligent Performance Assessment**: AI agent analyzes test results and provides insights
- **Root Cause Analysis**: Identifies performance bottlenecks and issues
- **Automated Recommendations**: Suggests optimizations and improvements
- **Memory & Learning**: AI agent learns from previous test results
- **Auto-Retry Logic**: Automatically retries tests based on AI recommendations
- **🆕 Image Analysis**: Analyze performance with visual context using OpenRouter + Gemini 2.0 Flash
- **🆕 Multi-AI Provider**: Support for both Google Gemini and OpenRouter APIs

### Performance Testing
- **Multiple Test Types**: Stress, Load, Spike, and Soak testing
- **Real-time Monitoring**: Live progress tracking and metrics visualization
- **Comprehensive Metrics**: Response times, success rates, throughput analysis
- **Test History**: Complete audit trail of all performance tests
- **Configurable Parameters**: Customizable test duration, users, ramp-up times

### Modern UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live charts and progress indicators
- **Beautiful Animations**: Smooth transitions and visual feedback
- **Dark Theme**: Modern dark interface with purple accents
- **Intuitive Navigation**: Easy-to-use tab-based interface

## 🏗️ Architecture

```
LUDO/
├── backend/                 # Flask API Server
│   ├── app.py              # Main application with AI agent
│   ├── requirements.txt    # Python dependencies
│   ├── vercel.json         # Vercel deployment config
│   └── env.example         # Environment template
├── frontend/               # React Frontend
│   ├── src/components/     # React components
│   ├── src/hooks/          # API hooks
│   ├── vercel.json         # Vercel deployment config
│   ├── env.example         # Environment template
│   └── package.json        # Node.js dependencies
├── setup.py               # Automated setup script
├── start.bat              # Windows startup script
├── start.sh               # Unix startup script
└── README.md              # This file
```

## 🛠️ Technology Stack

### Backend
- **Flask**: Python web framework
- **Google Gemini AI**: AI-powered analysis
- **🆕 OpenRouter API**: Alternative AI provider with Gemini 2.0 Flash
- **🆕 OpenAI Client**: Integration with OpenRouter
- **Flask-CORS**: Cross-origin resource sharing
- **python-dotenv**: Environment variable management
- **requests**: HTTP client library

### Frontend
- **React**: JavaScript framework
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library
- **Recharts**: Charting library
- **Axios**: HTTP client
- **Lucide React**: Icon library

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LUDO
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Configure environment variables**
   ```bash
   # Backend (.env file in backend/ directory)
   cp backend/env.example backend/.env
   # Edit backend/.env and add your AI API keys
   
   # Frontend (.env file in frontend/ directory)
   cp frontend/env.example frontend/.env
   # Edit frontend/.env if needed
   ```

4. **Start the application**
   ```bash
   # Windows
   start.bat
   
   # Unix/Linux
   ./start.sh
   ```

5. **Open your browser**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

### Vercel Deployment

#### Backend Deployment

1. **Deploy to Vercel**
   ```bash
   cd backend
   vercel
   ```

2. **Configure environment variables in Vercel dashboard**
   ```
   GEMINI_API_KEY=your-gemini-api-key
   OPENROUTER_API_KEY=your-openrouter-api-key
   FLASK_ENV=production
   FLASK_DEBUG=false
   BACKEND_URL=https://your-backend.vercel.app
   FRONTEND_URL=https://your-frontend.vercel.app
   ```

#### Frontend Deployment

1. **Deploy to Vercel**
   ```bash
   cd frontend
   vercel
   ```

2. **Configure environment variables in Vercel dashboard**
   ```
   REACT_APP_BACKEND_URL=https://your-backend.vercel.app
   REACT_APP_ENV=production
   ```

## 📋 Environment Variables

### Backend (.env)

```bash
# Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key-here

# OpenRouter AI Configuration (Alternative AI Provider)
OPENROUTER_API_KEY=your-openrouter-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_SITE_URL=https://your-site-url.com
OPENROUTER_SITE_NAME=Ludo Performance Suite

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=true
HOST=0.0.0.0
PORT=5000

# Test Configuration
MAX_CONCURRENT_TESTS=10
DEFAULT_TEST_DURATION=60
DEFAULT_NUM_USERS=100

# Deployment Configuration
BACKEND_URL=http://localhost:5000
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env)

```bash
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:5000

# Environment
REACT_APP_ENV=development

# Feature flags
REACT_APP_ENABLE_AI_ANALYSIS=true
REACT_APP_ENABLE_REAL_TIME_MONITORING=true
```

## 🔌 API Endpoints

### Core Endpoints
- `GET /` - API information and status
- `GET /health` - Health check
- `POST /test/start` - Start a new performance test
- `GET /test/:id/status` - Get test status and progress
- `GET /tests` - List all active tests
- `GET /tests/history` - Get test history

### AI Analysis Endpoints
- `POST /analyze` - Analyze test results with AI
- `🆕 POST /analyze/image` - Analyze test results with image support
- `GET /agent/memory` - Get AI agent's analysis memory
- `GET /agent/status` - Get AI agent status and capabilities

## 🎨 UI Components

### Dashboard
- Overview of system status
- Quick access to main features
- Connection status indicator

### Test Configuration
- Test type selection (Stress, Load, Spike, Soak)
- URL and parameter configuration
- Quick preset configurations
- Start/Stop/Reset controls

### Real-time Monitoring
- Live progress tracking
- Real-time metrics display
- Response time charts
- Success rate indicators

### Test Results
- Comprehensive test summary
- Performance metrics visualization
- Request distribution charts
- Performance grade calculation

### AI Analysis
- AI-powered insights
- Problem identification
- Root cause analysis
- Actionable recommendations
- Confidence scoring
- **🆕 Image Analysis**: Add screenshots/charts for enhanced analysis
- **🆕 AI Provider Info**: Shows which AI service is being used

### Test History
- Complete test audit trail
- Historical performance trends
- Test result comparison
- Export capabilities

## 🤖 AI Agent Features

### Intelligent Analysis
- **Context-Aware Assessment**: Considers multiple performance factors
- **Problem Identification**: Detects performance issues and bottlenecks
- **Root Cause Analysis**: Identifies underlying causes of problems
- **Recommendation Generation**: Provides specific, actionable advice

### Memory & Learning
- **Historical Context**: Learns from previous test results
- **Pattern Recognition**: Identifies recurring performance patterns
- **Adaptive Analysis**: Improves recommendations over time
- **Knowledge Retention**: Maintains analysis history

### Auto-Retry Logic
- **Smart Decision Making**: Determines when retry tests are needed
- **Conditional Triggers**: Retries based on specific criteria
- **Parameter Optimization**: Adjusts test parameters for retries
- **Success Prediction**: Estimates retry test success probability

### 🆕 Multi-AI Provider Support
- **Google Gemini**: Primary AI provider with text analysis
- **OpenRouter + Gemini 2.0 Flash**: Alternative provider with image analysis
- **Automatic Fallback**: Intelligent provider selection based on API availability
- **Enhanced Capabilities**: Image analysis for visual performance context

## 📊 Performance Features

### Test Types
- **Stress Test**: Maximum load testing
- **Load Test**: Normal load validation
- **Spike Test**: Sudden load spikes
- **Soak Test**: Extended duration testing

### Metrics Tracked
- **Response Times**: Average, median, 95th percentile
- **Success Rates**: Overall and per-interval success rates
- **Throughput**: Requests per second (RPS)
- **Error Rates**: Failed request analysis
- **Resource Utilization**: System resource monitoring

### Real-time Monitoring
- **Live Progress**: Real-time test progress updates
- **Instant Metrics**: Immediate performance feedback
- **Visual Indicators**: Charts and graphs for data visualization
- **Alert System**: Performance threshold notifications

## 🔒 Security

### Environment Variables
- Secure API key management
- Environment-specific configurations
- No hardcoded secrets

### CORS Configuration
- Proper cross-origin resource sharing
- Environment-specific CORS settings
- Secure API access

### Input Validation
- Request parameter validation
- Data sanitization
- Error handling

## 📈 Monitoring & Logging

### Application Monitoring
- Health check endpoints
- Performance metrics tracking
- Error rate monitoring
- Response time monitoring

### AI Agent Monitoring
- Analysis success rates
- Memory usage tracking
- Recommendation accuracy
- Learning progress
- **🆕 AI Provider Status**: Monitor which AI service is active

## 🛠️ Development

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Development Setup
1. Install Python dependencies: `pip install -r backend/requirements.txt`
2. Install Node.js dependencies: `npm install` (in frontend directory)
3. Set up environment variables
4. Start development servers

### Code Structure
- **Modular Architecture**: Separate frontend and backend
- **Component-Based**: Reusable React components
- **Hook-Based**: Custom React hooks for API integration
- **Service-Oriented**: Clean separation of concerns

## 🐛 Troubleshooting

### Common Issues

#### Backend Connection Issues
- Check if backend server is running
- Verify environment variables
- Check CORS configuration
- Review network connectivity

#### AI Analysis Failures
- Verify AI API keys are set (Gemini or OpenRouter)
- Check API quota and limits
- Review error logs
- Test with fallback analysis

#### Frontend Build Issues
- Clear node_modules and reinstall
- Check Node.js version compatibility
- Verify environment variables
- Review build logs

### Debug Mode
- Enable debug logging in backend
- Check browser console for frontend errors
- Review network requests
- Monitor API responses

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Write meaningful commit messages
- Add documentation for new features

### Testing
- Test both frontend and backend changes
- Verify environment variable handling
- Test deployment configurations
- Validate AI agent functionality

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for intelligent analysis capabilities
- **🆕 OpenRouter** for providing access to Gemini 2.0 Flash with image analysis
- Vercel for seamless deployment platform
- React and Flask communities for excellent frameworks
- Open source contributors for various libraries used

---

**Built with ❤️ for performance testing and AI-powered insights**

**🆕 Now featuring OpenRouter AI integration with image analysis capabilities!** #   P R O J E C T - L U D O  
 
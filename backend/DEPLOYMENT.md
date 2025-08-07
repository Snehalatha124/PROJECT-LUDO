# LUDO Backend Deployment Guide

## Render Deployment Configuration

### Service Settings:
- **Name:** `ludo-backend`
- **Environment:** `Python`
- **Region:** `Oregon (US West)` (or your preferred region)
- **Instance Type:** `Free` (for testing) or `Starter` ($7/month) for production
- **Root Directory:** `backend` (leave empty if deploying from backend directory)
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`

### Environment Variables:
Set these in your Render dashboard:

#### Required API Keys:
```
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

#### Optional Configuration:
```
FLASK_ENV=production
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_SITE_URL=https://your-frontend-url.onrender.com
OPENROUTER_SITE_NAME=Ludo Performance Suite
BACKEND_URL=https://your-backend-service.onrender.com
FRONTEND_URL=https://your-frontend-service.onrender.com
```

### Deployment Steps:

1. **Create New Web Service** in Render
2. **Connect GitHub Repository:** `https://github.com/Snehalatha124/PROJECT-LUDO.git`
3. **Set Root Directory:** `backend`
4. **Configure Environment Variables** (see above)
5. **Deploy**

### Features:
- ✅ Flask API with CORS support
- ✅ Socket.IO for real-time communication
- ✅ AI-powered performance analysis
- ✅ Simulated JMeter testing (cloud-compatible)
- ✅ Health check endpoint
- ✅ Production-ready with Gunicorn

### API Endpoints:
- `GET /` - Home page
- `GET /health` - Health check
- `POST /analyze` - Performance analysis
- `POST /test/start` - Start performance test
- `GET /test/{id}/status` - Get test status
- `POST /test/{id}/stop` - Stop test
- `GET /tests` - List all tests
- `GET /tests/history` - Get test history
- `GET /agent/status` - AI agent status

### Notes:
- JMeter functionality is simulated in cloud deployment
- Real JMeter requires system-level installation (not available on Render)
- All AI analysis features work normally
- Socket.IO supports real-time updates

# LUDO Backend Deployment Guide

## Render Deployment Configuration

### Service Settings:
- **Name:** `PROJECT-LUDO`
- **Environment:** `Python`
- **Region:** `Singapore (Southeast Asia)`
- **Instance Type:** `Free` (0.1 CPU, 512 MB)
- **Root Directory:** `backend` ⚠️ **IMPORTANT: Set this to `backend`**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`

### Environment Variables:
Set these in your Render dashboard:

#### Required API Keys:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

#### CORS Configuration (Optional - defaults to allow all):
```
CORS_ORIGINS=https://your-frontend-url.vercel.app,https://localhost:3000
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_HEADERS=Content-Type,Authorization
```

#### Optional Configuration:
```
FLASK_ENV=production
BACKEND_URL=https://project-ludo.onrender.com
FRONTEND_URL=https://your-frontend-url.vercel.app
```

### Deployment Steps:

1. **Create New Web Service** in Render
2. **Connect GitHub Repository:** `https://github.com/Snehalatha124/PROJECT-LUDO.git`
3. **Set Root Directory:** `backend` ⚠️ **CRITICAL**
4. **Configure Environment Variables** (see above)
5. **Deploy**

### Current Render Settings:
- ✅ **Name:** PROJECT-LUDO
- ✅ **Region:** Singapore (Southeast Asia)
- ✅ **Instance Type:** Free
- ✅ **Repository:** https://github.com/Snehalatha124/PROJECT-LUDO.git
- ✅ **Branch:** main
- ✅ **Build Command:** pip install -r requirements.txt
- ✅ **Start Command:** gunicorn app:app --bind 0.0.0.0:$PORT
- ⚠️ **Root Directory:** NEEDS TO BE SET TO `backend`

### Features:
- ✅ Flask API with CORS support
- ✅ Socket.IO for real-time communication
- ✅ AI-powered performance analysis (Gemini Pro)
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

### AI Integration:
- **Model:** Google Gemini Pro
- **Capabilities:** Performance analysis, problem identification, recommendations
- **Features:** JSON-structured responses, confidence scoring, severity assessment

### Notes:
- JMeter functionality is simulated in cloud deployment
- Real JMeter requires system-level installation (not available on Render)
- All AI analysis features work with Gemini Pro
- Socket.IO supports real-time updates

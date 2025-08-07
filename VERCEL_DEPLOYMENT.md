# LUDO Project - Vercel Deployment Guide

## Frontend Deployment (React App)

### 1. Project Structure
```
LUDO/
├── frontend/          # React application
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vercel.json
├── backend/           # Flask API (deploy separately)
└── vercel.json        # Root configuration
```

### 2. Vercel Configuration

#### Root vercel.json (already configured):
```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "frontend/build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "outputDirectory": "frontend/build"
}
```

### 3. Environment Variables

Set these in your Vercel dashboard:

#### Required:
```
REACT_APP_BACKEND_URL=https://your-backend-url.vercel.app
```

#### Optional:
```
REACT_APP_ENV=production
REACT_APP_ENABLE_AI_ANALYSIS=true
REACT_APP_ENABLE_REAL_TIME_MONITORING=true
REACT_APP_ENABLE_SOCKET_IO=true
```

### 4. Deployment Steps

1. **Connect to GitHub:**
   - Go to Vercel dashboard
   - Import project from GitHub
   - Select: `https://github.com/Snehalatha124/PROJECT-LUDO.git`

2. **Configure Build Settings:**
   - **Framework Preset:** Other
   - **Root Directory:** `frontend` (or leave empty to use root config)
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`

3. **Set Environment Variables:**
   - Add the environment variables listed above

4. **Deploy:**
   - Click "Deploy"

### 5. Backend Deployment

For the Flask backend, you have two options:

#### Option A: Deploy Backend to Vercel (Serverless)
- Create a separate Vercel project for the backend
- Use the `backend/` directory
- Configure as a Python function

#### Option B: Deploy Backend to Render (Recommended)
- Use the existing Render configuration
- Set environment variables in Render dashboard
- Connect frontend to Render backend URL

### 6. Troubleshooting

#### Common Issues:

1. **"Could not find index.html"**
   - ✅ Fixed: Root vercel.json now points to frontend directory

2. **Build fails**
   - Check that all dependencies are in frontend/package.json
   - Ensure Node.js version is compatible

3. **API calls fail**
   - Verify REACT_APP_BACKEND_URL is set correctly
   - Check CORS configuration in backend

4. **Environment variables not working**
   - Ensure variables start with `REACT_APP_`
   - Redeploy after adding variables

### 7. Post-Deployment

1. **Test the application:**
   - Navigate to your Vercel URL
   - Test all features
   - Check console for errors

2. **Update backend URL:**
   - If using Render backend, update REACT_APP_BACKEND_URL
   - If using Vercel backend, use the Vercel backend URL

3. **Monitor performance:**
   - Check Vercel analytics
   - Monitor API response times

### 8. Custom Domain (Optional)

1. Add custom domain in Vercel dashboard
2. Configure DNS settings
3. Update environment variables if needed

## Success! 🎉

Your LUDO frontend should now deploy successfully on Vercel!

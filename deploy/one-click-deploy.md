# 🚀 One-Click DigitalOcean Deployment

## Deploy Pet Ingredient Safety Checker in 60 seconds

### Option 1: Deploy to App Platform (Recommended)

[![Deploy to DO](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/your-username/pet-ingredient-safety-checker)

**Steps:**
1. Click the "Deploy to DO" button above
2. Connect your GitHub repository
3. Set environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `SECRET_KEY`: Generate at https://randomkeygen.com/
4. Click "Create Resources"
5. Wait 3-5 minutes for deployment
6. Your app will be live at: `https://your-app-name-xxxxx.ondigitalocean.app`

### Option 2: Manual App Platform Deployment

1. **Go to DigitalOcean Control Panel**: https://cloud.digitalocean.com/apps
2. **Click "Create App"**
3. **Connect Repository**: Choose your Git repository
4. **Configure App**:
   - Name: `pet-ingredient-safety-checker`
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `gunicorn --bind 0.0.0.0:$PORT backend.app:app`
5. **Add Database**: PostgreSQL 15, Basic plan
6. **Set Environment Variables**:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   DATABASE_URL=postgresql://... (auto-configured)
   FLASK_ENV=production
   SECRET_KEY=your_secret_key_here
   ```
7. **Deploy**: Click "Create Resources"

### Your Live Endpoint Will Be:
```
https://pet-ingredient-safety-checker-xxxxx.ondigitalocean.app
```

The `xxxxx` will be a unique identifier assigned by DigitalOcean.

### Alternative: Use Our Demo Instance

If you just want to see the application running immediately, I can provide you with a demo endpoint using a free hosting service:

**Demo URL**: `https://pet-safety-demo.herokuapp.com` (example)

This would be a temporary demo instance for testing purposes.

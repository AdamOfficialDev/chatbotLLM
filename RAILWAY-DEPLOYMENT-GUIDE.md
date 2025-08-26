# Railway Deployment Guide - LLM Chat Application

## Quick Deploy to Railway (Tanpa Ribet!)

### Method 1: Simple Nixpacks Deployment (Recommended)

1. **Connect to Railway:**
   - Go to [railway.app](https://railway.app)
   - Connect your GitHub repository
   - Import this project

2. **Configure Environment Variables:**
   Add these in Railway dashboard under Variables:
   ```
   EMERGENT_LLM_KEY=your_emergent_universal_key_here
   MONGO_URL=your_mongodb_connection_string
   NODE_ENV=production
   ```

3. **Railway Configuration:**
   - Railway will automatically detect `nixpacks.toml`
   - Uses Nixpacks builder (faster than Docker)
   - Automatically installs Python + Node.js

4. **MongoDB Setup Options:**
   
   **Option A: MongoDB Atlas (Recommended)**
   - Create free cluster at [mongodb.com](https://cloud.mongodb.com)
   - Get connection string
   - Add to Railway as `MONGO_URL`

   **Option B: Railway MongoDB Plugin**
   - Add MongoDB plugin in Railway dashboard
   - Copy the connection string to `MONGO_URL`

5. **Deploy:**
   - Push to GitHub
   - Railway auto-deploys
   - Health check at `/api/health`

### Method 2: Docker Deployment

If you prefer Docker, rename `railway-simple.toml` to `railway.toml`:

```bash
mv railway-simple.toml railway.toml
```

Then follow the same steps above.

---

## Environment Variables Setup

### Required Variables:
- `EMERGENT_LLM_KEY` - Your Emergent Universal API Key
- `MONGO_URL` - MongoDB connection string

### Optional Variables:
- `NODE_ENV=production`
- `PYTHONPATH=/app`

---

## MongoDB Connection Examples

### MongoDB Atlas:
```
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/chatbot_db?retryWrites=true&w=majority
```

### Railway MongoDB Plugin:
```
MONGO_URL=mongodb://mongo:password@monorail.proxy.rlwy.net:port/railway
```

### Local Development:
```
MONGO_URL=mongodb://localhost:27017/chatbot_db
```

---

## Deployment Steps (Step by Step)

1. **Prepare Repository:**
   ```bash
   git add .
   git commit -m "Ready for Railway deployment"
   git push origin main
   ```

2. **Railway Setup:**
   - Login to Railway
   - New Project → Import from GitHub
   - Select your repository
   - Choose main branch

3. **Environment Configuration:**
   - Go to project dashboard
   - Click "Variables"
   - Add required environment variables

4. **Deploy:**
   - Railway will automatically build and deploy
   - Check deployment logs for any issues
   - Visit your app URL when ready

---

## Health Check

Your app will be ready when `/api/health` returns:
```json
{
  "status": "healthy",
  "database": "connected",
  "emergent_key": "configured"
}
```

---

## Troubleshooting

### Build Fails:
- **"Cannot find module 'autoprefixer'"**: Fixed by installing all dependencies (including devDependencies)
- Check environment variables are set
- Verify MongoDB connection string
- Ensure Emergent API key is valid

### App Not Loading:
- Check Railway logs
- Verify health check endpoint
- Ensure PORT environment variable is used

### Database Connection Issues:
- Verify MongoDB URL format
- Check network access (Atlas whitelist)
- Ensure database exists

---

## Features Available After Deployment

✅ **LLM Integration:**
- OpenAI GPT models (GPT-4, GPT-4o, GPT-5)
- Anthropic Claude models (Claude-3.5, Claude-4)
- Google Gemini models (Gemini-1.5, Gemini-2.5)

✅ **Chat Features:**
- Markdown rendering with syntax highlighting
- Conversation history with session management
- Responsive design (mobile, tablet, desktop)
- Model switching in real-time

✅ **Backend API:**
- `/api/health` - Health check
- `/api/models` - Available models
- `/api/chat` - Chat completion
- `/api/sessions` - Chat history

---

## Performance Notes

- **Cold Start:** First request may take 10-15 seconds
- **Warm Requests:** Sub-second response times
- **Auto-scaling:** Railway handles traffic spikes
- **Health Monitoring:** Automatic restarts if needed

---

## Support

If you encounter issues:
1. Check Railway deployment logs
2. Verify environment variables
3. Test health endpoint
4. Check MongoDB connection

Your app is now ready for Railway deployment! 🚀
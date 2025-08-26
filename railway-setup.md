# 🚀 Setup Railway Deployment - Langkah Mudah

## 1. Push Code ke GitHub
```bash
git add .
git commit -m "Railway deployment ready"
git push origin main
```

## 2. Setup Railway Project
1. Login ke [Railway](https://railway.app)
2. Klik **"New Project"** 
3. Pilih **"Deploy from GitHub"**
4. Pilih repository Anda
5. Railway akan otomatis detect konfigurasi

## 3. Setup Database MongoDB

### Option A: MongoDB Atlas (Recommended)
1. Buat account [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create cluster gratis
3. Get connection string
4. Di Railway Variables, set:
   ```
   MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/chatbot_db
   ```

### Option B: Railway MongoDB Add-on  
1. Di Railway project, klik **"Add Service"**
2. Pilih **"MongoDB"** 
3. Railway auto-generate `MONGODB_URL`
4. Set variable:
   ```
   MONGO_URL=${{MONGODB_URL}}
   ```

## 4. Environment Variables (Required)
Di Railway dashboard > Variables:

```bash
# MongoDB Connection (choose one option above)
MONGO_URL=mongodb+srv://your-connection-string

# Optional
DB_NAME=chatbot_db
CORS_ORIGINS=*
```

## 5. Deployment
Railway akan otomatis:
- ✅ Detect `railway.toml` 
- ✅ Use `Dockerfile` untuk build
- ✅ Set PORT environment variable
- ✅ Generate public URL

## 6. Verify Deployment
Test endpoints:
- **Health**: `https://your-app.railway.app/api/health`
- **Models**: `https://your-app.railway.app/api/models` 
- **App**: `https://your-app.railway.app`

## ⚡ Features Ready
✅ Multi-LLM Integration (OpenAI, Anthropic, Gemini)
✅ User input API keys (no hardcoded keys)
✅ Chat history dengan MongoDB
✅ Responsive design 
✅ Markdown rendering
✅ Railway optimized

## 🔧 Troubleshooting
- **Build fail**: Check Railway build logs
- **DB connection**: Verify MONGO_URL format
- **Cold starts**: Railway apps sleep after inactivity

## 🎯 Done!
Aplikasi siap production di Railway dengan zero configuration!
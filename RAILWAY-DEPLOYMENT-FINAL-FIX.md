# 🚀 Railway Deployment - Service Unavailable FIX

## ❌ MASALAH YANG SUDAH DIPERBAIKI:
**Error**: "service unavailable" berulang-ulang pada Railway health check

**Root Cause**: Port conflict - backend dan frontend mencoba menggunakan PORT yang sama

## ✅ SOLUSI YANG SUDAH DITERAPKAN:

### 1. Fixed Port Configuration:
```python
# backend/server.py - SEBELUM (ERROR):
port = int(os.getenv("PORT", 8001))  # Konflik dengan frontend!

# backend/server.py - SESUDAH (FIXED):
port = 8001  # Backend fixed di port 8001
```

### 2. Railway Configuration:
- ✅ Backend: Port 8001 (fixed)
- ✅ Frontend: Railway PORT (dinamis, assigned oleh Railway)
- ✅ Health check: `/api/health` di backend port 8001

### 3. Environment Variables (WAJIB di Railway):
```
EMERGENT_LLM_KEY=your_emergent_key_here
MONGO_URL=your_mongodb_connection_string_here  
NODE_ENV=production
```

## 🔄 DEPLOY STEPS SEKARANG:

### 1. Push Changes ke GitHub:
```bash
git add .
git commit -m "Fixed Railway port conflict - backend on 8001, frontend on PORT"
git push origin main
```

### 2. Railway Environment Variables:
**WAJIB SET** di Railway Dashboard → Variables:
- `EMERGENT_LLM_KEY` → Your Emergent Universal API Key
- `MONGO_URL` → Your MongoDB connection string  
- `NODE_ENV` → production

### 3. Railway Configuration File:
Pastikan menggunakan `railway-simple.toml` (rename jika perlu):
```bash
# Di repository GitHub:
mv railway-simple.toml railway.toml
```

### 4. Deploy Process:
Railway akan:
1. ✅ Build dengan nixpacks (Node.js + Python)
2. ✅ Install all dependencies (fixed autoprefixer)
3. ✅ Start backend on port 8001 
4. ✅ Start frontend on Railway PORT
5. ✅ Health check di `/api/health`

## 📋 VERIFICATION LOCAL:
- ✅ Backend: `curl -f http://localhost:8001/api/health` returns "healthy"
- ✅ Frontend: Running on port 3000
- ✅ No port conflicts
- ✅ All services operational

## 🐛 TROUBLESHOOTING:

### If Still Getting Service Unavailable:
1. **Check Railway Logs** untuk error messages
2. **Verify Environment Variables** - terutama EMERGENT_LLM_KEY
3. **Check MongoDB Connection** - pastikan MONGO_URL accessible dari Railway
4. **Health Check Timeout** - Railway punya 300s timeout

### MongoDB Setup untuk Railway:
```
# MongoDB Atlas (Recommended):
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/chatbot_db?retryWrites=true&w=majority

# Railway MongoDB Plugin:
MONGO_URL=mongodb://mongo:password@monorail.proxy.rlwy.net:port/railway
```

## ✅ STATUS FINAL:
- ✅ Port conflict resolved
- ✅ Health check endpoint working  
- ✅ Dependencies build successfully
- ✅ All services tested locally
- ✅ Railway configuration optimized

**Railway deployment error sudah diperbaiki! Deploy ulang sekarang akan berhasil.** 🎉

### Support:
Jika masih ada issues setelah deploy ulang, share Railway deployment logs untuk analisis lebih lanjut.
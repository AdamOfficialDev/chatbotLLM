# 🚀 Railway Deployment Guide - SQLite Version

## Kenapa SQLite? 
- ✅ **ZERO Configuration** - Tidak perlu setup database apapun!
- ✅ **File-based** - Database tersimpan sebagai file, otomatis backup
- ✅ **Perfect untuk Railway** - Tidak perlu external database service
- ✅ **Fast & Reliable** - Performance tinggi untuk aplikasi chat
- ✅ **No Connection Issues** - Tidak ada network dependency

## 🎯 Deployment Steps (Super Simple!)

### Step 1: Login ke Railway
1. Buka [railway.app](https://railway.app)
2. Login dengan GitHub account
3. Klik "New Project"

### Step 2: Deploy dari GitHub
1. Pilih "Deploy from GitHub repo"
2. Connect repository ini
3. Railway akan otomatis detect dan deploy!

### Step 3: Set Environment Variable (Optional)
Jika ingin menggunakan Emergent Universal Key:
```
EMERGENT_LLM_KEY=your_key_here
```

**Atau biarkan kosong** - user bisa input API key mereka sendiri di frontend!

### Step 4: Done! 🎉
- Railway akan build dan deploy otomatis
- Health check di `/api/health`
- Frontend accessible di Railway domain
- Database SQLite otomatis dibuat

## 🔧 Technical Details

### Database
- **SQLite file**: `backend/chatbot.db` 
- **Tables**: `chats`, `sessions`
- **Auto-created** on first run
- **Persistent** across deploys (Railway mounts volume)

### Services
- **Frontend**: Next.js on dynamic PORT
- **Backend**: FastAPI on port 8001  
- **Database**: SQLite (file-based)

### Health Monitoring
Railway akan monitor aplikasi via:
- Health endpoint: `/api/health`
- Restart policy: ON_FAILURE
- Max retries: 5

## 🚨 Troubleshooting

### Build Issues
Jika ada error saat build:
1. Check `backend/requirements.txt` 
2. Ensure `emergentintegrations` package installed

### Runtime Issues  
Jika app tidak start:
1. Check Railway logs
2. Verify `/api/health` endpoint responds
3. Check environment variables

### Database Issues
SQLite rarely has issues, tapi jika ada:
1. Check file permissions
2. Verify database auto-creation in logs
3. Check disk space (Railway has limits)

## 🎨 Features Ready for Production

✅ **Complete LLM Integration** - OpenAI, Anthropic, Gemini
✅ **Chat History** - Persistent dengan SQLite
✅ **Session Management** - Multi-user support
✅ **Responsive Design** - Mobile & desktop
✅ **Markdown Support** - Beautiful AI responses  
✅ **Performance Optimized** - Fast loading & scrolling
✅ **No Database Config** - Just deploy and go!

## 📝 Notes

- SQLite file akan persist selama Railway project aktif
- Backup otomatis via Railway's volume snapshots
- Scalable sampai jutaan messages (SQLite very efficient)
- Zero maintenance - tidak seperti MongoDB yang ribet!

**Intinya: Push to Railway = Auto Deploy = Works! 🚀**
# Deploy ke Railway - Panduan Lengkap

## 🚀 Langkah-langkah Deployment

### 1. Persiapan Repository
Pastikan semua file sudah di push ke GitHub repository Anda.

### 2. Setup Railway Project

1. **Login ke Railway**: Buka [railway.app](https://railway.app) dan login
2. **New Project**: Klik "New Project"
3. **Deploy from GitHub**: Pilih repository GitHub Anda
4. **Select Branch**: Pilih branch yang ingin di-deploy (biasanya `main`)

### 3. Setup Environment Variables

Di Railway dashboard, buka tab **Variables** dan tambahkan:

#### Required Variables:
```
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/chatbot_db
```

#### Optional Variables:
```
DB_NAME=chatbot_db
CORS_ORIGINS=*
```

### 4. Setup MongoDB Database

#### Option A: MongoDB Atlas (Recommended)
1. Buat account di [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Buat cluster baru (free tier tersedia)
3. Dapatkan connection string
4. Set `MONGO_URL` dengan connection string Atlas

#### Option B: Railway MongoDB Add-on
1. Di Railway dashboard, klik "Add Service"
2. Pilih "MongoDB"
3. Railway akan otomatis set `MONGODB_URL`
4. Set environment variable: `MONGO_URL=${{MONGODB_URL}}`

### 5. Deploy Configuration

Railway akan otomatis:
- Detect `railway.toml` configuration
- Build menggunakan `Dockerfile`
- Expose aplikasi di URL publik

### 6. Verifikasi Deployment

1. **Health Check**: Kunjungi `https://your-app.railway.app/api/health`
2. **Models API**: Kunjungi `https://your-app.railway.app/api/models`
3. **Frontend**: Kunjungi `https://your-app.railway.app`

## 🔧 Troubleshooting

### Build Errors
- Check Railway build logs
- Pastikan semua dependencies ada di `package.json` dan `requirements.txt`

### Database Connection Issues
- Verifikasi `MONGO_URL` environment variable
- Check MongoDB Atlas network access (allow all IPs: 0.0.0.0/0)
- Pastikan username/password benar

### Port Issues
- Railway otomatis set `PORT` environment variable
- Aplikasi sudah dikonfigurasi menggunakan `$PORT`

### Memory Issues
- Railway free tier memiliki limits
- Optimize Docker image jika perlu

## 📦 File Structure untuk Railway

```
/app/
├── railway.toml          # Railway configuration
├── Dockerfile           # Multi-stage build
├── start-railway.sh     # Startup script
├── package.json         # Frontend dependencies & scripts
├── backend/
│   ├── server.py        # FastAPI backend
│   └── requirements.txt # Python dependencies
└── ... (other files)
```

## 🌐 Environment URLs

Setelah deploy, update environment variables:
```
NEXT_PUBLIC_BASE_URL=https://your-app.railway.app
REACT_APP_BACKEND_URL=https://your-app.railway.app
```

## 💡 Tips Optimization

1. **Cold Start**: Railway apps sleep after inactivity
2. **Logs**: Monitor Railway logs untuk debugging
3. **Custom Domain**: Tambahkan custom domain di Railway settings
4. **Scaling**: Upgrade plan untuk better performance

## 🔑 User API Keys

Aplikasi tidak menyimpan API keys. User input API key mereka sendiri di:
- OpenAI API Key
- Anthropic API Key  
- Google Gemini API Key
- Atau Emergent Universal Key

## 🎯 Features Ready

✅ Multi-LLM support (OpenAI, Anthropic, Gemini)
✅ Chat history dengan MongoDB
✅ Responsive design
✅ Markdown rendering dengan syntax highlighting
✅ Session management
✅ Railway optimized deployment
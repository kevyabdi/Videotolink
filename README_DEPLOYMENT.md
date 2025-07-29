# Deployment Guide for Telegram File Saver Bot

## ✅ Bot Status
Your bot is now working perfectly with SESSION_REVOKED error fixed!

## 🚀 Render.com Deployment Steps

### 1. Upload to GitHub
1. Create a new repository on GitHub
2. Upload all project files including:
   - `main.py` (main bot file)
   - `session_manager.py` (session recovery system)
   - `keep_alive.py` (web server)
   - `cleanup_sessions.py` (session cleanup utility)
   - `pyproject.toml` (dependencies)
   - `render.yaml` (deployment config)
   - All JSON files (files.json, stats.json, etc.)

### 2. Deploy on Render.com
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` configuration

### 3. Set Environment Variables
In Render dashboard, add these environment variables:
- `API_ID`: Your Telegram API ID (26176218)
- `API_HASH`: Your Telegram API hash
- `BOT_TOKEN`: Your new bot token from @BotFather

### 4. Deploy Configuration
- **Build Command**: `pip install pyrogram flask tgcrypto`
- **Start Command**: `python main.py`
- **Port**: 5000 (automatically configured)

## 🔧 Features Included

### Session Management
- ✅ Automatic recovery from SESSION_REVOKED errors
- ✅ Session file cleanup on corruption
- ✅ Retry mechanism (up to 3 attempts)
- ✅ Comprehensive error handling

### Bot Features
- ✅ File upload and sharing (all types)
- ✅ Permanent download links
- ✅ User statistics tracking
- ✅ Admin controls and moderation
- ✅ Premium user system

### Web Interface
- ✅ Status monitoring on port 5000
- ✅ Health check endpoints
- ✅ Feature documentation

## 📱 Testing Your Bot

After deployment, test these commands:
1. `/start` - Welcome message with buttons
2. Send any file - Get shareable download link
3. Admin commands (if you're the admin)

## 🔍 Monitoring

Your bot includes:
- Real-time logging for debugging
- Web status page at `your-app-url.onrender.com/status`
- Automatic session recovery
- Error handling with user feedback

## ⚡ Performance Notes

- Uses Telegram's infrastructure for file storage
- Lightweight JSON-based data storage
- Automatic cleanup of corrupted sessions
- Multi-threaded web server

Your bot is production-ready and will work perfectly on Render.com!
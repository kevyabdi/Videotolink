# Deployment Guide

This guide covers various deployment options for the Telegram File Saver Bot.

## Prerequisites

Before deploying, ensure you have:

1. **Telegram Bot Token**
   - Create a bot via [@BotFather](https://t.me/BotFather)
   - Save the bot token securely

2. **Telegram API Credentials**
   - Get API_ID and API_HASH from [my.telegram.org](https://my.telegram.org)
   - Create a new application and note the credentials

3. **Admin User ID**
   - Get your Telegram user ID (use [@userinfobot](https://t.me/userinfobot))
   - Update `ADMIN_USER_ID` in `main.py`

## Environment Variables

All deployment methods require these environment variables:

```bash
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
BOT_TOKEN=your_bot_token_from_botfather
```

## Deployment Options

### 1. Render.com (Recommended)

#### Auto Deploy (Easy)
1. **Fork/Clone Repository**
   ```bash
   git clone <your-repo-url>
   cd telegram-file-saver-bot
   ```

2. **Connect to Render**
   - Sign up at [render.com](https://render.com)
   - Connect your GitHub/GitLab repository
   - Choose "Web Service" deployment

3. **Configure Environment**
   - Set environment variables in Render dashboard
   - Build command: `pip install -r requirements.txt` (auto-generated)
   - Start command: `python main.py`

4. **Deploy**
   - Render will automatically deploy and provide a URL
   - The bot will start immediately after deployment

#### Manual Render Setup
```yaml
# render.yaml (already included)
services:
  - type: web
    name: telegram-file-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    envVars:
      - key: API_ID
        value: your_api_id
      - key: API_HASH
        value: your_api_hash
      - key: BOT_TOKEN
        value: your_bot_token
```

### 2. Railway

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and Deploy**
   ```bash
   railway login
   railway new
   railway add
   ```

3. **Set Environment Variables**
   ```bash
   railway variables set API_ID=your_api_id
   railway variables set API_HASH=your_api_hash
   railway variables set BOT_TOKEN=your_bot_token
   ```

4. **Deploy**
   ```bash
   railway up
   ```

### 3. Heroku

1. **Install Heroku CLI**
   ```bash
   # MacOS
   brew install heroku/brew/heroku
   
   # Ubuntu/Debian
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Create App**
   ```bash
   heroku create your-bot-name
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set API_ID=your_api_id
   heroku config:set API_HASH=your_api_hash
   heroku config:set BOT_TOKEN=your_bot_token
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

### 4. VPS/Cloud Server

#### Requirements
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.11+
- Root or sudo access

#### Installation Steps

1. **Update System**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Python and Dependencies**
   ```bash
   sudo apt install python3.11 python3.11-pip python3.11-venv git -y
   ```

3. **Clone Repository**
   ```bash
   git clone <your-repo-url>
   cd telegram-file-saver-bot
   ```

4. **Create Virtual Environment**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```

5. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Set Environment Variables**
   ```bash
   export API_ID=your_api_id
   export API_HASH=your_api_hash
   export BOT_TOKEN=your_bot_token
   ```

7. **Create Systemd Service**
   ```bash
   sudo nano /etc/systemd/system/telegram-bot.service
   ```

   ```ini
   [Unit]
   Description=Telegram File Saver Bot
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/telegram-file-saver-bot
   Environment=API_ID=your_api_id
   Environment=API_HASH=your_api_hash
   Environment=BOT_TOKEN=your_bot_token
   ExecStart=/home/ubuntu/telegram-file-saver-bot/venv/bin/python main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

8. **Start Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable telegram-bot
   sudo systemctl start telegram-bot
   ```

### 5. Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app
   COPY . .

   RUN pip install --no-cache-dir -r requirements.txt

   EXPOSE 5000

   CMD ["python", "main.py"]
   ```

2. **Build and Run**
   ```bash
   docker build -t telegram-file-bot .
   docker run -d \
     -e API_ID=your_api_id \
     -e API_HASH=your_api_hash \
     -e BOT_TOKEN=your_bot_token \
     -p 5000:5000 \
     --name file-bot \
     telegram-file-bot
   ```

## Post-Deployment

### 1. Verify Deployment
- Check the web interface at your deployment URL
- Test bot commands in Telegram
- Monitor logs for any errors

### 2. Health Monitoring
The bot includes health check endpoints:
- `GET /` - Basic status
- `GET /status` - Detailed bot information
- `GET /features` - Feature documentation

### 3. Log Monitoring
Check application logs:
```bash
# Render/Railway/Heroku
# Use platform-specific log viewing

# VPS/Server
sudo journalctl -u telegram-bot -f

# Docker
docker logs -f file-bot
```

## Troubleshooting

### Common Issues

#### Bot Not Responding
1. Check environment variables are set correctly
2. Verify bot token is valid
3. Ensure API_ID and API_HASH are correct
4. Check application logs for errors

#### Session Errors
- The bot automatically handles session recovery
- If persistent issues occur, delete session files and restart

#### Port Issues
- Default port is 5000 for the web interface
- Ensure port is not blocked by firewall
- Some platforms assign ports automatically

#### Database Lock Errors
- Usually resolves automatically with session recovery
- If persistent, restart the application

### Getting Help

1. **Check Logs**: Always start by examining application logs
2. **Verify Credentials**: Ensure all API keys and tokens are correct
3. **Test Locally**: Try running the bot locally first
4. **Platform Support**: Check your deployment platform's documentation

## Security Considerations

1. **Environment Variables**: Never commit API keys to version control
2. **Admin Access**: Only set trusted user IDs as admins
3. **Server Security**: Keep your server/platform updated
4. **Monitoring**: Regularly check logs for suspicious activity

## Scaling

### For High Usage
1. **Database**: Consider migrating from JSON to PostgreSQL/MongoDB
2. **Caching**: Implement Redis for session management
3. **Load Balancing**: Use multiple instances behind a load balancer
4. **CDN**: Consider using external CDN for file delivery

### Performance Optimization
1. **Enable TgCrypto**: Already included for faster encryption
2. **Connection Pooling**: Pyrogram handles this automatically
3. **Memory Management**: Monitor memory usage in production
4. **Rate Limiting**: Implement if experiencing high load

## Backup and Recovery

### Data Backup
Regular backup of JSON files:
```bash
# Create backup directory
mkdir backups

# Backup data files
cp files.json stats.json banned_users.json premium_users.json backups/
```

### Session Recovery
The bot automatically handles session corruption, but you can manually clean sessions:
```bash
rm filetobot.session*
# Restart the bot - it will recreate sessions
```

## Updates and Maintenance

### Updating the Bot
1. **Pull Latest Changes**
   ```bash
   git pull origin main
   ```

2. **Update Dependencies**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **Restart Service**
   ```bash
   # Platform-specific restart commands
   # VPS: sudo systemctl restart telegram-bot
   # Docker: docker restart file-bot
   ```

### Regular Maintenance
- Monitor disk space (JSON files grow over time)
- Check for Python/dependency updates
- Review logs for errors or abuse
- Update API credentials if needed

This deployment guide covers most common scenarios. Choose the option that best fits your technical expertise and requirements.
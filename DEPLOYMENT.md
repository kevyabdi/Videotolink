# Deployment Guide

This guide explains how to deploy your Telegram File Saver Bot on various platforms.

## GitHub Repository Setup

### 1. Prepare Your Files
- Use `main-github.py` as your main file (rename to `main.py`)
- Use `requirements-github.txt` as your requirements file (rename to `requirements.txt`)
- Set your admin user ID in the code
- Never commit your actual credentials

### 2. Upload to GitHub
```bash
# Initialize git repository
git init

# Add files
git add .

# Commit
git commit -m "Initial commit - Telegram File Saver Bot"

# Add remote repository
git remote add origin https://github.com/yourusername/telegram-file-saver-bot.git

# Push to GitHub
git push -u origin main
```

## Platform Deployments

### Heroku Deployment

1. **Create Heroku App**
   ```bash
   heroku create your-bot-name
   ```

2. **Set Environment Variables**
   ```bash
   heroku config:set API_ID=your_api_id
   heroku config:set API_HASH=your_api_hash
   heroku config:set BOT_TOKEN=your_bot_token
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

4. **Scale Worker**
   ```bash
   heroku ps:scale worker=1
   ```

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard:
   - `API_ID`
   - `API_HASH`
   - `BOT_TOKEN`
3. Deploy automatically from GitHub

### Render Deployment

1. Create new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables:
   - `API_ID`
   - `API_HASH`
   - `BOT_TOKEN`
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python main.py`

### VPS/Server Deployment

1. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/telegram-file-saver-bot.git
   cd telegram-file-saver-bot
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variables**
   ```bash
   export API_ID="your_api_id"
   export API_HASH="your_api_hash"
   export BOT_TOKEN="your_bot_token"
   ```

4. **Run Bot**
   ```bash
   python main.py
   ```

5. **Run with PM2 (Recommended)**
   ```bash
   npm install -g pm2
   pm2 start ecosystem.config.js
   pm2 startup
   pm2 save
   ```

## Getting Credentials

### Telegram Bot Token
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Follow instructions to create your bot
4. Copy the bot token

### Telegram API Credentials
1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy API ID and API Hash

### Admin User ID
1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Copy your user ID number
3. Replace `ADMIN_USER_ID` in the code

## Environment Variables

All platforms require these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `API_ID` | Telegram API ID | `12345678` |
| `API_HASH` | Telegram API Hash | `abcdef1234567890abcdef1234567890` |
| `BOT_TOKEN` | Bot token from BotFather | `123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ` |

## Monitoring and Logs

### Heroku
```bash
heroku logs --tail
```

### Railway/Render
Check platform-specific log viewers in dashboard

### VPS
```bash
pm2 logs
```

## Troubleshooting

### Common Issues

1. **"No module named 'pyrogram'"**
   - Solution: Install dependencies with `pip install -r requirements.txt`

2. **"Invalid API_ID or API_HASH"**
   - Solution: Double-check credentials from my.telegram.org

3. **"Bot token invalid"**
   - Solution: Get new token from @BotFather

4. **"Permission denied"**
   - Solution: Check if admin user ID is correct

### Health Check

The bot includes a web server for health checks on port 5000. This helps with:
- Heroku keeping the bot alive
- Platform health monitoring
- Status verification

## Security Notes

- Never commit credentials to version control
- Use environment variables for all sensitive data
- Regularly rotate bot tokens and API keys
- Monitor bot logs for suspicious activity
- Keep dependencies updated

## Scaling

For high-traffic bots:
- Use webhook instead of polling (modify code)
- Consider using Redis for session storage
- Implement database connection pooling
- Use load balancers for multiple instances
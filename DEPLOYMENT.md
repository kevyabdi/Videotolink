# Deployment Guide

This guide covers how to deploy the Telegram File Saver Bot on various platforms.

## Prerequisites

Before deploying, make sure you have:

1. **Telegram Bot Token** - Get it from [@BotFather](https://t.me/botfather)
2. **Telegram API Credentials** - Get them from [my.telegram.org](https://my.telegram.org/)
   - API_ID
   - API_HASH
3. **Admin User ID** - Your Telegram user ID (get it from [@userinfobot](https://t.me/userinfobot))

## Environment Variables

Set these environment variables on your deployment platform:

```
API_ID=your_api_id_here
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here
```

## Deployment Options

### 1. Replit (Recommended for beginners)

1. **Fork this repository** to your GitHub account
2. **Import to Replit**:
   - Go to [Replit](https://replit.com)
   - Click "Create Repl"
   - Choose "Import from GitHub"
   - Enter your repository URL
3. **Set environment variables**:
   - Go to "Secrets" tab (lock icon)
   - Add your API_ID, API_HASH, and BOT_TOKEN
4. **Configure admin user**:
   - Edit `main.py`
   - Replace `ADMIN_USER_ID = 1096693642` with your Telegram user ID
5. **Run the bot**:
   - Click the "Run" button
   - The bot will start automatically

### 2. Heroku

1. **Create a Heroku app**:
   ```bash
   heroku create your-bot-name
   ```

2. **Set environment variables**:
   ```bash
   heroku config:set API_ID=your_api_id
   heroku config:set API_HASH=your_api_hash
   heroku config:set BOT_TOKEN=your_bot_token
   ```

3. **Deploy**:
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

4. **Keep the bot running**:
   - The `keep_alive.py` file helps keep the bot active on Heroku
   - Consider using Heroku Scheduler or similar services for better uptime

### 3. Railway

1. **Connect your GitHub repository** to Railway
2. **Add environment variables** in Railway dashboard:
   - API_ID
   - API_HASH  
   - BOT_TOKEN
3. **Deploy** - Railway will automatically deploy from your repository

### 4. VPS/Cloud Server

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/telegram-file-saver-bot.git
   cd telegram-file-saver-bot
   ```

2. **Install Python dependencies**:
   ```bash
   pip install pyrogram tgcrypto
   ```

3. **Set environment variables**:
   ```bash
   export API_ID="your_api_id"
   export API_HASH="your_api_hash"
   export BOT_TOKEN="your_bot_token"
   ```

4. **Configure admin user**:
   - Edit `main.py`
   - Set your `ADMIN_USER_ID`

5. **Run the bot**:
   ```bash
   python main.py
   ```

6. **Run in background** (optional):
   ```bash
   nohup python main.py &
   ```

### 5. Docker

1. **Create Dockerfile**:
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY . .
   
   RUN pip install pyrogram tgcrypto
   
   CMD ["python", "main.py"]
   ```

2. **Build and run**:
   ```bash
   docker build -t telegram-file-bot .
   docker run -e API_ID=your_api_id -e API_HASH=your_api_hash -e BOT_TOKEN=your_bot_token telegram-file-bot
   ```

## Post-Deployment

### Testing Your Bot

1. **Start a chat** with your bot on Telegram
2. **Send a file** to test file upload functionality
3. **Test admin commands**:
   - `/stats` - Check bot statistics
   - `/users` - View user list
   - `/broadcast Hello everyone!` - Test broadcast feature

### Monitoring

- Check logs regularly for errors
- Monitor user activity through `/stats` command
- Keep track of banned users with `/banned` command

### Maintenance

- **Database files** (`files.json`, `stats.json`, `banned_users.json`) are created automatically
- **Backup** these files regularly if running on VPS
- **Update** the bot code by pulling latest changes from repository

## Troubleshooting

### Common Issues

1. **"database is locked" error**:
   - Stop all running instances of the bot
   - Delete any `.session` files
   - Restart the bot

2. **Bot doesn't respond**:
   - Check environment variables are set correctly
   - Verify bot token is valid
   - Check logs for error messages

3. **Admin commands not working**:
   - Verify your user ID is correctly set in `ADMIN_USER_ID`
   - Get your user ID from [@userinfobot](https://t.me/userinfobot)

4. **Import errors**:
   - Make sure `pyrogram` and `tgcrypto` are installed
   - Use Python 3.8 or higher

### Getting Help

- Check the [README.md](README.md) for detailed documentation
- Review the code comments in `main.py`
- Create an issue on GitHub if you encounter problems

## Security Notes

- **Never commit** your API credentials to version control
- **Use environment variables** for all sensitive data
- **Keep your bot token secure** - treat it like a password
- **Regularly review** banned users and statistics
- **Monitor logs** for suspicious activity

## Performance Tips

- The bot uses JSON files for storage, suitable for small to medium usage
- For high-traffic bots, consider migrating to a proper database
- Rate limiting is built-in for broadcast messages
- Monitor memory usage on resource-constrained platforms
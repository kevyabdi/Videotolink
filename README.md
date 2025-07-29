# Telegram File Saver Bot

A robust Telegram bot built with Python and Pyrogram that provides secure file storage and sharing capabilities with advanced session recovery and admin features.

## Features

### Core Features
- **File Upload & Sharing**: Upload any file type and get permanent sharing links
- **Clean Interface**: Simple one-button interface for uploads and shares
- **No File Size Limits**: Uses Telegram's infrastructure (subject to Telegram limits)
- **Permanent Links**: Files never expire and remain accessible
- **Session Recovery**: Automatic handling of authentication errors and session corruption

### User Interface
- **Upload Flow**: Send file → Get "Copy Link" button
- **Share Flow**: Click shared link → View file with "Join DAAWO" button
- **Clean Captions**: Shared files display original captions only

### Admin Features
- **Statistics Dashboard**: View user counts, file uploads, and download metrics
- **User Management**: Ban/unban users with simple commands
- **Broadcasting**: Send messages to all bot users
- **Admin-Only Commands**: Restricted access for moderation tools

## Quick Start

### Prerequisites
- Python 3.11+
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Telegram API credentials (API_ID and API_HASH)

### Installation & Running
1. **Install Dependencies**:
   ```bash
   pip install pyrogram flask tgcrypto
   ```

2. **Set Environment Variables**:
   ```bash
   export API_ID=your_telegram_api_id
   export API_HASH=your_telegram_api_hash
   export BOT_TOKEN=your_bot_token
   ```

3. **Run the Bot**:
   ```bash
   python main.py
   ```

## Commands

### User Commands
- `/start` - Welcome message with channel join button
- `/help` - Detailed help with support and channel buttons

### Admin Commands (ID: 1096693642)
- `/stats` - View bot statistics and usage metrics
- `/ban <user_id>` - Ban a user from using the bot
- `/unban <user_id>` - Remove user ban
- `/broadcast <message>` - Send message to all users

## File Sharing Flow

1. **User uploads file** → Bot generates unique ID and stores metadata
2. **Bot responds** with sharing link and "Copy Link" button
3. **User shares link** → Recipients click link to access file
4. **File delivery** with original caption and "Join DAAWO" button

## Project Structure

```
├── main.py                 # Main bot logic and handlers
├── session_manager.py      # Session recovery system
├── keep_alive.py          # Web server for monitoring
├── files.json             # File metadata storage
├── stats.json             # User statistics
├── banned_users.json      # Banned users list
├── premium_users.json     # Premium users database
├── pyproject.toml         # Dependencies
├── README.md              # This file
└── DEPLOYMENT.md          # Deployment guide
```

## Configuration

### Admin Settings
Update `ADMIN_USER_ID` in main.py:
```python
ADMIN_USER_ID = 1096693642  # Replace with your Telegram user ID
```

### Channel Links
Update channel URLs in the code:
```python
# Join DAAWO button
url="https://t.me/daawotv"

# DM Owner button  
url="https://t.me/viizet"
```

## Monitoring

### Web Interface
- **Health Check**: `GET /` - Basic status
- **Detailed Status**: `GET /status` - Bot information
- **Features**: `GET /features` - Feature documentation

### Logging
Comprehensive logging for user interactions, session recovery, admin commands, and error tracking.

## Support

For issues or questions:
- **Bot Owner**: [@viizet](https://t.me/viizet)
- **Channel**: [@daawotv](https://t.me/daawotv)

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## License

This project is provided as-is for educational and personal use.
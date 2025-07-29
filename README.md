# Telegram File Saver Bot

A simple and reliable Telegram bot that allows users to upload files and receive permanent sharing links. Built with Python and Pyrogram, this bot provides secure file storage using Telegram's infrastructure.

## Features

- 📁 **File Upload**: Support for all file types (videos, documents, audio, photos)
- 🔗 **Permanent Links**: Generate shareable download links that never expire
- 🔒 **Secure Storage**: Files stored using Telegram's secure infrastructure
- 📺 **Community Integration**: Automatic JOIN DAAWO button on shared videos
- 💬 **Direct Support**: Easy access to bot owner via DM button
- 🚀 **Unlimited Usage**: No restrictions on file uploads or downloads

## How It Works

1. **Upload**: Send any file to the bot
2. **Get Link**: Receive a permanent sharing link instantly
3. **Share**: Anyone can download the file using the link
4. **Access**: Files remain accessible through Telegram's servers

## Bot Commands

- `/start` - Welcome message with quick access buttons
- Send any file - Get a shareable download link

## Technical Stack

- **Language**: Python 3.11
- **Bot Framework**: Pyrogram
- **Web Server**: Flask (for status monitoring)
- **Data Storage**: JSON files for lightweight persistence
- **File Hosting**: Telegram's CDN infrastructure

## Project Structure

```
├── main.py                 # Main bot application
├── keep_alive.py          # Flask web server for status
├── files.json            # File metadata storage
├── stats.json            # Usage statistics
├── banned_users.json     # User moderation
├── premium_users.json    # Premium user data (unused)
└── pyproject.toml        # Python dependencies
```

## Setup & Deployment

### Prerequisites

- Python 3.11+
- Telegram Bot Token (from @BotFather)
- Telegram API credentials (API_ID, API_HASH)

### Environment Variables

Set these required environment variables:

```bash
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here
```

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install pyrogram flask tgcrypto
   ```
3. Set environment variables
4. Run the bot:
   ```bash
   python main.py
   ```

### Replit Deployment

This bot is optimized for Replit deployment:

1. Import the project to Replit
2. Add secrets in the Secrets tab:
   - `BOT_TOKEN`
   - `API_ID` 
   - `API_HASH`
3. Click Run - the bot will start automatically

## Features Overview

### File Sharing
- Supports all Telegram file types
- Generates unique shareable links
- Files never expire or get deleted
- Fast downloads via Telegram's CDN

### User Interface
- Clean welcome message with helpful buttons
- Simple help system
- Direct contact with bot owner (@viizet)
- Community access via DAAWO channel

### Data Management
- Lightweight JSON-based storage
- Automatic user registration
- Download statistics tracking
- Banned user management

## Status Monitoring

The bot includes a Flask web server for status monitoring:

- **Port**: 5000
- **Status endpoint**: `/status` - JSON status information
- **Features page**: `/features` - Feature documentation

## Community

- **Support Channel**: [@daawotv](https://t.me/daawotv)
- **Contact Admin**: [@viizet](https://t.me/viizet)

## License

This project is open source and available under standard terms.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the bot.

---

**Made with ❤️ for the DAAWO community**
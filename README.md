# Telegram File Saver Bot

A powerful Telegram bot that allows users to upload files and receive permanent shareable download links. Built with Python and Pyrogram, featuring premium user system and comprehensive admin controls.

## Features

### Core Functionality
- **File Upload & Sharing**: Upload any file type (documents, videos, audio, photos) and get permanent download links
- **Original Caption Preservation**: Videos retain their original captions when downloaded
- **Unlimited Storage**: Uses Telegram's infrastructure for file hosting
- **Permanent Links**: Generated links work indefinitely

### Premium System
- **Free Users**: Limited to 10 file uploads
- **Premium Users**: Unlimited uploads
- **Interactive Upgrade**: Upgrade buttons with detailed plan information
- **Admin Management**: /premium and /unpremium commands

### Admin Features
- **User Statistics**: Comprehensive analytics including premium user counts
- **User Management**: View detailed user lists with activity data
- **Ban/Unban System**: Complete user access control
- **Broadcast System**: Send messages to all registered users
- **Real-time Monitoring**: Track bot performance and user activity

### Promotional Features
- **Channel Integration**: "Join Daawotv" buttons on all downloads
- **Upgrade Prompts**: Premium plan details and contact information
- **Channel Links**: Direct links to @daawotv

## Installation

### Prerequisites
- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Telegram API credentials (from [my.telegram.org](https://my.telegram.org/))

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/telegram-file-saver-bot.git
cd telegram-file-saver-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
Create a `.env` file or set environment variables:
```bash
export API_ID="your_api_id"
export API_HASH="your_api_hash"
export BOT_TOKEN="your_bot_token"
```

4. **Set admin user ID**
Edit `main.py` and replace the admin user ID:
```python
ADMIN_USER_ID = YOUR_TELEGRAM_USER_ID  # Replace with your actual Telegram user ID
```

5. **Run the bot**
```bash
python main.py
```

## Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `API_ID` | Telegram API ID from my.telegram.org | Yes |
| `API_HASH` | Telegram API Hash from my.telegram.org | Yes |
| `BOT_TOKEN` | Bot token from @BotFather | Yes |

### Admin Configuration
- Set your Telegram user ID in the `ADMIN_USER_ID` variable in `main.py`
- Only this user will have access to admin commands

## Usage

### For Users
1. **Upload Files**: Send any file to the bot
2. **Get Share Link**: Receive a permanent download link
3. **Share**: Anyone with the link can download the file
4. **Premium Upgrade**: Use upgrade buttons for unlimited uploads

### For Admins
- `/stats` - View bot statistics including premium user counts
- `/premium <user_id>` - Grant premium access to a user
- `/unpremium <user_id>` - Remove premium access from a user
- `/ban <user_id>` - Ban a user from using the bot
- `/unban <user_id>` - Remove ban from a user
- `/broadcast <message>` - Send message to all registered users

## Deployment

### Replit
1. Import the repository to Replit
2. Set environment variables in Replit Secrets
3. Run the bot using the built-in workflow

### VPS/Local Server
1. Clone the repository
2. Install dependencies
3. Set environment variables
4. Run with `python main.py`

## File Structure
```
telegram-file-saver-bot/
├── main.py              # Main bot application
├── keep_alive.py        # Web server for hosting platforms
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── files.json          # File mappings database (auto-generated)
├── stats.json          # User statistics (auto-generated)
├── banned_users.json   # Banned users list (auto-generated)
├── premium_users.json  # Premium users list (auto-generated)
└── .gitignore          # Git ignore file
```

## Technical Details

### Architecture
- **Framework**: Pyrogram (Telegram MTProto API)
- **Storage**: JSON files for data persistence
- **Web Server**: Flask for keep-alive functionality
- **Async**: Full async/await support for better performance

### Security Features
- Environment variable configuration
- Admin-only command access
- Comprehensive user ban system
- Input validation and error handling

## Premium Features

### Free Plan
- 10 file uploads maximum
- All file types supported
- Permanent download links
- Basic support

### Premium Plan
- Unlimited file uploads
- No file size restrictions
- Priority support
- Permanent file storage
- Early access to new features

### Upgrade Process
1. Use the "Upgrade to Premium" button in the bot
2. Contact admin through @daawotv
3. Provide your user ID for activation

## Support

For support and questions:
- Join our channel: [@daawotv](https://t.me/daawotv)
- Contact admin for premium access
- Create an issue on GitHub

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Pyrogram](https://github.com/pyrogram/pyrogram)
- Inspired by file sharing bots on Telegram
- Thanks to the Telegram Bot API community

---

**Note**: Make sure to keep your bot token and API credentials secure. Never commit them to version control.
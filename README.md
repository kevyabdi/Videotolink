# Telegram File Saver Bot

A powerful Telegram bot that allows users to upload files and receive permanent shareable download links. Built with Python and Pyrogram, featuring comprehensive admin controls and user management.

## Features

### Core Functionality

- **File Upload & Sharing**: Upload any file type (documents, videos, audio, photos) and get permanent download links
- **Original Caption Preservation**: Videos retain their original captions when downloaded
- **Unlimited Storage**: Uses Telegram's infrastructure for file hosting
- **Permanent Links**: Generated links work indefinitely

### Admin Features

- **User Statistics**: Comprehensive analytics on bot usage
- **User Management**: View detailed user lists with activity data
- **Ban/Unban System**: Complete user access control
- **Broadcast System**: Send messages to all registered users
- **Real-time Monitoring**: Track bot performance and user activity

### Security & Management

- **Admin-only Commands**: Secure access to management features
- **Ban Protection**: Comprehensive blocking of banned users
- **Activity Tracking**: Detailed logs of user interactions
- **Persistent Storage**: JSON-based data storage

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

### For Admins

- `/stats` - View bot statistics
- `/users` - View user list and activity
- `/ban <user_id>` - Ban a user from using the bot
- `/unban <user_id>` - Remove ban from a user
- `/banned` - View list of banned users
- `/broadcast <message>` - Send message to all registered users

## Deployment

### Replit

1. Import the repository to Replit
2. Set environment variables in Replit Secrets
3. Run the bot using the built-in workflow

### Heroku

1. Create a new Heroku app
2. Set environment variables in Heroku Config Vars
3. Deploy using Git or GitHub integration

### VPS/Local Server

1. Clone the repository
2. Install dependencies
3. Set environment variables
4. Run with `python main.py`

## File Structure

```
telegram-file-saver-bot/
├── main.py              # Main bot application
├── keep_alive.py        # Web server for hosting platforms (optional)
├── requirements.txt     # Python dependencies
├── files.json          # File mappings database (auto-generated)
├── stats.json          # User statistics (auto-generated)
├── banned_users.json   # Banned users list (auto-generated)
├── README.md           # This file
├── replit.md           # Project documentation
└── .gitignore          # Git ignore file
```

## Technical Details

### Architecture

- **Framework**: Pyrogram (Telegram MTProto API)
- **Storage**: JSON files for data persistence
- **Web Server**: Flask for keep-alive functionality (optional)
- **Async**: Full async/await support for better performance

### Database Schema

- **files.json**: Maps unique file IDs to Telegram file IDs
- **stats.json**: Stores user statistics and activity data
- **banned_users.json**: List of banned user IDs

### Security Features

- Environment variable configuration
- Admin-only command access
- Comprehensive user ban system
- Input validation and error handling

## Broadcast Feature

The bot includes a powerful broadcast system for administrators:

### Features
- Send messages to all registered users
- Real-time progress tracking
- Rate limiting (30 messages/second)
- Automatic skip of banned users
- Detailed delivery statistics
- Error handling for blocked users

### Usage
```
/broadcast Your message here
```

The bot will automatically:
1. Load all users from the database
2. Send the message to each user (except banned users)
3. Track delivery statistics
4. Provide real-time updates every 50 messages
5. Show final completion report

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- Create an issue on GitHub
- Check the documentation
- Review the code comments

## Acknowledgments

- Built with [Pyrogram](https://github.com/pyrogram/pyrogram)
- Inspired by file sharing bots on Telegram
- Thanks to the Telegram Bot API community

---

**Note**: Make sure to keep your bot token and API credentials secure. Never commit them to version control.

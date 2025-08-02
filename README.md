# YukkiChatBot - Telegram Anonymous Feedback Bot

A powerful Telegram bot for anonymous feedback collection, similar to Livegram Bot. Built with Python and Pyrogram framework without MongoDB dependency.

## Features

- 🔒 **Anonymous Feedback Collection** - Users can send anonymous messages to administrators
- 👨‍💼 **Admin Management** - Block/unblock users, view statistics, broadcast messages
- 📊 **Statistics Tracking** - Monitor bot usage, user activity, and message counts
- 🔄 **Dual Mode Operation** - Switch between private admin messages and group forwarding
- ⚡ **Rate Limiting** - Prevent spam with configurable rate limits
- 💾 **File-based Storage** - No database required, uses JSON for data persistence
- 📱 **Interactive Interface** - Inline keyboards and user-friendly commands

## Admin Commands

- `/start` - Start the bot and show welcome message
- `/help` - Display help information
- `/stats` - View bot statistics (admin only)
- `/block <user_id>` - Block a user from using the bot (admin only)
- `/unblock <user_id>` - Unblock a previously blocked user (admin only)
- `/mode` - Check current mode or switch between private/group mode (admin only)
- `/broadcast <message>` - Send a message to all bot users (admin only)

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd YukkiChatBot
```

2. Install dependencies:
```bash
pip install pyrogram tgcrypto
```

3. Set up environment variables:
```bash
export API_ID="your_api_id"
export API_HASH="your_api_hash"
export BOT_TOKEN="your_bot_token"
export ADMIN_IDS="admin_user_id_1,admin_user_id_2"
export OWNER_ID="owner_user_id"
```

4. Run the bot:
```bash
python main.py
```

## Configuration

### Required Environment Variables

- `API_ID` - Your Telegram API ID (get from https://my.telegram.org)
- `API_HASH` - Your Telegram API Hash (get from https://my.telegram.org)
- `BOT_TOKEN` - Your bot token from @BotFather
- `ADMIN_IDS` - Comma-separated list of admin user IDs
- `OWNER_ID` - Primary owner user ID

### Optional Environment Variables

- `BOT_MODE` - Bot operation mode (`private` or `group`, default: `private`)
- `TARGET_GROUP_ID` - Target group ID for group mode
- `MAX_MESSAGE_LENGTH` - Maximum message length (default: 4096)
- `RATE_LIMIT_MESSAGES` - Messages per rate limit window (default: 10)
- `RATE_LIMIT_WINDOW` - Rate limit window in seconds (default: 60)
- `DATA_FILE` - Data persistence file name (default: `bot_data.json`)
- `AUTO_SAVE_INTERVAL` - Auto-save interval in seconds (default: 300)

## File Structure

```
YukkiChatBot/
├── main.py           # Main bot application
├── config.py         # Configuration management
├── handlers.py       # Message and command handlers
├── storage.py        # In-memory storage with JSON persistence
├── utils.py          # Utility functions
├── dependencies.txt  # Python dependencies
└── README.md         # This file
```

## How It Works

1. **User Interaction**: Users send messages to the bot privately
2. **Anonymous Forwarding**: Messages are forwarded anonymously to admins/group
3. **Admin Management**: Admins can manage users, view stats, and broadcast messages
4. **Data Persistence**: All data is stored in memory and saved to JSON files
5. **Rate Limiting**: Prevents spam with configurable limits

## Getting Your Telegram API Credentials

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Copy your `API_ID` and `API_HASH`
6. Create a bot with @BotFather on Telegram
7. Copy the bot token

## Deployment

This bot is designed to run as a single process and can be deployed on:
- VPS/Dedicated servers
- Cloud platforms (Heroku, Railway, etc.)
- Replit
- Local machines

## License

MIT License - feel free to use and modify for your needs.

## Support

For issues and questions, please check the code comments or create an issue in the repository.

## Credits

Inspired by YukkiChatBot and designed to work similarly to Livegram Bot, but with file-based storage instead of MongoDB.
# Telegram File Saver Bot - Premium Edition

A powerful Telegram bot with premium features that allows users to upload files and receive permanent shareable download links. Built with Python and Pyrogram, featuring comprehensive admin controls, premium user management, and usage limits.

## 🌟 Premium Features

### Premium System
- **💎 Premium Users**: Unlimited uploads, no daily limits, no waiting periods
- **🆓 Free Users**: 5 uploads per day with 4-hour cooldown after limit
- **📺 JOIN DAAWO Button**: Automatically added to all video messages linking to https://t.me/daawotv
- **📞 Admin Contact**: @viizet for premium upgrades and support

### Enhanced Commands
- `/premium <user_id>` - Upgrade user to premium (admin only)
- `/unpremium <user_id>` - Remove premium status (admin only)
- `/upgrade` - Get premium upgrade information
- `/myplan` - Check current plan status and usage

## Features

### Core Functionality

- **File Upload & Sharing**: Upload any file type (documents, videos, audio, photos) and get permanent download links
- **Original Caption Preservation**: Videos retain their original captions when downloaded
- **Unlimited Storage**: Uses Telegram's infrastructure for file hosting
- **Permanent Links**: Generated links work indefinitely
- **Smart Usage Limits**: Free users get 5 uploads/day, premium users get unlimited

### Premium Features

- **Usage Tracking**: Daily upload limits with automatic reset
- **Cooldown System**: 4-hour waiting period for free users after limit
- **Premium Management**: Complete admin control over premium users
- **JOIN DAAWO Integration**: Automatic button on video messages
- **Plan Status**: Users can check their current plan and usage

### Admin Features

- **User Statistics**: Comprehensive analytics including premium user counts
- **Premium Management**: Upgrade/downgrade users with simple commands
- **User Management**: View detailed user lists with premium status
- **Ban/Unban System**: Complete user access control with premium preservation
- **Broadcast System**: Send messages to all registered users
- **Real-time Monitoring**: Track bot performance and premium user activity

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
pip install pyrogram tgcrypto flask
```

3. **Configure environment variables**

Set environment variables:

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
3. **Check Plan**: Use `/myplan` to see your current status
4. **Upgrade**: Use `/upgrade` to get premium information

### For Admins

- `/stats` - View bot statistics with premium analytics
- `/users` - View user list and activity with premium status
- `/premium <user_id>` - Upgrade user to premium
- `/unpremium <user_id>` - Remove premium status
- `/ban <user_id>` - Ban a user from using the bot
- `/unban <user_id>` - Remove ban from a user
- `/banned` - View list of banned users
- `/broadcast <message>` - Send message to all registered users

## File Structure

```
telegram-file-saver-bot/
├── main.py              # Main bot application with premium features
├── keep_alive.py        # Web server for hosting platforms
├── files.json          # File mappings database (auto-generated)
├── stats.json          # User statistics with premium tracking (auto-generated)
├── banned_users.json   # Banned users list (auto-generated)
├── premium_users.json  # Premium users database (auto-generated)
├── replit.md           # Project documentation
└── pyproject.toml      # Python dependencies
```

## Premium System Details

### Free Users
- 5 file uploads per day
- 4-hour cooldown after hitting daily limit
- All basic features included
- Permanent download links

### Premium Users
- Unlimited file uploads
- No daily limits or cooldowns
- Priority support
- All features included

### Admin Management
- Instant premium upgrades/downgrades
- Real-time usage monitoring
- Premium user analytics
- Complete user management

## Contact & Support

- **Admin Contact**: @viizet
- **JOIN DAAWO**: https://t.me/daawotv
- Create issues for bugs or feature requests

## License

This project is licensed under the MIT License.

---

**Note**: Keep your bot token and API credentials secure. Never commit them to version control.
# Telegram File Saver Bot

A powerful Telegram bot that allows users to upload files and receive permanent shareable download links. Built with Python and Pyrogram, featuring comprehensive admin controls, user management, and advanced duplicate message prevention.

## ✨ New Features

### 🚫 Duplicate Message Prevention
- **Session Management**: Tracks user sessions to prevent spam
- **Command Cooldowns**: 2-second cooldown for commands, 1-second for file uploads
- **Smart Welcome Messages**: Only sends welcome message once per hour per user
- **Anti-Spam Protection**: Prevents multiple responses to the same command

### 🔧 Enhanced Admin Controls
- Complete admin command set with proper error handling
- Real-time user statistics and management
- Advanced ban/unban system with user verification
- Comprehensive user activity tracking

## 🎯 Core Features

### File Management
- **File Upload & Sharing**: Upload any file type and get permanent download links
- **Original Caption Preservation**: Videos retain their original captions
- **Unlimited Storage**: Uses Telegram's infrastructure for file hosting
- **Permanent Links**: Generated links work indefinitely

### Admin Features
- **User Statistics**: Comprehensive analytics on bot usage
- **User Management**: Detailed user lists with activity data
- **Ban/Unban System**: Complete user access control
- **Session Tracking**: Monitor user interactions and prevent abuse

### Security & Management
- **Admin-only Commands**: Secure access to management features
- **Ban Protection**: Comprehensive blocking of banned users
- **Activity Tracking**: Detailed logs of user interactions
- **Persistent Storage**: JSON-based data storage

## 📋 Commands

### User Commands
- `/start` - Welcome message and bot info
- `/help` - Show help and available commands
- Send any file - Get shareable download link

### Admin Commands
- `/stats` - View comprehensive bot statistics
- `/users` - List all users with activity data
- `/ban <user_id>` - Ban a user from using the bot
- `/unban <user_id>` - Remove ban from a user
- `/banned` - View list of banned users

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Telegram API credentials (from [my.telegram.org](https://my.telegram.org))

### Environment Variables
```bash
export API_ID="your_api_id"
export API_HASH="your_api_hash"
export BOT_TOKEN="your_bot_token"
export ADMIN_USER_ID="your_telegram_user_id"

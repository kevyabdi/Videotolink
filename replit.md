# Telegram File Saver Bot

## Overview

This is a Telegram bot application that allows users to upload files and receive permanent shareable download links. The bot is built using Python with the Pyrogram library for Telegram API interactions, and includes comprehensive admin controls, user management, anti-spam features, and a web dashboard for monitoring.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a simple event-driven architecture with the following key components:

### Backend Architecture
- **Framework**: Python with Pyrogram for Telegram Bot API
- **Web Server**: Flask for health check and status monitoring
- **Data Storage**: JSON file-based storage system
- **Session Management**: In-memory user session tracking
- **Anti-Spam System**: Cooldown-based duplicate prevention

### Data Storage Strategy
The application uses a lightweight JSON-based storage approach instead of a traditional database:
- `files.json`: Stores file mappings and metadata
- `stats.json`: Tracks user statistics and bot analytics
- `banned_users.json`: Manages banned user list
- `user_sessions.json`: Handles session data

This approach was chosen for simplicity and ease of deployment, avoiding the need for database setup and management.

## Key Components

### 1. Bot Core (`main.py`)
- Main application entry point
- Handles all Telegram bot interactions
- Implements command routing and message processing
- Manages user sessions and cooldown systems

### 2. Web Dashboard (`keep_alive.py`)
- Flask-based web interface for monitoring bot status
- Provides health check endpoint
- Displays bot statistics and status information
- Serves as a keep-alive mechanism for hosting platforms

### 3. Data Management System
- JSON-based file storage for persistence
- User statistics tracking and analytics
- Ban/unban system for user access control
- File metadata and download link management

### 4. Anti-Spam Protection
- Command cooldown system (2 seconds for commands, 1 second for file uploads)
- Session-based duplicate message prevention
- Smart welcome message limiting (once per hour per user)
- User activity tracking and rate limiting

## Data Flow

### File Upload Process
1. User sends file to bot
2. Bot validates user permissions (not banned)
3. System checks upload cooldown to prevent spam
4. File is processed and stored in Telegram's servers
5. Unique download link is generated and stored in `files.json`
6. Statistics are updated in `stats.json`
7. Download link is sent back to user

### Admin Management Flow
1. Admin sends management command
2. Bot verifies admin privileges using `ADMIN_USER_ID`
3. Command is processed with appropriate data operations
4. Results are formatted and sent back to admin
5. Changes are persisted to respective JSON files

### User Session Management
1. User interactions are tracked in memory
2. Cooldown timers prevent rapid successive commands
3. Welcome messages are limited using session data
4. Ban status is checked on every interaction

## External Dependencies

### Core Dependencies
- **Pyrogram (2.0.106)**: Telegram Bot API client library
- **TgCrypto (1.2.5)**: Cryptographic functions for Pyrogram
- **Flask (3.1.1)**: Web framework for status dashboard

### Environment Variables
- `API_ID`: Telegram API ID from my.telegram.org
- `API_HASH`: Telegram API hash from my.telegram.org
- `BOT_TOKEN`: Bot token from @BotFather
- `ADMIN_USER_ID`: Telegram user ID of the bot administrator

### External Services
- **Telegram Bot API**: Core bot functionality and file hosting
- **Telegram MTProto API**: Advanced API features through Pyrogram
- **File Storage**: Uses Telegram's infrastructure for permanent file hosting

## Deployment Strategy

### Supported Platforms
The bot is designed for deployment on various cloud platforms:

1. **Heroku**: Primary deployment target with environment variable configuration
2. **Railway**: Alternative cloud platform deployment
3. **Replit**: Development and testing environment
4. **VPS/Dedicated Servers**: Self-hosted deployment options

### Deployment Configuration
- Environment-based configuration for security
- JSON file persistence for data storage
- Web dashboard for monitoring and health checks
- Git-based deployment workflow

### Key Deployment Features
- **Zero-Database Setup**: Uses JSON files, no database configuration required
- **Environment Security**: All sensitive data stored in environment variables
- **Health Monitoring**: Built-in web dashboard for status checking
- **Scalable Architecture**: Can handle multiple concurrent users with session management

### Production Considerations
- File storage relies on Telegram's infrastructure for permanence
- JSON files provide sufficient performance for moderate user loads
- Admin controls ensure proper user management and spam prevention
- Session tracking prevents abuse while maintaining performance
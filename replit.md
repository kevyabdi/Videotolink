# Telegram File Saver Bot

## Overview

This is a Telegram bot built with Pyrogram that provides file storage and sharing capabilities. Users can upload files and receive permanent download links, while administrators have access to comprehensive management features including user statistics, ban/unban functionality, and broadcast messaging.

## User Preferences

Preferred communication style: Simple, everyday language.
Features requested: Premium user system with unlimited uploads, free user upload limits (10 files), admin controls for premium management, JOIN DAAWO button for videos.

## System Architecture

The application follows a simple monolithic architecture with file-based data persistence:

- **Bot Framework**: Pyrogram (Python Telegram bot library) for Telegram API interactions
- **Web Server**: Flask for keep-alive functionality and status monitoring
- **Data Storage**: JSON files for lightweight, file-based persistence
- **Authentication**: Telegram-based user identification with admin privilege system
- **File Management**: Telegram's infrastructure for file hosting with local metadata tracking

## Key Components

### 1. Bot Client (`main.py`)
- **Technology**: Pyrogram Client
- **Purpose**: Core bot functionality, message handling, file processing
- **Configuration**: Environment variables for API credentials (API_ID, API_HASH, BOT_TOKEN)
- **Admin System**: Single hardcoded admin user ID with elevated privileges

### 2. Keep-Alive Server (`keep_alive.py`)
- **Technology**: Flask web server
- **Purpose**: Maintains bot uptime on hosting platforms like Replit
- **Endpoints**: 
  - `/` - Basic status page
  - `/status` - JSON status response
- **Threading**: Runs in daemon thread alongside main bot

### 3. Data Storage (JSON Files)
- **files.json**: Stores file metadata, download links, and sharing information
- **stats.json**: Tracks comprehensive user statistics and usage analytics
- **banned_users.json**: Maintains list of banned users for moderation

### 4. User Management System
- **Admin Controls**: Statistics viewing, user management, ban/unban, broadcasting
- **User Tracking**: Activity monitoring, upload counting, download tracking
- **Premium System**: Placeholder for premium user functionality
- **Upload Limits**: Free users have configurable upload limits

### 5. File Handling System
- **Multi-format Support**: Documents, videos, audio files, photos
- **UUID Generation**: Unique identifiers for each uploaded file
- **Metadata Preservation**: Original captions and file information retained
- **Download Tracking**: Usage analytics and access monitoring

## Data Flow

### File Upload Process
1. User sends file to bot via Telegram
2. Bot validates user (checks ban status)
3. Generates unique UUID for file identification
4. Stores file metadata in files.json
5. Updates user statistics in stats.json
6. Returns shareable download link to user

### File Download Process
1. User shares download link
2. Recipients click link to access file
3. Bot retrieves file using stored metadata
4. Increments download counter in statistics
5. Serves file through Telegram's infrastructure

### Admin Operations
1. Admin sends management command
2. Bot verifies admin privileges
3. Executes requested operation (stats, ban, broadcast, etc.)
4. Updates relevant JSON databases
5. Returns confirmation or results to admin

## External Dependencies

### Core Dependencies
- **Pyrogram**: Telegram MTProto API client library
- **TgCrypto**: Cryptographic acceleration for Pyrogram
- **Flask**: Lightweight web framework for keep-alive server

### Telegram Services
- **Bot API**: For bot authentication and basic operations
- **MTProto API**: For advanced file operations and user management
- **File Storage**: Telegram's infrastructure for permanent file hosting

### Environment Configuration
- **API_ID & API_HASH**: Telegram application credentials
- **BOT_TOKEN**: Bot authentication token from BotFather
- **Admin Configuration**: Hardcoded admin user ID in main.py

## Deployment Strategy

### Platform Support
- **Replit**: Primary deployment target with keep-alive server
- **Heroku**: Alternative cloud deployment option
- **Local/VPS**: Direct Python execution capability

### Key Deployment Considerations
- **Environment Variables**: Secure credential management
- **File Persistence**: JSON files must persist across restarts
- **Keep-Alive**: Flask server prevents platform sleep on free hosting
- **Port Configuration**: Uses port 8080 for web server
- **Admin Setup**: Requires manual admin user ID configuration

### Scalability Limitations
- **File Storage**: Limited by JSON file performance
- **Concurrent Users**: Single-threaded bot processing
- **Data Growth**: Linear performance degradation with file count
- **Memory Usage**: All metadata loaded into memory

Note: The current architecture uses JSON files for simplicity. For production scale, consider migrating to a proper database system like PostgreSQL with Drizzle ORM for better performance and reliability.

## Recent Changes

### July 28, 2025 - Premium User System Implementation
- ✓ Added premium user system with unlimited uploads
- ✓ Implemented free user upload limit (10 files maximum)
- ✓ Created /premium command for admins to upgrade users
- ✓ Created /unpremium command for admins to downgrade users
- ✓ Added premium user statistics tracking
- ✓ Enhanced user interface to show Premium/Free status
- ✓ Added upload count display for free users
- ✓ Implemented JOIN DAAWO button for video downloads
- ✓ Updated port configuration to 5000 for Replit compatibility
- ✓ Integrated keep-alive server with main bot application

### Key Features Added:
- **Premium System**: Only main admin can grant/revoke premium status
- **Upload Limits**: Free users limited to 10 uploads, premium users unlimited
- **Status Display**: Clear indication of user status (💎 Premium or 🆓 Free)  
- **Video Enhancement**: JOIN DAAWO button (t.me/daawotv) appears on video downloads
- **Admin Controls**: Premium management accessible only to main admin
- **Statistics**: Enhanced stats tracking for premium vs free users
# Telegram File Saver Bot - Premium Edition

## Overview

This is a Telegram bot built with Python and Pyrogram that provides file storage and sharing capabilities with a comprehensive premium user system. The bot allows users to upload files and receive permanent shareable download links, with enhanced features for premium users including unlimited uploads and no waiting periods.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a monolithic architecture with file-based data persistence:

- **Bot Framework**: Pyrogram (Python Telegram bot library)
- **Data Storage**: JSON files for lightweight persistence
- **Web Interface**: Flask web server for status monitoring
- **Authentication**: Telegram-based user identification with premium status
- **File Management**: Telegram's infrastructure for file hosting
- **Premium System**: JSON-based premium user management with usage tracking

## Key Components

### 1. Bot Client (`main.py`)
- **Technology**: Pyrogram Client
- **Purpose**: Handles all Telegram API interactions including message processing, file uploads, and premium features
- **Configuration**: Environment-based credentials (API_ID, API_HASH, BOT_TOKEN)
- **Features**: Supports all file types, inline keyboards, callback queries, and admin commands

### 2. Data Storage Layer
- **files.json**: Stores file metadata and unique sharing identifiers
- **stats.json**: Comprehensive statistics including user data, file counts, download tracking, and premium metrics
- **banned_users.json**: List of banned users for moderation
- **premium_users.json**: Premium user database with timestamps and status

### 3. Premium Management System
- **Admin Controls**: Single admin user (ID: 1096693642) with full premium management privileges
- **Usage Limits**: Free users limited to 5 uploads per day, premium users get unlimited access
- **Cooldown System**: 4-hour waiting period for free users after reaching daily limit
- **Plan Tracking**: Real-time monitoring of user plan status and daily usage

### 4. Web Status Interface (`keep_alive.py`)
- **Technology**: Flask web server
- **Purpose**: Provides HTTP endpoints for bot status monitoring and feature documentation
- **Endpoints**: 
  - `/` - Basic status page
  - `/status` - JSON status with premium system info
  - `/features` - Detailed feature breakdown for premium vs free users

### 5. User Management
- **Registration**: Automatic user registration on first interaction
- **Statistics Tracking**: Comprehensive user analytics with premium status
- **Ban System**: Admin can ban/unban users while preserving premium status
- **Broadcast System**: Admin can send messages to all registered users

## Data Flow

### File Upload Process
1. User sends file to bot
2. System checks user's premium status and daily usage limits
3. If within limits, file is processed and unique ID generated
4. File metadata stored in files.json with permanent Telegram file_id
5. User receives shareable download link
6. Usage statistics updated

### Premium Management Flow
1. Admin uses `/premium <user_id>` command
2. User ID added to premium_users.json with timestamp
3. User gains unlimited upload access and no cooldown periods
4. Premium status reflected in all user interactions

### Download Process
1. User accesses shared link with unique file ID
2. Bot retrieves file metadata from files.json
3. File served directly from Telegram's servers
4. Download count incremented in statistics

## External Dependencies

### Required Packages
- **Pyrogram**: Telegram bot framework for Python
- **Flask**: Lightweight web framework for status interface
- **Threading**: For running Flask server alongside bot

### Telegram Integration
- **Telegram Bot API**: Core bot functionality
- **File Storage**: Uses Telegram's infrastructure for permanent file hosting
- **Inline Keyboards**: For JOIN DAAWO buttons on video messages

### Environment Variables
- `API_ID`: Telegram API ID for bot authentication
- `API_HASH`: Telegram API hash for bot authentication
- `BOT_TOKEN`: Bot token from @BotFather

## Deployment Strategy

### File-Based Persistence
- **Rationale**: Simple JSON files chosen for lightweight deployment without database dependencies
- **Data Files**: All user data, file metadata, and premium status stored in JSON format
- **Backup Strategy**: JSON files can be easily backed up and restored

### Process Management
- **Multi-Threading**: Flask web server runs in separate thread from main bot
- **Error Handling**: Comprehensive logging and error recovery
- **Monitoring**: Web interface provides real-time status monitoring

### Premium Features Integration
- **JOIN DAAWO Button**: Automatically added to video messages linking to https://t.me/daawotv
- **Admin Contact**: @viizet contact integrated for premium upgrades
- **Usage Limits**: Daily reset system with persistent tracking across restarts

### Scalability Considerations
- **File Storage**: Leverages Telegram's CDN for file distribution
- **User Management**: JSON-based storage suitable for moderate user bases
- **Premium System**: Designed for easy migration to database if needed

The architecture prioritizes simplicity and reliability while providing comprehensive premium features. The file-based approach allows for easy deployment and maintenance while the premium system adds monetization capabilities through usage restrictions and upgrade paths.
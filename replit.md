# Telegram File Saver Bot

## Overview

This is a Telegram bot built with Python and Pyrogram that provides file storage and sharing capabilities with advanced session recovery and premium features. The bot allows users to upload files and receive permanent download links, while automatically handling session corruption issues that commonly affect Telegram bots.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a monolithic architecture with file-based data persistence and robust session recovery mechanisms:

- **Bot Framework**: Pyrogram (Python Telegram bot library) for comprehensive Telegram API integration
- **Session Management**: Custom SessionManager class with automatic recovery from authentication errors
- **Data Storage**: JSON files for lightweight persistence without database overhead
- **Web Interface**: Flask web server for status monitoring and health checks
- **Authentication**: Telegram-based user identification with admin privileges
- **File Management**: Leverages Telegram's CDN infrastructure for file hosting and sharing
- **Error Handling**: Comprehensive session error recovery with automatic cleanup and retry mechanisms

## Key Components

### 1. Session Management (`session_manager.py`)
- **Purpose**: Handles Pyrogram session lifecycle with automatic recovery from authentication errors
- **Key Features**: 
  - Automatic detection and cleanup of corrupted session files
  - Recovery from SESSION_REVOKED, AuthKeyUnregistered, and similar errors
  - Retry mechanism with up to 3 attempts
  - Clean session file removal and regeneration
- **Problem Solved**: Eliminates manual intervention when Telegram sessions become corrupted, a common issue in long-running bots

### 2. Bot Client (`main.py`)
- **Technology**: Pyrogram Client with SessionManager integration
- **Purpose**: Handles all Telegram API interactions including message processing and file uploads
- **Configuration**: Environment-based credentials with fallback defaults for development
- **Features**: File upload handling, inline keyboards, user interaction, admin controls

### 3. Data Storage Layer
- **files.json**: Stores file metadata with unique identifiers for permanent sharing links
- **stats.json**: User statistics including upload counts, download tracking, and activity timestamps
- **banned_users.json**: User moderation list for access control
- **premium_users.json**: Premium user database for feature access management

### 4. Web Status Interface (`keep_alive.py`)
- **Technology**: Flask web server with suppressed logging for clean output
- **Purpose**: Provides HTTP endpoints for bot health monitoring and deployment status
- **Endpoints**: 
  - `/` - Basic status confirmation
  - `/status` - Detailed bot status with feature information
  - `/features` - Comprehensive feature documentation

### 5. Utility Scripts
- **cleanup_sessions.py**: Standalone utility for manual session cleanup during troubleshooting
- **Session recovery automation**: Integrated cleanup and retry mechanisms

## Data Flow

1. **User Interaction**: Users send files to the bot via Telegram
2. **File Processing**: Bot receives files and generates unique identifiers
3. **Metadata Storage**: File information stored in JSON format with timestamps
4. **Link Generation**: Permanent download links created using Telegram's file_id system
5. **Statistics Tracking**: User activity and file upload statistics updated
6. **Response Generation**: Bot sends confirmation with download link and inline keyboard

## External Dependencies

### Core Dependencies
- **Pyrogram**: Telegram API client library for bot functionality
- **Flask**: Web framework for status monitoring endpoints
- **TgCrypto**: Optional encryption library for improved Pyrogram performance

### Telegram Integration
- **API Credentials**: Requires API_ID, API_HASH, and BOT_TOKEN from Telegram
- **File Storage**: Leverages Telegram's CDN for permanent file hosting
- **User Authentication**: Uses Telegram's built-in user identification system

### Environment Variables
- `API_ID`: Telegram API identifier
- `API_HASH`: Telegram API hash key
- `BOT_TOKEN`: Bot token from @BotFather

## Deployment Strategy

### Platform Support
- **Primary**: Render.com with automatic deployment via `render.yaml`
- **Alternative**: Any Python hosting platform supporting long-running processes

### Configuration Management
- Environment-based configuration with development fallbacks
- Automatic dependency installation via `pyproject.toml`
- Web server integration for platform health checks

### Session Persistence Strategy
- **Problem**: Telegram sessions can become corrupted, causing bot failures
- **Solution**: Automatic session cleanup and regeneration on authentication errors
- **Recovery**: Multi-attempt retry mechanism with exponential backoff
- **Monitoring**: Comprehensive logging for troubleshooting session issues

### Scalability Considerations
- File-based storage suitable for moderate usage (JSON persistence)
- Stateless design allows for easy horizontal scaling if needed
- Telegram CDN handles file storage and bandwidth requirements
- Ready for database migration if user base grows significantly

The architecture prioritizes reliability and ease of deployment while maintaining the flexibility to scale. The robust session management system addresses the most common failure point in Telegram bots, ensuring consistent uptime and user experience.
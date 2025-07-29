# Telegram File Saver Bot

## Overview

This is a Telegram bot built with Python and Pyrogram that provides file storage and sharing capabilities with session recovery and premium features. The bot allows users to upload files and receive permanent sharing links, using Telegram's infrastructure for file hosting. The system includes robust session management, user statistics tracking, and admin controls.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a monolithic architecture with file-based data persistence and session recovery:

- **Bot Framework**: Pyrogram (Python Telegram bot library)
- **Session Management**: Custom SessionManager class with automatic recovery from authentication errors
- **Data Storage**: JSON files for lightweight persistence
- **Web Interface**: Flask web server for status monitoring and health checks
- **Authentication**: Telegram-based user identification with admin privileges
- **File Management**: Telegram's CDN infrastructure for file hosting and sharing
- **Error Handling**: Comprehensive session error recovery with automatic cleanup

## Key Components

### 1. Session Management (`session_manager.py`)
- **Purpose**: Handles Pyrogram session lifecycle with automatic recovery from authentication errors
- **Key Features**: 
  - Automatic detection and cleanup of corrupted session files
  - Recovery from SESSION_REVOKED, AuthKeyUnregistered, and similar errors
  - Retry mechanism with up to 3 attempts
  - Clean session file removal and regeneration
- **Problem Solved**: Eliminates manual intervention when Telegram sessions become corrupted

### 2. Bot Client (`main.py`)
- **Technology**: Pyrogram Client with SessionManager integration
- **Purpose**: Handles all Telegram API interactions including message processing and file uploads
- **Configuration**: Environment-based credentials with fallback defaults
- **Features**: File upload handling, inline keyboards, user interaction, admin controls

### 3. Data Storage Layer
- **files.json**: Stores file metadata with unique identifiers for sharing
- **stats.json**: User statistics including upload counts, download tracking, and activity timestamps
- **banned_users.json**: User moderation list (currently empty array)
- **premium_users.json**: Premium user database (currently empty object)

### 4. Web Status Interface (`keep_alive.py`)
- **Technology**: Flask web server with suppressed logging
- **Purpose**: Provides HTTP endpoints for bot health monitoring
- **Endpoints**: 
  - `/` - Basic status confirmation
  - `/status` - Detailed JSON status with session recovery info
  - `/features` - Feature documentation including session management capabilities

### 5. Session Cleanup Utility (`cleanup_sessions.py`)
- **Purpose**: Standalone script for manual session cleanup
- **Features**: Removes all Pyrogram session files to force re-authentication
- **Use Case**: Emergency recovery tool when automatic session recovery fails

## Data Flow

### File Upload Process
1. User sends file to bot via Telegram
2. Bot receives file and generates unique identifier
3. File metadata stored in files.json with timestamp
4. User statistics updated in stats.json
5. Permanent sharing link generated using Telegram's file infrastructure
6. User receives shareable download link

### Session Recovery Process
1. Bot attempts to connect using existing session
2. If authentication error occurs, SessionManager detects the issue
3. Corrupted session files are automatically removed
4. New session is created and authentication is re-established
5. Bot continues operation without manual intervention

### User Interaction Flow
1. User sends /start command or file
2. Bot checks user ban status and updates statistics
3. Appropriate response sent with inline keyboard buttons
4. Join community and contact admin buttons provided for engagement

## External Dependencies

### Core Dependencies
- **Pyrogram**: Telegram MTProto API client for bot functionality
- **Flask**: Lightweight web framework for status monitoring
- **Python Standard Library**: json, os, logging, datetime, asyncio modules

### Telegram API Integration
- **API Credentials**: API_ID and API_HASH for Telegram application
- **Bot Token**: Official bot token from BotFather
- **File Storage**: Uses Telegram's CDN for permanent file hosting

### Environment Variables
- `API_ID`: Telegram API application ID (default: 26176218)
- `API_HASH`: Telegram API hash (default provided)
- `BOT_TOKEN`: Telegram bot token (default provided)

## Deployment Strategy

### Local Development
- Files stored locally in JSON format for simple development
- Session files managed automatically by SessionManager
- Flask server runs on default port for status monitoring

### Production Considerations
- Environment variables should be properly configured
- Session recovery ensures minimal downtime during authentication issues
- JSON file persistence suitable for small to medium scale usage
- Flask keep-alive server maintains bot availability status

### Error Recovery
- Automatic session cleanup on authentication errors
- Manual cleanup utility available for emergency situations
- Comprehensive logging for debugging session issues
- Retry mechanism prevents permanent failures from temporary issues

### Scaling Limitations
- JSON file storage not suitable for high-volume usage
- Single-instance deployment (no horizontal scaling)
- File storage dependent on Telegram's infrastructure
- Session management tied to single bot instance

The architecture prioritizes reliability and automatic recovery over complex scaling, making it ideal for personal or small community file sharing bots with robust session management.
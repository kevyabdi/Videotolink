# File Storage Telegram Bot

## Overview

This is a Telegram bot built with Pyrogram that provides file storage and sharing capabilities. The bot allows users to upload files and receive unique sharing links, with administrative features for user management and statistics tracking.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a simple monolithic architecture with file-based data persistence:

- **Bot Framework**: Pyrogram (Python Telegram bot library)
- **Data Storage**: JSON files for lightweight persistence
- **Authentication**: Telegram-based user identification
- **File Management**: Local file system storage with unique identifiers

## Key Components

### 1. Bot Client
- **Technology**: Pyrogram Client
- **Purpose**: Handles Telegram API interactions
- **Configuration**: Environment-based credentials (API_ID, API_HASH, BOT_TOKEN)

### 2. Data Storage
- **files.json**: Stores file metadata and sharing information
- **stats.json**: Tracks user statistics and usage analytics
- **banned_users.json**: Maintains list of banned users for moderation

### 3. User Management
- **Admin System**: Single admin user with elevated privileges
- **User Tracking**: Statistics collection for each user interaction
- **Ban System**: Admin can ban/unban users
- **Broadcast System**: Admin can send messages to all registered users

### 4. File Handling
- **Upload Processing**: Handles multiple file types (documents, videos, audio, photos)
- **Unique Identifiers**: UUID-based file identification system
- **Download Tracking**: Monitors file access and usage patterns

## Data Flow

1. **File Upload**:
   - User sends file to bot
   - Bot generates unique UUID for file
   - File metadata stored in files.json
   - User receives shareable link

2. **File Retrieval**:
   - User requests file via unique ID
   - Bot validates access permissions
   - File served to authorized user
   - Download statistics updated

3. **Admin Operations**:
   - Statistics viewing and management
   - User ban/unban functionality
   - Broadcast messaging to all users
   - System monitoring capabilities

## External Dependencies

### Required Environment Variables
- `API_ID`: Telegram API application ID
- `API_HASH`: Telegram API hash
- `BOT_TOKEN`: Telegram bot token

### Python Packages
- **pyrogram**: Telegram bot framework
- **Standard libraries**: json, os, uuid, logging, asyncio, time, datetime

## Deployment Strategy

### Local Development
- File-based storage for simplicity
- Environment variable configuration
- Direct Python execution

### Production Considerations
- **Scalability**: Current JSON-based storage suitable for small to medium usage
- **Data Persistence**: Files stored locally (consider cloud storage for production)
- **Monitoring**: Basic logging implemented
- **Security**: Admin-only access for sensitive operations

### Potential Improvements
- Database migration (SQLite/PostgreSQL) for better performance
- Cloud file storage integration
- Enhanced error handling and recovery
- Rate limiting and spam protection
- Backup and recovery mechanisms

## Key Design Decisions

### JSON File Storage
- **Problem**: Need simple, lightweight data persistence
- **Solution**: JSON files for metadata storage
- **Rationale**: Easy to implement, human-readable, sufficient for initial requirements
- **Trade-offs**: Limited scalability but excellent for prototyping and small deployments

### Pyrogram Framework
- **Problem**: Need reliable Telegram bot interaction
- **Solution**: Pyrogram client library
- **Rationale**: Modern async support, comprehensive API coverage, good documentation
- **Alternatives**: python-telegram-bot (more common but different architecture)

### UUID-based File Identification
- **Problem**: Need unique, secure file identifiers
- **Solution**: UUID generation for each file
- **Rationale**: Cryptographically secure, prevents enumeration attacks
- **Benefits**: Scalable, collision-resistant, privacy-preserving

## Recent Changes

### July 28, 2025 - GitHub Repository Setup
- Created comprehensive README.md with full documentation
- Added MIT license and professional .gitignore file
- Implemented DEPLOYMENT.md with multi-platform deployment instructions
- Added keep_alive.py for hosting platform compatibility
- Created requirements_sample.txt for dependency management
- Confirmed broadcast functionality is fully operational
- Enhanced project structure for GitHub deployment and sharing
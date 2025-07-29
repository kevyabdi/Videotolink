# File Storage Telegram Bot - Premium Edition

## Overview

This is an enhanced Telegram bot built with Pyrogram that provides file storage and sharing capabilities with a comprehensive premium user system. The bot allows users to upload files and receive unique sharing links, with usage limits for free users and unlimited access for premium users, plus administrative features for user management and statistics tracking.

## User Preferences

Preferred communication style: Simple, everyday language with premium features integration.

## System Architecture

The application follows a simple monolithic architecture with enhanced file-based data persistence:

- **Bot Framework**: Pyrogram (Python Telegram bot library)
- **Data Storage**: Enhanced JSON files for lightweight persistence with premium tracking
- **Authentication**: Telegram-based user identification with premium status
- **File Management**: Local file system storage with unique identifiers
- **Premium System**: JSON-based premium user management
- **Usage Limits**: Daily upload tracking with cooldown management

## Key Components

### 1. Bot Client
- **Technology**: Pyrogram Client
- **Purpose**: Handles Telegram API interactions with premium features
- **Configuration**: Environment-based credentials (API_ID, API_HASH, BOT_TOKEN)
- **New Features**: Inline keyboard support for JOIN DAAWO buttons

### 2. Enhanced Data Storage
- **files.json**: Stores file metadata and sharing information
- **stats.json**: Enhanced with daily upload tracking and premium statistics
- **banned_users.json**: Maintains list of banned users for moderation
- **premium_users.json**: NEW - Premium user management with timestamps

### 3. Premium User Management
- **Admin System**: Single admin user with premium management privileges
- **Premium Tracking**: JSON-based premium user database
- **Usage Limits**: 5 files/day for free users, unlimited for premium
- **Cooldown System**: 4-hour waiting period after free limit reached
- **Plan Status**: Real-time tracking of user plan and usage

### 4. Enhanced User Management
- **User Tracking**: Enhanced statistics collection with premium status
- **Ban System**: Admin can ban/unban users with premium status preservation
- **Broadcast System**: Admin can send messages to all registered users
- **Contact Integration**: @viizet admin contact for premium upgrades

### 5. File Handling with Premium Features
- **Upload Processing**: Handles multiple file types with usage limit checking
- **Unique Identifiers**: UUID-based file identification system
- **Download Tracking**: Monitors file access and usage patterns
- **Video Enhancement**: JOIN DAAWO button automatically added to videos
- **Premium Benefits**: Unlimited uploads for premium users

## Data Flow

### 1. File Upload (Enhanced)
- User sends file to bot
- Bot checks user premium status and usage limits
- For free users: Verify daily limit (5 files) and cooldown status
- For premium users: Allow unlimited uploads
- Bot generates unique UUID for file
- File metadata stored in files.json with enhanced tracking
- User receives shareable link with plan status information

### 2. File Retrieval (Enhanced)
- User requests file via unique ID
- Bot validates access permissions and ban status
- File served to authorized user
- For videos: JOIN DAAWO button automatically added
- Download statistics updated with premium tracking

### 3. Premium Management
- Admin upgrades/downgrades users with /premium and /unpremium commands
- Premium status tracked in premium_users.json
- Real-time plan checking with /myplan command
- Usage statistics include premium vs free user analytics

### 4. Admin Operations (Enhanced)
- Premium user statistics and management
- Enhanced user ban/unban functionality
- Broadcast messaging to all users
- System monitoring with premium analytics
- Usage limit monitoring and enforcement

## External Dependencies

### Required Environment Variables
- `API_ID`: Telegram API application ID
- `API_HASH`: Telegram API hash
- `BOT_TOKEN`: Telegram bot token

### Python Packages
- **pyrogram**: Telegram bot framework with inline keyboard support
- **flask**: Web server for keep-alive functionality
- **Standard libraries**: json, os, uuid, logging, asyncio, time, datetime, timedelta

### External Integrations
- **JOIN DAAWO**: https://t.me/daawotv (automatic button on videos)
- **Admin Contact**: @viizet (premium upgrades and support)

## Deployment Strategy

### Local Development
- Enhanced file-based storage for premium system
- Environment variable configuration
- Direct Python execution with premium features

### Production Considerations
- **Scalability**: JSON-based storage suitable for small to medium premium user base
- **Data Persistence**: Enhanced files stored locally with premium tracking
- **Premium Management**: Real-time premium status checking
- **Monitoring**: Enhanced logging with premium user activity
- **Security**: Admin-only access for premium management operations

### Potential Improvements
- Database migration (SQLite/PostgreSQL) for better premium user management
- Payment integration for automated premium upgrades
- Enhanced analytics dashboard for premium user tracking
- Bulk premium user management tools
- Premium user referral system

## Key Design Decisions

### Premium System Architecture
- **Problem**: Need to limit free users while providing premium benefits
- **Solution**: JSON-based premium user tracking with daily usage limits
- **Rationale**: Simple implementation, flexible upgrade/downgrade system
- **Trade-offs**: Manual premium management but excellent control and transparency

### Usage Limit Implementation
- **Problem**: Prevent abuse while encouraging premium upgrades
- **Solution**: Daily upload limits (5 for free) with 4-hour cooldown
- **Rationale**: Balances user experience with resource management
- **Benefits**: Clear upgrade incentive, fair usage policy, admin control

### JOIN DAAWO Integration
- **Problem**: Community building and engagement for video content
- **Solution**: Automatic inline button on all video messages
- **Rationale**: Non-intrusive promotion, enhances user experience
- **Implementation**: Pyrogram InlineKeyboardMarkup with direct link

### Admin Contact System
- **Problem**: Premium upgrade requests and user support
- **Solution**: Integrated @viizet contact in messages and commands
- **Rationale**: Clear support channel, professional user experience
- **Benefits**: Centralized support, upgrade request handling

## Enhanced JSON File Storage

### Premium Users Database (premium_users.json)
```json
{
  "user_id": {
    "username": "user_name",
    "is_premium": true,
    "upgraded_at": "2025-07-29T10:00:00",
    "downgraded_at": null
  }
}

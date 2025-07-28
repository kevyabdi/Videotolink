# Telegram File Saver Bot

## Overview

This is a Telegram bot built with Pyrogram that provides file upload, sharing, and management capabilities. The bot features a premium user system, usage analytics, admin controls, and permanent download links. It includes a Flask-based keep-alive server to maintain uptime and provides a web interface showing bot status.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a simple monolithic architecture with the following components:

- **Telegram Bot**: Built using Pyrogram framework for handling Telegram API interactions
- **File Storage**: Local JSON-based storage for metadata and user data
- **Keep-Alive Server**: Flask web server for health monitoring and uptime maintenance
- **User Management**: Role-based system with regular users, premium users, and admin privileges

## Key Components

### 1. Bot Core (`main.py`)
- **Purpose**: Main bot application handling Telegram interactions
- **Framework**: Pyrogram client for Telegram Bot API
- **Authentication**: Uses API credentials from environment variables
- **User Management**: Implements admin controls and user privilege systems

### 2. Keep-Alive Service (`keep_alive.py`)
- **Purpose**: Maintains bot uptime with a web health endpoint
- **Framework**: Flask web server
- **Features**: 
  - Status dashboard at root endpoint
  - Health check endpoint at `/health`
  - Real-time status updates with timestamps

### 3. Data Storage
- **Files Database** (`files.json`): Stores file metadata and sharing information
- **User Statistics** (`stats.json`): Tracks usage analytics and user data
- **Premium Users** (`premium_users.json`): Manages premium user list
- **Banned Users** (`banned_users.json`): Maintains banned user list

## Data Flow

1. **File Upload**: Users send files to bot → Bot processes and stores metadata → Generates unique sharing links
2. **File Sharing**: Users request files via links → Bot validates permissions → Serves file content
3. **User Management**: Admin commands → Update user status in respective JSON files
4. **Analytics**: All interactions → Update statistics in stats.json
5. **Health Monitoring**: External services → Query Flask endpoints → Receive status updates

## External Dependencies

- **Pyrogram**: Telegram MTProto API client library
- **Flask**: Web framework for keep-alive functionality
- **Environment Variables**: 
  - `API_ID`: Telegram API application ID
  - `API_HASH`: Telegram API application hash
  - `BOT_TOKEN`: Telegram bot token

## Deployment Strategy

The application is designed for cloud deployment with the following characteristics:

- **Stateless Design**: All data stored in JSON files for simplicity
- **Environment Configuration**: Credentials managed via environment variables
- **Health Monitoring**: Built-in Flask server for uptime checks
- **Logging**: Structured logging for debugging and monitoring

### Configuration Requirements
- Python environment with Pyrogram and Flask
- Telegram bot token and API credentials
- Admin user ID configuration (currently hardcoded: 1096693642)
- File system access for JSON data storage

### Key Features
- **Premium User System**: Differentiated access levels with upgrade buttons
- **Upload Limits**: Free users limited to 10 uploads, premium users unlimited
- **Ban System**: Admin can ban/unban users
- **Broadcast Messaging**: Admin broadcast capabilities
- **Analytics**: Comprehensive usage tracking with premium user counts
- **Permanent Links**: Persistent file sharing URLs
- **Promotional Features**: "Join Daawotv" buttons on all downloads
- **Interactive Upgrade System**: Premium plan details and contact buttons

### Recent Changes (July 28, 2025)
- ✅ Fixed /help command functionality
- ✅ Added "Join Daawotv" button to all file downloads linking to t.me/daawotv
- ✅ Implemented premium user system with /premium and /unpremium admin commands
- ✅ Added usage tracking showing premium vs free user statistics in /stats
- ✅ Created interactive upgrade buttons in /help and /start commands
- ✅ Added premium plan details with pricing and contact information
- ✅ Integrated Flask keep-alive server running on port 5000
- ✅ Fixed database lock issues and session management

The architecture prioritizes simplicity and rapid deployment while providing essential bot functionality for file management and user administration.
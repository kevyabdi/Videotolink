# YukkiChatBot - Telegram Anonymous Feedback Bot

## Overview

YukkiChatBot is a Telegram bot designed for anonymous feedback collection. The bot can operate in both private and group modes, allowing users to send feedback while providing administrators with comprehensive management tools including user blocking, statistics tracking, and rate limiting.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture
- **Framework**: Python-based Telegram bot using Pyrogram library
- **Storage**: In-memory data structure with JSON file persistence (no database)
- **Deployment**: Single-process application with file-based configuration
- **Communication**: Telegram Bot API for all user interactions

### Design Patterns
- **Modular Architecture**: Separated concerns with distinct modules for configuration, handlers, storage, and utilities
- **Event-Driven**: Handler-based message processing using Pyrogram decorators
- **Stateful Storage**: In-memory data structures with periodic JSON persistence

## Key Components

### Configuration Management (`config.py`)
- **Purpose**: Centralized environment variable management and validation
- **Key Features**: Telegram API credentials, admin settings, rate limiting, and message configuration
- **Validation**: Built-in configuration validation to ensure required settings are present

### Message Handlers (`handlers.py`)
- **Purpose**: Process all incoming Telegram messages and commands
- **Key Features**: Command processing (/start, admin commands), callback handling, and user interaction management
- **Security**: User blocking checks and admin authorization

### Storage System (`storage.py`)
- **Purpose**: In-memory data management with JSON persistence
- **Data Structures**: User data, statistics, rate limiting counters, and message history
- **Persistence**: Auto-save functionality with configurable intervals

### Utilities (`utils.py`)
- **Purpose**: Helper functions for common operations
- **Key Features**: Markdown escaping, statistics formatting, and user information processing

### Main Application (`main.py`)
- **Purpose**: Application entry point and bot lifecycle management
- **Features**: Logging configuration, component initialization, and startup sequence

## Data Flow

### User Interaction Flow
1. User sends message to bot
2. Handler validates user (not blocked, rate limits)
3. Message processed and stored in memory
4. Response sent to user
5. Statistics updated
6. Data persisted to JSON file

### Admin Operations Flow
1. Admin sends command
2. Authorization check against admin IDs
3. Command executed (user management, statistics, settings)
4. Changes reflected in memory storage
5. Updated data persisted to file

### Storage Persistence Flow
1. All operations modify in-memory data structures
2. Auto-save timer triggers periodic JSON write
3. Manual save triggered on critical operations
4. Data loaded from JSON on startup

## External Dependencies

### Required Dependencies
- **Pyrogram**: Telegram Bot API framework for Python
- **Python Standard Library**: JSON, asyncio, logging, datetime, os, typing

### Telegram Integration
- **Bot API**: Uses Telegram Bot API through Pyrogram
- **Authentication**: Requires API_ID, API_HASH, and BOT_TOKEN from BotFather
- **Permissions**: Needs message sending/receiving permissions

### Environment Variables
- **API_ID**: Telegram API identifier
- **API_HASH**: Telegram API hash
- **BOT_TOKEN**: Bot token from BotFather
- **ADMIN_IDS**: Comma-separated list of admin user IDs
- **OWNER_ID**: Primary owner user ID

## Deployment Strategy

### Single-Process Deployment
- **Architecture**: Monolithic application running as single Python process
- **Storage**: File-based JSON persistence (no external database required)
- **Logging**: File and console logging with configurable levels
- **Configuration**: Environment variable-based configuration

### Resource Requirements
- **Minimal**: Low memory footprint with in-memory storage
- **File System**: Write access for JSON persistence and log files
- **Network**: Outbound HTTPS for Telegram API communication

### Scalability Considerations
- **Current**: Single-instance design suitable for small to medium user bases
- **Limitations**: In-memory storage limits horizontal scaling
- **Future**: Can be migrated to database storage for larger deployments

### Error Handling
- **Graceful Degradation**: Bot continues operating even with storage errors
- **Recovery**: Data recovery from JSON files on restart
- **Monitoring**: Comprehensive logging for debugging and monitoring
"""
Utility functions for YukkiChatBot
Helper functions for formatting, validation, and common operations
"""

import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pyrogram.types import User

logger = logging.getLogger(__name__)

def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    if not text:
        return ""
    
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

def format_stats(stats: Dict[str, Any]) -> str:
    """Format statistics for display"""
    try:
        # Parse timestamps
        bot_started = datetime.fromisoformat(stats.get('bot_started', datetime.now().isoformat()))
        last_reset = datetime.fromisoformat(stats.get('last_reset', datetime.now().isoformat()))
        
        # Calculate uptime
        uptime = datetime.now() - bot_started
        uptime_days = uptime.days
        uptime_hours = uptime.seconds // 3600
        uptime_minutes = (uptime.seconds % 3600) // 60
        
        # Format uptime string
        uptime_str = f"{uptime_days}d {uptime_hours}h {uptime_minutes}m"
        
        stats_text = (
            f"👥 **Total Users:** {stats.get('total_users', 0)}\n"
            f"📊 **Active Users (7d):** {stats.get('active_users_7d', 0)}\n"
            f"🚫 **Blocked Users:** {stats.get('total_blocked_users', 0)}\n\n"
            f"💬 **Total Messages:** {stats.get('total_messages', 0)}\n"
            f"📅 **Messages Today:** {stats.get('messages_today', 0)}\n\n"
            f"🤖 **Bot Uptime:** {uptime_str}\n"
            f"📊 **Current Mode:** {stats.get('current_mode', 'private')}\n"
            f"🔄 **Last Reset:** {last_reset.strftime('%Y-%m-%d %H:%M')}"
        )
        
        return stats_text
        
    except Exception as e:
        logger.error(f"Error formatting stats: {e}")
        return "❌ Error formatting statistics"

def get_user_info(user: User) -> Dict[str, Any]:
    """Extract user information from Pyrogram User object"""
    try:
        return {
            'id': user.id,
            'first_name': user.first_name or "",
            'last_name': user.last_name or "",
            'username': user.username or "",
            'language_code': user.language_code or "",
            'is_bot': user.is_bot or False,
            'is_premium': getattr(user, 'is_premium', False),
            'last_seen': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error extracting user info: {e}")
        return {
            'id': user.id if user else 0,
            'first_name': "",
            'last_name': "",
            'username': "",
            'language_code': "",
            'is_bot': False,
            'is_premium': False,
            'last_seen': datetime.now().isoformat()
        }

def validate_user_id(user_id_str: str) -> Optional[int]:
    """Validate and convert user ID string to integer"""
    try:
        user_id = int(user_id_str)
        if user_id > 0:
            return user_id
        return None
    except ValueError:
        return None

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def clean_username(username: str) -> str:
    """Clean and validate username"""
    if not username:
        return ""
    
    # Remove @ if present
    username = username.lstrip('@')
    
    # Validate username format (letters, numbers, underscores, 5-32 chars)
    if re.match(r'^[a-zA-Z0-9_]{5,32}$', username):
        return username
    
    return ""

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    size_index = 0
    size_float = float(size_bytes)
    
    while size_float >= 1024 and size_index < len(size_names) - 1:
        size_float = size_float / 1024.0
        size_index += 1
    
    return f"{size_float:.1f} {size_names[size_index]}"

def is_valid_chat_id(chat_id: str) -> bool:
    """Validate chat ID format"""
    try:
        chat_id_int = int(chat_id)
        # Telegram chat IDs are typically negative for groups/channels
        # and positive for users
        return chat_id_int != 0
    except ValueError:
        return False

def get_message_type(message) -> str:
    """Get the type of message"""
    if not message:
        return "unknown"
    
    if message.text:
        return "text"
    elif message.photo:
        return "photo"
    elif message.video:
        return "video"
    elif message.audio:
        return "audio"
    elif message.voice:
        return "voice"
    elif message.document:
        return "document"
    elif message.sticker:
        return "sticker"
    elif message.animation:
        return "animation"
    elif message.video_note:
        return "video_note"
    elif message.location:
        return "location"
    elif message.contact:
        return "contact"
    elif message.poll:
        return "poll"
    else:
        return "other"

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h {remaining_minutes}m"

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>&"\'`]', '', text)
    
    # Limit length
    sanitized = sanitized[:4096]  # Telegram message limit
    
    return sanitized.strip()

def extract_command_args(message_text: str, command: str) -> list:
    """Extract arguments from command message"""
    if not message_text or not command:
        return []
    
    # Remove the command part
    if message_text.startswith(f'/{command}'):
        args_text = message_text[len(command) + 1:].strip()
        if args_text:
            return args_text.split()
    
    return []

def is_admin_command(command: str) -> bool:
    """Check if command requires admin privileges"""
    admin_commands = [
        'stats', 'block', 'unblock', 'broadcast', 
        'mode', 'reply', 'ban', 'unban', 'admin'
    ]
    return command.lower() in admin_commands

def generate_error_message(error_type: str, details: str = "") -> str:
    """Generate standardized error messages"""
    error_messages = {
        'permission_denied': "❌ You don't have permission to use this command.",
        'invalid_usage': f"❌ Invalid usage. {details}",
        'user_not_found': "❌ User not found.",
        'user_blocked': "❌ You have been blocked from using this bot.",
        'rate_limited': "⏰ You're sending messages too quickly. Please wait a moment.",
        'system_error': "❌ An error occurred. Please try again later.",
        'invalid_input': f"❌ Invalid input. {details}",
        'command_failed': f"❌ Command failed. {details}"
    }
    
    return error_messages.get(error_type, f"❌ Error: {error_type}")

def log_user_action(user_id: int, action: str, details: str = ""):
    """Log user actions for monitoring"""
    timestamp = datetime.now().isoformat()
    log_message = f"[{timestamp}] User {user_id} - {action}"
    if details:
        log_message += f" - {details}"
    
    logger.info(log_message)

def validate_environment_config() -> Dict[str, Any]:
    """Validate environment configuration and return missing variables"""
    required_vars = [
        'API_ID',
        'API_HASH', 
        'BOT_TOKEN'
    ]
    
    missing_vars = []
    
    import os
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return {
        'missing': missing_vars,
        'status': 'valid' if not missing_vars else 'invalid'
    }

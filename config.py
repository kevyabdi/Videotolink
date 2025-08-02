"""
Configuration management for YukkiChatBot
Handles environment variables and bot settings
"""

import os
from typing import List, Optional

class Config:
    """Configuration class for bot settings"""
    
    def __init__(self):
        # Required Telegram API credentials
        self.API_ID: int = int(os.getenv("API_ID", "0"))
        self.API_HASH: str = os.getenv("API_HASH", "")
        self.BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
        
        # Admin configuration
        self.ADMIN_IDS: List[int] = self._parse_admin_ids()
        self.OWNER_ID: int = int(os.getenv("OWNER_ID", "0"))
        
        # Bot settings
        self.BOT_MODE: str = os.getenv("BOT_MODE", "private")  # private or group
        self.TARGET_GROUP_ID: Optional[int] = self._parse_target_group()
        
        # Message settings
        self.MAX_MESSAGE_LENGTH: int = int(os.getenv("MAX_MESSAGE_LENGTH", "4096"))
        self.WELCOME_MESSAGE: str = os.getenv("WELCOME_MESSAGE", self._default_welcome_message())
        
        # Storage settings
        self.DATA_FILE: str = os.getenv("DATA_FILE", "bot_data.json")
        self.AUTO_SAVE_INTERVAL: int = int(os.getenv("AUTO_SAVE_INTERVAL", "300"))  # 5 minutes
        
        # Rate limiting
        self.RATE_LIMIT_MESSAGES: int = int(os.getenv("RATE_LIMIT_MESSAGES", "10"))
        self.RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
        
        # Validate configuration
        self._validate_config()
    
    def _parse_admin_ids(self) -> List[int]:
        """Parse admin IDs from environment variable"""
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        if not admin_ids_str:
            return []
        
        try:
            return [int(id_.strip()) for id_ in admin_ids_str.split(",") if id_.strip()]
        except ValueError:
            return []
    
    def _parse_target_group(self) -> Optional[int]:
        """Parse target group ID from environment variable"""
        group_id_str = os.getenv("TARGET_GROUP_ID", "")
        if not group_id_str:
            return None
        
        try:
            return int(group_id_str)
        except ValueError:
            return None
    
    def _default_welcome_message(self) -> str:
        """Default welcome message"""
        return (
            "👋 Welcome to Anonymous Feedback Bot!\n\n"
            "📝 Send me any message and I'll forward it anonymously to the administrators.\n"
            "🔒 Your identity will remain completely anonymous.\n\n"
            "ℹ️ Use /help for more information."
        )
    
    def _validate_config(self):
        """Validate required configuration"""
        if not self.API_ID or self.API_ID == 0:
            raise ValueError("API_ID is required and must be a valid integer")
        
        if not self.API_HASH:
            raise ValueError("API_HASH is required")
        
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        
        if self.BOT_MODE not in ["private", "group"]:
            raise ValueError("BOT_MODE must be either 'private' or 'group'")
        
        if self.BOT_MODE == "group" and not self.TARGET_GROUP_ID:
            raise ValueError("TARGET_GROUP_ID is required when BOT_MODE is 'group'")
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is an admin"""
        return user_id in self.ADMIN_IDS or user_id == self.OWNER_ID
    
    def is_owner(self, user_id: int) -> bool:
        """Check if user is the owner"""
        return user_id == self.OWNER_ID
    
    def get_target_chat_id(self) -> int:
        """Get target chat ID based on mode"""
        if self.BOT_MODE == "group" and self.TARGET_GROUP_ID:
            return self.TARGET_GROUP_ID
        elif self.ADMIN_IDS:
            return self.ADMIN_IDS[0]  # Send to first admin
        else:
            return self.OWNER_ID

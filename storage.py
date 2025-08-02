"""
In-memory storage management for YukkiChatBot
Handles user data, statistics, and persistence without MongoDB
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Storage:
    """In-memory storage with JSON persistence"""
    
    def __init__(self, data_file: str = "bot_data.json"):
        self.data_file = data_file
        
        # User data storage
        self.users: Dict[int, Dict[str, Any]] = {}
        self.blocked_users: set = set()
        
        # Statistics
        self.stats = {
            "total_users": 0,
            "total_messages": 0,
            "messages_today": 0,
            "last_reset": datetime.now().isoformat(),
            "bot_started": datetime.now().isoformat()
        }
        
        # Rate limiting
        self.user_message_count: Dict[int, List[datetime]] = {}
        
        # Admin settings
        self.bot_settings = {
            "mode": "private",
            "target_group_id": None,
            "welcome_message": None
        }
        
        # Message history for context
        self.message_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        # Message mapping for replies (user_message_id -> admin_chat_message_id)
        self.message_mapping: Dict[str, int] = {}
    
    async def load_data(self):
        """Load data from JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load users (convert string keys back to int)
            if 'users' in data:
                self.users = {int(k): v for k, v in data['users'].items()}
            
            # Load blocked users
            if 'blocked_users' in data:
                self.blocked_users = set(data['blocked_users'])
            
            # Load statistics
            if 'stats' in data:
                self.stats.update(data['stats'])
            
            # Load bot settings
            if 'bot_settings' in data:
                self.bot_settings.update(data['bot_settings'])
            
            # Load message history
            if 'message_history' in data:
                self.message_history = data['message_history'][-self.max_history_size:]
            
            # Load message mapping
            if 'message_mapping' in data:
                self.message_mapping = data['message_mapping']
            
            # Reset daily stats if needed
            await self._check_daily_reset()
            
            logger.info(f"Loaded data for {len(self.users)} users")
            
        except FileNotFoundError:
            logger.info("No existing data file found, starting fresh")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing data file: {e}")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    async def save_data(self):
        """Save data to JSON file"""
        try:
            data = {
                'users': {str(k): v for k, v in self.users.items()},
                'blocked_users': list(self.blocked_users),
                'stats': self.stats,
                'bot_settings': self.bot_settings,
                'message_history': self.message_history[-self.max_history_size:],
                'message_mapping': self.message_mapping
            }
            
            # Write to temporary file first, then rename for atomic operation
            temp_file = f"{self.data_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            import os
            os.replace(temp_file, self.data_file)
            
            logger.debug("Data saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    async def _check_daily_reset(self):
        """Reset daily statistics if needed"""
        try:
            last_reset = datetime.fromisoformat(self.stats['last_reset'])
            now = datetime.now()
            
            if now.date() > last_reset.date():
                self.stats['messages_today'] = 0
                self.stats['last_reset'] = now.isoformat()
                logger.info("Daily statistics reset")
        except Exception as e:
            logger.error(f"Error checking daily reset: {e}")
    
    def add_user(self, user_id: int, user_data: Dict[str, Any]):
        """Add or update user data"""
        is_new_user = user_id not in self.users
        if is_new_user:
            self.users[user_id] = {
                'first_seen': datetime.now().isoformat(),
                'message_count': 0,
                'last_activity': datetime.now().isoformat(),
                'welcomed': False,
                **user_data
            }
            self.stats['total_users'] += 1
        else:
            self.users[user_id].update(user_data)
            self.users[user_id]['last_activity'] = datetime.now().isoformat()
        return is_new_user
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data"""
        return self.users.get(user_id)
    
    def is_user_blocked(self, user_id: int) -> bool:
        """Check if user is blocked"""
        return user_id in self.blocked_users
    
    def block_user(self, user_id: int):
        """Block a user"""
        self.blocked_users.add(user_id)
        logger.info(f"User {user_id} blocked")
    
    def unblock_user(self, user_id: int):
        """Unblock a user"""
        self.blocked_users.discard(user_id)
        logger.info(f"User {user_id} unblocked")
    
    def increment_message_count(self, user_id: int):
        """Increment message count for user and global stats"""
        if user_id in self.users:
            self.users[user_id]['message_count'] += 1
        
        self.stats['total_messages'] += 1
        self.stats['messages_today'] += 1
    
    def check_rate_limit(self, user_id: int, max_messages: int, window_seconds: int) -> bool:
        """Check if user is rate limited"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)
        
        # Initialize if not exists
        if user_id not in self.user_message_count:
            self.user_message_count[user_id] = []
        
        # Remove old messages
        self.user_message_count[user_id] = [
            msg_time for msg_time in self.user_message_count[user_id]
            if msg_time > cutoff
        ]
        
        # Check limit
        if len(self.user_message_count[user_id]) >= max_messages:
            return True  # Rate limited
        
        # Add current message
        self.user_message_count[user_id].append(now)
        return False  # Not rate limited
    
    def add_message_to_history(self, message_data: Dict[str, Any]):
        """Add message to history"""
        message_data['timestamp'] = datetime.now().isoformat()
        self.message_history.append(message_data)
        
        # Keep only recent messages
        if len(self.message_history) > self.max_history_size:
            self.message_history = self.message_history[-self.max_history_size:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bot statistics"""
        active_users_7d = 0
        week_ago = datetime.now() - timedelta(days=7)
        
        for user_data in self.users.values():
            try:
                last_activity = datetime.fromisoformat(user_data['last_activity'])
                if last_activity > week_ago:
                    active_users_7d += 1
            except:
                pass
        
        return {
            **self.stats,
            'active_users_7d': active_users_7d,
            'total_blocked_users': len(self.blocked_users),
            'current_mode': self.bot_settings.get('mode', 'private')
        }
    
    def get_all_user_ids(self) -> List[int]:
        """Get all user IDs (excluding blocked users)"""
        return [uid for uid in self.users.keys() if uid not in self.blocked_users]
    
    def set_bot_mode(self, mode: str, target_group_id: Optional[int] = None):
        """Set bot mode"""
        self.bot_settings['mode'] = mode
        if target_group_id:
            self.bot_settings['target_group_id'] = target_group_id
    
    def get_bot_mode(self) -> str:
        """Get current bot mode"""
        return self.bot_settings.get('mode', 'private')
    
    def get_target_group_id(self) -> Optional[int]:
        """Get target group ID"""
        return self.bot_settings.get('target_group_id')
    
    def set_user_welcomed(self, user_id: int):
        """Mark user as welcomed"""
        if user_id in self.users:
            self.users[user_id]['welcomed'] = True
    
    def is_user_welcomed(self, user_id: int) -> bool:
        """Check if user has been welcomed"""
        return self.users.get(user_id, {}).get('welcomed', False)
    
    def store_message_mapping(self, user_message_key: str, admin_message_id: int):
        """Store mapping between user message and admin message for replies"""
        self.message_mapping[user_message_key] = admin_message_id
    
    def get_admin_message_id(self, user_message_key: str) -> Optional[int]:
        """Get admin message ID for reply mapping"""
        return self.message_mapping.get(user_message_key)

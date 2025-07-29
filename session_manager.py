"""
Robust session management for Pyrogram with automatic recovery
"""

import os
import logging
from pyrogram import Client
from pyrogram.errors import (
    SessionRevoked, 
    AuthKeyUnregistered, 
    AuthKeyDuplicated,
    UserDeactivated,
    Unauthorized
)

logger = logging.getLogger(__name__)

class SessionManager:
    """Handles Pyrogram session management with automatic recovery"""
    
    def __init__(self, session_name, api_id, api_hash, bot_token=None):
        self.session_name = session_name
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.client = None
        
    def _remove_session_files(self):
        """Remove all session-related files for clean start"""
        session_files = [
            f"{self.session_name}.session",
            f"{self.session_name}.session-journal",
            f"{self.session_name}.session-wal", 
            f"{self.session_name}.session-shm"
        ]
        
        removed = []
        for file_path in session_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    removed.append(file_path)
                    logger.info(f"Removed corrupted session file: {file_path}")
                except OSError as e:
                    logger.warning(f"Could not remove {file_path}: {e}")
        
        return removed
    
    def create_client(self):
        """Create Pyrogram client with proper configuration"""
        try:
            if self.bot_token:
                # Bot client
                client = Client(
                    name=self.session_name,
                    api_id=self.api_id,
                    api_hash=self.api_hash,
                    bot_token=self.bot_token,
                    in_memory=False  # Use persistent sessions
                )
            else:
                # User client  
                client = Client(
                    name=self.session_name,
                    api_id=self.api_id,
                    api_hash=self.api_hash,
                    in_memory=False
                )
            
            return client
            
        except Exception as e:
            logger.error(f"Failed to create client: {e}")
            raise
    
    def connect_with_recovery(self, max_retries=3):
        """Connect to Telegram with automatic session recovery"""
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Connection attempt {attempt + 1}/{max_retries}")
                
                # Create fresh client
                self.client = self.create_client()
                
                # Try to start the client
                self.client.start()
                logger.info("✅ Successfully connected to Telegram!")
                return self.client
                
            except (SessionRevoked, AuthKeyUnregistered, AuthKeyDuplicated) as e:
                logger.warning(f"Session error on attempt {attempt + 1}: {e}")
                
                # Clean up corrupted session files
                removed_files = self._remove_session_files()
                if removed_files:
                    logger.info(f"Cleaned up {len(removed_files)} session files")
                
                # Stop current client if it exists
                if self.client:
                    try:
                        self.client.stop()
                    except:
                        pass
                    self.client = None
                
                if attempt == max_retries - 1:
                    logger.error("❌ All session recovery attempts failed")
                    raise
                    
                logger.info("🔄 Retrying with fresh session...")
                continue
                
            except UserDeactivated as e:
                logger.error(f"❌ Account deactivated: {e}")
                raise
                
            except Unauthorized as e:
                logger.error(f"❌ Authorization failed: {e}")
                
                # Try cleaning session and retry once
                if attempt == 0:
                    self._remove_session_files()
                    continue
                raise
                
            except Exception as e:
                logger.error(f"❌ Unexpected error on attempt {attempt + 1}: {e}")
                
                # Clean up on unexpected errors too
                if attempt < max_retries - 1:
                    self._remove_session_files()
                    if self.client:
                        try:
                            self.client.stop()
                        except:
                            pass
                        self.client = None
                    continue
                raise
        
        raise Exception("Failed to establish connection after all retry attempts")
    
    def disconnect(self):
        """Safely disconnect the client"""
        if self.client:
            try:
                self.client.stop()
                logger.info("Client disconnected successfully")
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")
            finally:
                self.client = None
    
    def get_client(self):
        """Get the active client instance"""
        return self.client
    
    def is_connected(self):
        """Check if client is connected"""
        return self.client is not None and self.client.is_connected
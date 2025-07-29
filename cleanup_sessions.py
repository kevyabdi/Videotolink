#!/usr/bin/env python3
"""
Session cleanup utility to remove corrupted Pyrogram session files
Run this script if you encounter SESSION_REVOKED errors
"""

import os
import glob
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_session_files():
    """Remove all Pyrogram session files to force re-authentication"""
    
    # Common session file patterns
    session_patterns = [
        "*.session",
        "*.session-journal", 
        "*.session-wal",
        "*.session-shm",
        "filetobot.session*",
        "my_account.session*"
    ]
    
    removed_files = []
    
    for pattern in session_patterns:
        files = glob.glob(pattern)
        for file_path in files:
            try:
                os.remove(file_path)
                removed_files.append(file_path)
                logger.info(f"Removed session file: {file_path}")
            except OSError as e:
                logger.warning(f"Could not remove {file_path}: {e}")
    
    if removed_files:
        logger.info(f"Successfully removed {len(removed_files)} session files")
        logger.info("Session cleanup complete. Bot will re-authenticate on next start.")
    else:
        logger.info("No session files found to remove")
    
    return removed_files

if __name__ == "__main__":
    print("🧹 Cleaning up corrupted session files...")
    cleanup_session_files()
    print("✅ Cleanup complete! You can now restart the bot.")

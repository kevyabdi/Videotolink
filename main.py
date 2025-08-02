#!/usr/bin/env python3
"""
YukkiChatBot - Telegram Bot for Anonymous Feedback Collection
Main entry point for the bot application
"""

import asyncio
import logging
from pyrogram.client import Client
from config import Config
from handlers import register_handlers
from storage import Storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class YukkiChatBot:
    """Main bot class"""
    
    def __init__(self):
        self.config = Config()
        self.storage = Storage()
        
        # Initialize Pyrogram client
        self.app = Client(
            "YukkiChatBot",
            api_id=self.config.API_ID,
            api_hash=self.config.API_HASH,
            bot_token=self.config.BOT_TOKEN,
            workdir="."
        )
        
        # Register all handlers
        register_handlers(self.app, self.storage, self.config)
    
    async def start(self):
        """Start the bot"""
        try:
            logger.info("Starting YukkiChatBot...")
            await self.app.start()
            
            # Get bot info
            me = await self.app.get_me()
            logger.info(f"Bot started successfully: @{me.username}")
            
            # Load existing data
            await self.storage.load_data()
            logger.info("Storage data loaded successfully")
            
            # Keep the bot running
            await asyncio.Event().wait()
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
    
    async def stop(self):
        """Stop the bot"""
        try:
            logger.info("Stopping bot...")
            await self.storage.save_data()
            await self.app.stop()
            logger.info("Bot stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")

async def main():
    """Main function"""
    bot = YukkiChatBot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await bot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown completed")
    except Exception as e:
        logger.error(f"Fatal error: {e}")

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import SessionRevoked, AuthKeyUnregistered, Unauthorized
import json
import os
import uuid
import logging
import asyncio
import time
from datetime import datetime, timedelta
from session_manager import SessionManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get credentials from environment variables with proper fallbacks
API_ID = int(os.getenv("API_ID", "26176218"))
API_HASH = os.getenv("API_HASH", "4a50bc8acb0169930f5914eb88091736")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8452579938:AAGeNe_GEes9iiCDRz99bk94ubkbTbbzm7M")

# Admin user ID
ADMIN_USER_ID = 1096693642

# Global variables
app = None
session_manager = None

def initialize_bot():
    """Initialize bot with session recovery"""
    global app, session_manager
    
    try:
        logger.info("🚀 Initializing Telegram bot with session recovery...")
        
        # Create session manager
        session_manager = SessionManager(
            session_name="filetobot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN
        )
        
        # Connect with automatic recovery
        app = session_manager.connect_with_recovery(max_retries=3)
        
        if app and session_manager.is_connected():
            logger.info("✅ Bot initialized successfully!")
            return True
        else:
            logger.error("❌ Failed to initialize bot")
            return False
            
    except Exception as e:
        logger.error(f"❌ Critical error during bot initialization: {e}")
        return False

# Ensure JSON databases exist
def ensure_json_files():
    """Ensure all required JSON files exist with proper structure"""
    
    files_to_create = {
        "files.json": {},
        "stats.json": {
            "total_users": 0,
            "total_files": 0,
            "files_by_type": {"document": 0, "video": 0, "audio": 0, "photo": 0},
            "downloads": 0,
            "users": {}
        },
        "banned_users.json": [],
        "premium_users.json": {}
    }
    
    for filename, default_content in files_to_create.items():
        if not os.path.exists(filename):
            try:
                with open(filename, "w", encoding='utf-8') as f:
                    json.dump(default_content, f, indent=2, ensure_ascii=False)
                logger.info(f"Created {filename} with default structure")
            except Exception as e:
                logger.error(f"Failed to create {filename}: {e}")

# Initialize JSON files
ensure_json_files()

def load_files():
    """Load file mappings from JSON database"""
    try:
        with open("files.json", "r", encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading files.json: {e}")
        return {}

def load_stats():
    """Load statistics from JSON database"""
    try:
        with open("stats.json", "r", encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading stats.json: {e}")
        return {
            "total_users": 0,
            "total_files": 0,
            "files_by_type": {"document": 0, "video": 0, "audio": 0, "photo": 0},
            "downloads": 0,
            "users": {}
        }

def load_premium_users():
    """Load premium users from JSON database"""
    try:
        with open("premium_users.json", "r", encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading premium_users.json: {e}")
        return {}

def save_premium_users(premium_data):
    """Save premium users to JSON database"""
    try:
        with open("premium_users.json", "w", encoding='utf-8') as f:
            json.dump(premium_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving premium_users.json: {e}")
        return False

def is_premium_user(user_id):
    """Check if user has premium status"""
    premium_users = load_premium_users()
    user_str = str(user_id)
    return user_str in premium_users and premium_users[user_str].get("is_premium", False)

def add_premium_user(user_id, username):
    """Add user to premium list"""
    premium_users = load_premium_users()
    user_str = str(user_id)
    premium_users[user_str] = {
        "username": username,
        "is_premium": True,
        "upgraded_at": datetime.utcnow().isoformat()
    }
    return save_premium_users(premium_users)

def remove_premium_user(user_id):
    """Remove user from premium list"""
    premium_users = load_premium_users()
    user_str = str(user_id)
    if user_str in premium_users:
        premium_users[user_str]["is_premium"] = False
        premium_users[user_str]["downgraded_at"] = datetime.utcnow().isoformat()
    return save_premium_users(premium_users)

def get_user_upload_count(user_id):
    """Get user's upload count for today"""
    stats = load_stats()
    user_str = str(user_id)
    if user_str not in stats["users"]:
        return 0
    
    user_data = stats["users"][user_str]
    today = datetime.utcnow().date().isoformat()
    return user_data.get("daily_uploads", {}).get(today, 0)

def get_user_last_upload_time(user_id):
    """Get user's last upload time"""
    stats = load_stats()
    user_str = str(user_id)
    if user_str not in stats["users"]:
        return None
    
    return stats["users"][user_str].get("last_upload_time")

def can_user_upload(user_id):
    """Check if user can upload based on limits - No restrictions now"""
    # Removed all upload restrictions per the original code modification
    return True, None

def update_stats(user_id, username, action, file_type=None):
    """Update user statistics"""
    try:
        stats = load_stats()
        user_str = str(user_id)
        
        # Initialize user if not exists
        if user_str not in stats["users"]:
            stats["users"][user_str] = {
                "username": username,
                "files_uploaded": 0,
                "downloads": 0,
                "first_seen": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat(),
                "daily_uploads": {},
                "last_upload_time": None
            }
            stats["total_users"] += 1
        
        # Update last seen
        stats["users"][user_str]["last_seen"] = datetime.utcnow().isoformat()
        stats["users"][user_str]["username"] = username
        
        # Update action-specific stats
        if action == "upload" and file_type:
            stats["users"][user_str]["files_uploaded"] += 1
            stats["users"][user_str]["last_upload_time"] = datetime.utcnow().isoformat()
            stats["total_files"] += 1
            stats["files_by_type"][file_type] += 1
            
            # Update daily upload count
            today = datetime.utcnow().date().isoformat()
            if "daily_uploads" not in stats["users"][user_str]:
                stats["users"][user_str]["daily_uploads"] = {}
            stats["users"][user_str]["daily_uploads"][today] = stats["users"][user_str]["daily_uploads"].get(today, 0) + 1
            
        elif action == "download":
            stats["users"][user_str]["downloads"] += 1
            stats["downloads"] += 1
        
        # Save updated stats
        with open("stats.json", "w", encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error updating stats: {e}")
        return False

def is_admin(user_id):
    """Check if user is admin"""
    return user_id == ADMIN_USER_ID

def load_banned_users():
    """Load banned users list"""
    try:
        with open("banned_users.json", "r", encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading banned_users.json: {e}")
        return []

def save_banned_users(banned_list):
    """Save banned users list"""
    try:
        with open("banned_users.json", "w", encoding='utf-8') as f:
            json.dump(banned_list, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving banned_users.json: {e}")
        return False

def is_banned(user_id):
    """Check if user is banned"""
    banned_users = load_banned_users()
    return user_id in banned_users

def ban_user(user_id):
    """Ban a user"""
    banned_users = load_banned_users()
    if user_id not in banned_users:
        banned_users.append(user_id)
        return save_banned_users(banned_users)
    return True

def unban_user(user_id):
    """Unban a user"""
    banned_users = load_banned_users()
    if user_id in banned_users:
        banned_users.remove(user_id)
        return save_banned_users(banned_users)
    return True

def save_file_mapping(file_id, unique_id, file_type, original_caption=None):
    """Save file ID, type and original caption mapping to JSON database"""
    try:
        data = load_files()
        data[unique_id] = {
            "file_id": file_id,
            "file_type": file_type,
            "original_caption": original_caption,
            "timestamp": datetime.utcnow().isoformat()
        }
        with open("files.json", "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved file mapping for unique_id: {unique_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving file mapping: {e}")
        return False

async def handle_session_error(client, error):
    """Handle session-related errors with automatic recovery"""
    global app, session_manager
    
    logger.warning(f"Session error detected: {error}")
    
    try:
        # Stop current client
        if client:
            try:
                client.stop()
            except:
                pass
        
        # Reinitialize bot
        success = initialize_bot()
        if success:
            logger.info("✅ Session recovered successfully!")
            return app
        else:
            logger.error("❌ Failed to recover session")
            return None
            
    except Exception as e:
        logger.error(f"Error during session recovery: {e}")
        return None

# Set up handlers only after successful initialization
def setup_handlers():
    """Set up all bot handlers"""
    global app
    
    if not app:
        logger.error("Cannot setup handlers - app not initialized")
        return
    
    @app.on_message(filters.command("start"))
    async def start_command(client, message):
        """Handle /start command with welcome message and file sharing"""
        try:
            # Check if user is banned
            if is_banned(message.from_user.id):
                await message.reply_text("❌ You have been banned from using this bot.\n\n📞 Contact Admin: @viizet")
                logger.info(f"Banned user {message.from_user.id} tried to access /start")
                return

            # Update user statistics
            username = message.from_user.username or message.from_user.first_name or "Unknown"
            update_stats(message.from_user.id, username, "start")

            # Check if there's a file ID parameter in the /start command
            if len(message.command) > 1:
                unique_id = message.command[1].strip()
                if unique_id:
                    # Handle file sharing request
                    await handle_file_request(client, message, unique_id)
                    return

            # No file ID parameter, show welcome message
            welcome_text = (
                "🔒 Secure & Private File Sharing\n"
                "• Files are stored using Telegram's infrastructure\n"
                "• No external hosting required\n"
                "• Links work indefinitely\n\n"
                "📤 Send me a file to get started!\n\n"
                "📞 Need help? Contact Admin: @viizet"
            )

            # Create inline keyboard with DM Owner and DAAWO buttons
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("💬 DM Owner", url="https://t.me/viizet"),
                    InlineKeyboardButton("📺 Join DAAWO ↗", url="https://t.me/daawotv")
                ]
            ])

            await message.reply_text(welcome_text, reply_markup=keyboard)
            logger.info(f"User {message.from_user.id} ({username}) used /start command")

        except (SessionRevoked, AuthKeyUnregistered, Unauthorized) as e:
            logger.warning(f"Session error in start_command: {e}")
            recovered_client = await handle_session_error(client, e)
            if recovered_client:
                # Retry the command with recovered client
                await start_command(recovered_client, message)
            else:
                await message.reply_text("❌ Temporary connection issue. Please try again in a moment.")
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await message.reply_text("❌ An error occurred. Please try again later.\n\n📞 Contact Admin: @viizet")

    @app.on_message(filters.document | filters.video | filters.audio | filters.photo)
    async def file_handler(client, message):
        """Handle incoming file uploads"""
        try:
            # Check if user is banned
            if is_banned(message.from_user.id):
                await message.reply_text("❌ You have been banned from using this bot.\n\n📞 Contact Admin: @viizet")
                logger.info(f"Banned user {message.from_user.id} tried to upload file")
                return

            # No upload limits - all users can upload unlimited files
            file = None
            file_type = ""
            display_type = "📁 File"

            if message.document:
                file = message.document
                file_type = "document"
                display_type = "📄 Document"
            elif message.video:
                file = message.video
                file_type = "video"
                display_type = "🎥 Video"
            elif message.audio:
                file = message.audio
                file_type = "audio"
                display_type = "🎵 Audio"
            elif message.photo:
                file = message.photo
                file_type = "photo"
                display_type = "🖼️ Photo"

            if not file:
                await message.reply_text("❌ No valid file detected. Please send a valid file.")
                return

            # Generate unique ID for the file
            unique_id = str(uuid.uuid4()).replace('-', '')[:16]

            # Get file info
            file_name = getattr(file, 'file_name', f"{file_type}_{unique_id}")
            if not file_name:
                file_name = f"{file_type}_{unique_id}"

            file_size = getattr(file, 'file_size', 0)
            file_id = file.file_id

            # Save original caption if exists
            original_caption = message.caption

            # Save file mapping to database
            if save_file_mapping(file_id, unique_id, file_type, original_caption):
                # Update user statistics
                username = message.from_user.username or message.from_user.first_name or "Unknown"
                update_stats(message.from_user.id, username, "upload", file_type)

                # Create shareable link
                bot_username = (await client.get_me()).username
                share_link = f"https://t.me/{bot_username}?start={unique_id}"

                # Format file size
                if file_size > 0:
                    if file_size < 1024 * 1024:  # Less than 1MB
                        size_str = f"{file_size / 1024:.1f} KB"
                    else:  # 1MB or more
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"
                else:
                    size_str = "Unknown size"

                # Create response message
                response_text = (
                    f"✅ {display_type} uploaded successfully!\n\n"
                    f"📁 **File:** `{file_name}`\n"
                    f"📊 **Size:** {size_str}\n"
                    f"🔗 **Share Link:** {share_link}\n\n"
                    f"💡 Anyone can access your file using this link!"
                )

                # Create inline keyboard
                keyboard_buttons = [
                    [InlineKeyboardButton("🔗 Copy Link", url=share_link)]
                ]

                # Add JOIN DAAWO button for videos
                if file_type == "video":
                    keyboard_buttons.append([
                        InlineKeyboardButton("📺 JOIN DAAWO ↗", url="https://t.me/daawotv")
                    ])

                keyboard = InlineKeyboardMarkup(keyboard_buttons)

                await message.reply_text(response_text, reply_markup=keyboard)
                logger.info(f"User {message.from_user.id} uploaded {file_type}: {file_name}")

            else:
                await message.reply_text("❌ Failed to save file. Please try again.\n\n📞 Contact Admin: @viizet")

        except (SessionRevoked, AuthKeyUnregistered, Unauthorized) as e:
            logger.warning(f"Session error in file_handler: {e}")
            recovered_client = await handle_session_error(client, e)
            if recovered_client:
                await file_handler(recovered_client, message)
            else:
                await message.reply_text("❌ Temporary connection issue. Please try again in a moment.")
        except Exception as e:
            logger.error(f"Error in file handler: {e}")
            await message.reply_text("❌ An error occurred while processing your file. Please try again.\n\n📞 Contact Admin: @viizet")

    async def handle_file_request(client, message, unique_id):
        """Handle file download requests from shared links"""
        try:
            files_data = load_files()
            
            if unique_id not in files_data:
                await message.reply_text(
                    "❌ File not found or has been removed.\n\n"
                    "📞 Contact Admin: @viizet"
                )
                return

            file_info = files_data[unique_id]
            file_id = file_info["file_id"]
            file_type = file_info["file_type"]
            original_caption = file_info.get("original_caption")

            # Update download statistics
            username = message.from_user.username or message.from_user.first_name or "Unknown"
            update_stats(message.from_user.id, username, "download")

            # Send the file back to user
            caption_text = f"📥 File shared via File Saver Bot\n\n📞 Contact Admin: @viizet"
            
            if original_caption:
                caption_text = f"{original_caption}\n\n---\n{caption_text}"

            # Create inline keyboard
            keyboard_buttons = []
            
            # Add JOIN DAAWO button for videos
            if file_type == "video":
                keyboard_buttons.append([
                    InlineKeyboardButton("📺 JOIN DAAWO ↗", url="https://t.me/daawotv")
                ])
            
            keyboard_buttons.append([
                InlineKeyboardButton("💬 DM Owner", url="https://t.me/viizet")
            ])

            keyboard = InlineKeyboardMarkup(keyboard_buttons)

            # Send file based on type
            if file_type == "document":
                await client.send_document(
                    chat_id=message.chat.id,
                    document=file_id,
                    caption=caption_text,
                    reply_markup=keyboard
                )
            elif file_type == "video":
                await client.send_video(
                    chat_id=message.chat.id,
                    video=file_id,
                    caption=caption_text,
                    reply_markup=keyboard
                )
            elif file_type == "audio":
                await client.send_audio(
                    chat_id=message.chat.id,
                    audio=file_id,
                    caption=caption_text,
                    reply_markup=keyboard
                )
            elif file_type == "photo":
                await client.send_photo(
                    chat_id=message.chat.id,
                    photo=file_id,
                    caption=caption_text,
                    reply_markup=keyboard
                )

            logger.info(f"User {message.from_user.id} downloaded file {unique_id}")

        except (SessionRevoked, AuthKeyUnregistered, Unauthorized) as e:
            logger.warning(f"Session error in handle_file_request: {e}")
            recovered_client = await handle_session_error(client, e)
            if recovered_client:
                await handle_file_request(recovered_client, message, unique_id)
            else:
                await message.reply_text("❌ Temporary connection issue. Please try again in a moment.")
        except Exception as e:
            logger.error(f"Error handling file request: {e}")
            await message.reply_text("❌ Error retrieving file. Please try again later.\n\n📞 Contact Admin: @viizet")

    # Admin commands
    @app.on_message(filters.command("stats") & filters.user(ADMIN_USER_ID))
    async def stats_command(client, message):
        """Show bot statistics (admin only)"""
        try:
            stats = load_stats()
            premium_users = load_premium_users()
            
            premium_count = sum(1 for user in premium_users.values() if user.get("is_premium", False))
            
            stats_text = (
                f"📊 **Bot Statistics**\n\n"
                f"👥 **Total Users:** {stats['total_users']}\n"
                f"⭐ **Premium Users:** {premium_count}\n"
                f"📁 **Total Files:** {stats['total_files']}\n"
                f"📥 **Total Downloads:** {stats['downloads']}\n\n"
                f"**Files by Type:**\n"
                f"📄 Documents: {stats['files_by_type']['document']}\n"
                f"🎥 Videos: {stats['files_by_type']['video']}\n"
                f"🎵 Audio: {stats['files_by_type']['audio']}\n"
                f"🖼️ Photos: {stats['files_by_type']['photo']}"
            )
            
            await message.reply_text(stats_text)
            
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await message.reply_text(f"❌ Error retrieving stats: {e}")

    logger.info("✅ All bot handlers have been set up successfully!")

def run_bot():
    """Main function to run the bot with error handling"""
    try:
        # Initialize bot
        if not initialize_bot():
            logger.error("❌ Failed to initialize bot. Exiting.")
            return
        
        # Setup handlers
        setup_handlers()
        
        # Bot is already running from SessionManager, just keep it alive
        logger.info("🚀 Telegram bot is running and ready!")
        logger.info("📱 You can now interact with your bot on Telegram")
        
        # Keep the bot running indefinitely
        import asyncio
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        
    except Exception as e:
        logger.error(f"❌ Fatal error in bot execution: {e}")
    finally:
        # Cleanup
        if session_manager:
            session_manager.disconnect()
        logger.info("Bot has been stopped.")

if __name__ == "__main__":
    # Import and start keep-alive server
    try:
        from keep_alive import keep_alive
        keep_alive()
        logger.info("✅ Keep-alive server started")
    except ImportError:
        logger.warning("Keep-alive module not found, continuing without web server")
    except Exception as e:
        logger.warning(f"Failed to start keep-alive server: {e}")
    
    # Run the bot
    run_bot()

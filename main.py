from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import json
import os
import uuid
import logging
import asyncio
import time
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get credentials from environment variables
API_ID = int(os.getenv("API_ID", "26176218"))
API_HASH = os.getenv("API_HASH", "4a50bc8acb0169930f5914eb88091736")
BOT_TOKEN = os.getenv("BOT_TOKEN", "AAGeNe_GEes9iiCDRZ99bk94ubkbTbbzm7M")

# Admin user ID (replace with your Telegram user ID)
ADMIN_USER_ID = 1096693642  # Replace with your actual Telegram user ID

# Initialize the Pyrogram client
app = Client("filetobot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Ensure files.json exists
if not os.path.exists("files.json"):
    with open("files.json", "w") as f:
        json.dump({}, f)
    logger.info("Created new files.json database")

# Ensure stats.json exists for user statistics
if not os.path.exists("stats.json"):
    with open("stats.json", "w") as f:
        json.dump({
            "total_users": 0,
            "total_files": 0,
            "files_by_type": {"document": 0, "video": 0, "audio": 0, "photo": 0},
            "downloads": 0,
            "users": {}
        }, f, indent=2)
    logger.info("Created new stats.json database")

# Ensure banned_users.json exists
if not os.path.exists("banned_users.json"):
    with open("banned_users.json", "w") as f:
        json.dump([], f)
    logger.info("Created new banned_users.json database")

# Ensure premium_users.json exists
if not os.path.exists("premium_users.json"):
    with open("premium_users.json", "w") as f:
        json.dump({}, f)
    logger.info("Created new premium_users.json database")

def load_files():
    """Load file mappings from JSON database"""
    try:
        with open("files.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading files.json: {e}")
        return {}

def load_stats():
    """Load statistics from JSON database"""
    try:
        with open("stats.json", "r") as f:
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
        with open("premium_users.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading premium_users.json: {e}")
        return {}

def save_premium_users(premium_data):
    """Save premium users to JSON database"""
    try:
        with open("premium_users.json", "w") as f:
            json.dump(premium_data, f, indent=2)
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
    """Check if user can upload based on limits"""
    if is_premium_user(user_id):
        return True, None
    
    upload_count = get_user_upload_count(user_id)
    if upload_count < 10:
        return True, None
    
    last_upload_time = get_user_last_upload_time(user_id)
    if last_upload_time:
        last_upload = datetime.fromisoformat(last_upload_time)
        time_since_last = datetime.utcnow() - last_upload
        if time_since_last < timedelta(hours=5):
            remaining_time = timedelta(hours=5) - time_since_last
            hours = int(remaining_time.total_seconds() // 3600)
            minutes = int((remaining_time.total_seconds() % 3600) // 60)
            return False, f"{hours}h {minutes}m"
    
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
        stats["users"][user_str]["username"] = username  # Update in case username changed
        
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
        with open("stats.json", "w") as f:
            json.dump(stats, f, indent=2)
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
        with open("banned_users.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading banned_users.json: {e}")
        return []

def save_banned_users(banned_list):
    """Save banned users list"""
    try:
        with open("banned_users.json", "w") as f:
            json.dump(banned_list, f, indent=2)
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
        with open("files.json", "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved file mapping for unique_id: {unique_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving file mapping: {e}")
        return False

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

    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.reply_text("❌ An error occurred. Please try again later.\n\n📞 Contact Admin: @viizet")

# Premium features removed

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
            await message.reply_text("❌ Unable to process this file type.\n\n📞 Contact Admin: @viizet")
            return

        file_id = file.file_id
        unique_id = file.file_unique_id
        original_caption = message.caption if message.caption else None

        # Update statistics
        username = message.from_user.username or message.from_user.first_name or "Unknown"
        update_stats(message.from_user.id, username, "upload", file_type)

        if save_file_mapping(file_id, unique_id, file_type, original_caption):
            bot_me = await app.get_me()
            bot_username = bot_me.username
            share_link = f"https://t.me/{bot_username}?start={unique_id}"
            
            file_size = ""
            if hasattr(file, 'file_size') and file.file_size:
                size_mb = file.file_size / (1024 * 1024)
                file_size = f" ({size_mb:.1f} MB)" if size_mb >= 1 else f" ({file.file_size} bytes)"
            
            file_name = ""
            if hasattr(file, 'file_name') and file.file_name:
                file_name = f"\n📝 Name: {file.file_name}"
            
            response_text = (
                f"✅ File uploaded successfully!\n\n"
                f"📂 Type: {display_type}{file_size}"
                f"{file_name}\n"
                f"🔗 Share Link:\n{share_link}\n\n"
                f"📞 Contact Admin: @viizet"
            )

            # Create keyboard based on file type
            if file_type == "video":
                # Add JOIN DAAWO button for videos
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📺 JOIN DAAWO ↗", url="https://t.me/daawotv")]
                ])
                await message.reply_text(response_text, reply_markup=keyboard)
            else:
                await message.reply_text(response_text)

            logger.info(f"File uploaded by {username} ({message.from_user.id}): {file_type} - {unique_id}")
        else:
            await message.reply_text("❌ Failed to save file. Please try again.\n\n📞 Contact Admin: @viizet")

    except Exception as e:
        logger.error(f"Error in file handler: {e}")
        await message.reply_text("❌ An error occurred while processing your file.\n\n📞 Contact Admin: @viizet")

@app.on_message(filters.text & filters.private)
async def text_handler(client, message):
    """Handle text messages for file retrieval"""
    try:
        # Check if user is banned
        if is_banned(message.from_user.id):
            await message.reply_text("❌ You have been banned from using this bot.\n\n📞 Contact Admin: @viizet")
            logger.info(f"Banned user {message.from_user.id} tried to access text handler")
            return

        text = message.text.strip()
        
        # Handle /start with parameter (file sharing)
        if text.startswith('/start '):
            unique_id = text.replace('/start ', '').strip()
            if unique_id:
                await handle_file_request(client, message, unique_id)
            else:
                await message.reply_text("❌ Invalid file link.\n\n📞 Contact Admin: @viizet")
        # Handle direct unique ID
        elif len(text) > 10:  # Assume it's a unique ID if long enough
            await handle_file_request(client, message, text)
        else:
            # Unknown text message - show simple help
            help_text = (
                "ℹ️ **How to use this bot:**\n\n"
                "📁 **Upload Files:** Send any document, video, audio, or photo\n"
                "🔗 **Get Links:** Receive permanent sharing links\n"
                "🔒 **Secure:** Files stored using Telegram's infrastructure\n\n"
                "📺 **Join Community:** @daawotv\n"
                "📞 **Need help?** Contact @viizet"
            )
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("💬 DM Owner", url="https://t.me/viizet"),
                    InlineKeyboardButton("📺 Join DAAWO ↗", url="https://t.me/daawotv")
                ]
            ])
            
            await message.reply_text(help_text, reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Error in text handler: {e}")
        await message.reply_text("❌ An error occurred.\n\n📞 Contact Admin: @viizet")

async def handle_file_request(client, message, unique_id):
    """Handle file download requests"""
    try:
        data = load_files()
        
        if unique_id not in data:
            await message.reply_text("❌ File not found or expired.\n\n📞 Contact Admin: @viizet")
            return

        file_data = data[unique_id]
        file_id = file_data["file_id"]
        file_type = file_data["file_type"]
        original_caption = file_data.get("original_caption")

        # Update download statistics
        username = message.from_user.username or message.from_user.first_name or "Unknown"
        update_stats(message.from_user.id, username, "download")

        # Send the file with original caption if it exists
        caption = original_caption if original_caption else "📁 Downloaded from File Saver Bot\n\n📞 Contact Admin: @viizet"
        
        # Send the file based on type
        if file_type == "video":
            # Add JOIN DAAWO button for videos
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📺 JOIN DAAWO ↗", url="https://t.me/daawotv")]
            ])
            await client.send_video(message.chat.id, file_id, caption=caption, reply_markup=keyboard)
        elif file_type == "document":
            await client.send_document(message.chat.id, file_id, caption=caption)
        elif file_type == "audio":
            await client.send_audio(message.chat.id, file_id, caption=caption)
        elif file_type == "photo":
            await client.send_photo(message.chat.id, file_id, caption=caption)

        logger.info(f"File {unique_id} downloaded by {username} ({message.from_user.id})")

    except Exception as e:
        logger.error(f"Error handling file request: {e}")
        await message.reply_text("❌ Error retrieving file. Please try again.\n\n📞 Contact Admin: @viizet")

# /upgrade command removed (premium features disabled)

# /myplan command removed (premium features disabled)

# Premium admin commands removed

@app.on_message(filters.command("stats") & filters.user(ADMIN_USER_ID))
async def stats_command(client, message):
    """Handle /stats command for admin"""
    try:
        stats = load_stats()

        stats_text = (
            "📊 **Bot Statistics**\n\n"
            f"👥 **Users:** {stats['total_users']}\n\n"
            f"📁 **Files:**\n"
            f"• Total uploaded: {stats['total_files']}\n"
            f"• Documents: {stats['files_by_type']['document']}\n"
            f"• Videos: {stats['files_by_type']['video']}\n"
            f"• Audio: {stats['files_by_type']['audio']}\n"
            f"• Photos: {stats['files_by_type']['photo']}\n\n"
            f"📈 **Downloads:** {stats['downloads']}\n\n"
            f"📞 **Admin:** @viizet"
        )

        await message.reply_text(stats_text)

    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        await message.reply_text("❌ An error occurred.")

@app.on_message(filters.command("users") & filters.user(ADMIN_USER_ID))
async def users_command(client, message):
    """Handle /users command for admin"""
    try:
        stats = load_stats()
        
        if not stats["users"]:
            await message.reply_text("📊 No users found.")
            return

        users_text = "👥 **User List**\n\n"
        count = 0
        
        for user_id, user_data in stats["users"].items():
            if count >= 20:  # Limit to prevent message too long
                users_text += f"\n... and {len(stats['users']) - 20} more users"
                break
                
            username = user_data.get("username", "Unknown")
            files_uploaded = user_data.get("files_uploaded", 0)
            
            users_text += f"• {username} ({user_id})\n  Files: {files_uploaded}\n\n"
            count += 1

        await message.reply_text(users_text)

    except Exception as e:
        logger.error(f"Error in users command: {e}")
        await message.reply_text("❌ An error occurred.")

@app.on_message(filters.command("ban") & filters.user(ADMIN_USER_ID))
async def ban_command(client, message):
    """Handle /ban command for admin"""
    try:
        if len(message.command) != 2:
            await message.reply_text("❌ Usage: /ban <user_id>")
            return

        try:
            target_user_id = int(message.command[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Use numeric ID.")
            return

        if target_user_id == ADMIN_USER_ID:
            await message.reply_text("❌ Cannot ban admin user.")
            return

        if ban_user(target_user_id):
            await message.reply_text(f"✅ User {target_user_id} has been banned!")
            logger.info(f"Admin {message.from_user.id} banned user {target_user_id}")
        else:
            await message.reply_text("❌ Failed to ban user.")

    except Exception as e:
        logger.error(f"Error in ban command: {e}")
        await message.reply_text("❌ An error occurred.")

@app.on_message(filters.command("unban") & filters.user(ADMIN_USER_ID))
async def unban_command(client, message):
    """Handle /unban command for admin"""
    try:
        if len(message.command) != 2:
            await message.reply_text("❌ Usage: /unban <user_id>")
            return

        try:
            target_user_id = int(message.command[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Use numeric ID.")
            return

        if unban_user(target_user_id):
            await message.reply_text(f"✅ User {target_user_id} has been unbanned!")
            logger.info(f"Admin {message.from_user.id} unbanned user {target_user_id}")
        else:
            await message.reply_text("❌ Failed to unban user.")

    except Exception as e:
        logger.error(f"Error in unban command: {e}")
        await message.reply_text("❌ An error occurred.")

@app.on_message(filters.command("banned") & filters.user(ADMIN_USER_ID))
async def banned_command(client, message):
    """Handle /banned command for admin"""
    try:
        banned_users = load_banned_users()
        
        if not banned_users:
            await message.reply_text("📊 No banned users found.")
            return

        banned_text = "🚫 **Banned Users**\n\n"
        for user_id in banned_users:
            banned_text += f"• {user_id}\n"

        await message.reply_text(banned_text)

    except Exception as e:
        logger.error(f"Error in banned command: {e}")
        await message.reply_text("❌ An error occurred.")

@app.on_message(filters.command("broadcast") & filters.user(ADMIN_USER_ID))
async def broadcast_command(client, message):
    """Handle /broadcast command for admin"""
    try:
        if len(message.command) < 2:
            await message.reply_text("❌ Usage: /broadcast <message>")
            return

        broadcast_message = " ".join(message.command[1:])
        stats = load_stats()
        
        if not stats["users"]:
            await message.reply_text("📊 No users found to broadcast to.")
            return

        success_count = 0
        failed_count = 0
        
        status_message = await message.reply_text("📡 Broadcasting message...")
        
        for user_id in stats["users"].keys():
            try:
                user_id_int = int(user_id)
                if not is_banned(user_id_int):
                    await client.send_message(user_id_int, f"📢 **Admin Broadcast**\n\n{broadcast_message}")
                    success_count += 1
                    await asyncio.sleep(0.1)  # Small delay to avoid flooding
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send broadcast to {user_id}: {e}")

        await status_message.edit_text(
            f"📡 **Broadcast Complete**\n\n"
            f"✅ Sent: {success_count}\n"
            f"❌ Failed: {failed_count}\n"
            f"📊 Total users: {len(stats['users'])}"
        )

    except Exception as e:
        logger.error(f"Error in broadcast command: {e}")
        await message.reply_text("❌ An error occurred.")

if __name__ == "__main__":
    try:
        # Import and start keep-alive server
        from keep_alive import keep_alive
        keep_alive()
        
        logger.info("Starting Telegram File Saver Bot with premium features...")
        app.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")

from pyrogram import filters
from pyrogram.client import Client
import json
import os
import uuid
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get credentials from environment variables
API_ID = int(os.getenv("API_ID", "26176218"))
API_HASH = os.getenv("API_HASH", "4a50bc8acb0169930f5914eb88091736")
BOT_TOKEN = os.getenv("BOT_TOKEN", "6872287601:AAFrxXxXU9s4V0CJHxybBQ-cvMYP9fJFxyg")

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
                "last_seen": datetime.utcnow().isoformat()
            }
            stats["total_users"] += 1
        
        # Update last seen
        stats["users"][user_str]["last_seen"] = datetime.utcnow().isoformat()
        stats["users"][user_str]["username"] = username  # Update in case username changed
        
        # Update action-specific stats
        if action == "upload" and file_type:
            stats["users"][user_str]["files_uploaded"] += 1
            stats["total_files"] += 1
            stats["files_by_type"][file_type] += 1
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

@app.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def file_handler(client, message):
    """Handle incoming file uploads"""
    try:
        # Check if user is banned
        if is_banned(message.from_user.id):
            await message.reply_text("❌ You have been banned from using this bot.")
            logger.info(f"Banned user {message.from_user.id} tried to upload file")
            return

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
            await message.reply_text("❌ Unable to process this file type.")
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
                f"💡 Anyone with this link can download your file!"
            )

            await message.reply_text(response_text, parse_mode=None)
            logger.info(f"File uploaded by user {message.from_user.id}: {display_type}")
        else:
            await message.reply_text("❌ Failed to save file. Please try again.")

    except Exception as e:
        logger.error(f"Error handling file upload: {e}")
        await message.reply_text("❌ An error occurred while processing your file. Please try again.")

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    """Handle /start command and file retrieval"""
    try:
        # Check if user is banned
        if is_banned(message.from_user.id):
            await message.reply_text("❌ You have been banned from using this bot.")
            logger.info(f"Banned user {message.from_user.id} tried to use start command")
            return

        args = message.text.split()

        if len(args) == 2:
            file_key = args[1]
            files = load_files()

            if file_key in files:
                file_data = files[file_key]
                file_id = file_data.get("file_id")
                file_type = file_data.get("file_type")
                original_caption = file_data.get("original_caption")

                await message.reply_text("📤 Sending your file...")

                # Update download statistics
                username = message.from_user.username or message.from_user.first_name or "Unknown"
                update_stats(message.from_user.id, username, "download")

                try:
                    if file_type == "photo":
                        await client.send_photo(message.chat.id, file_id, caption=original_caption)
                    elif file_type == "video":
                        await client.send_video(message.chat.id, file_id, caption=original_caption)
                    elif file_type == "audio":
                        await client.send_audio(message.chat.id, file_id, caption=original_caption)
                    else:
                        await client.send_document(message.chat.id, file_id, caption=original_caption)

                    logger.info(f"File retrieved by user {message.from_user.id}: {file_key}")
                except Exception as e:
                    logger.error(f"Error sending file {file_key}: {e}")
                    await message.reply_text(
                        "❌ File not accessible\n\n"
                        "This file may have been deleted from Telegram's servers or is no longer available."
                    )
            else:
                await message.reply_text(
                    "❌ File not found\n\n"
                    "The file you're looking for doesn't exist or the link is invalid."
                )
        else:
            welcome_text = (
                "👋 Welcome to File Saver Bot!\n\n"
                "📁 How it works:\n"
                "1️⃣ Send me any file (document, video, audio, or photo)\n"
                "2️⃣ Get a unique shareable download link\n"
                "3️⃣ Anyone with the link can download your file\n\n"
                "🔒 Secure & Private\n"
                "• Files are stored using Telegram's infrastructure\n"
                "• No external hosting required\n"
                "• Links work indefinitely\n\n"
                "📤 Send me a file to get started!"
            )

            await message.reply_text(welcome_text, parse_mode=None)
            logger.info(f"New user started the bot: {message.from_user.id}")

    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@app.on_message(filters.command("stats"))
async def stats_handler(client, message):
    """Handle /stats command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.")
            return

        stats = load_stats()
        
        # Calculate active users (users who interacted in last 30 days)
        active_users = 0
        from datetime import datetime, timedelta
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        
        for user_data in stats["users"].values():
            if user_data["last_seen"] > thirty_days_ago:
                active_users += 1

        # Get top uploaders
        top_uploaders = sorted(
            [(uid, data) for uid, data in stats["users"].items()],
            key=lambda x: x[1]["files_uploaded"],
            reverse=True
        )[:5]

        stats_text = (
            f"📊 **Bot Statistics**\n\n"
            f"👥 **Users:**\n"
            f"• Total Users: {stats['total_users']}\n"
            f"• Active Users (30 days): {active_users}\n\n"
            f"📁 **Files:**\n"
            f"• Total Files: {stats['total_files']}\n"
            f"• Documents: {stats['files_by_type']['document']}\n"
            f"• Videos: {stats['files_by_type']['video']}\n"
            f"• Audio: {stats['files_by_type']['audio']}\n"
            f"• Photos: {stats['files_by_type']['photo']}\n\n"
            f"📥 **Downloads:** {stats['downloads']}\n\n"
            f"🏆 **Top Uploaders:**\n"
        )

        for i, (uid, data) in enumerate(top_uploaders, 1):
            username = data['username']
            files = data['files_uploaded']
            stats_text += f"{i}. @{username}: {files} files\n"

        await message.reply_text(stats_text, parse_mode=None)
        logger.info(f"Admin {message.from_user.id} requested statistics")

    except Exception as e:
        logger.error(f"Error in stats handler: {e}")
        await message.reply_text("❌ An error occurred while retrieving statistics.")

@app.on_message(filters.command("users"))
async def users_handler(client, message):
    """Handle /users command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.")
            return

        stats = load_stats()
        users_list = []
        
        for uid, data in stats["users"].items():
            username = data['username']
            files = data['files_uploaded']
            downloads = data['downloads']
            last_seen = data['last_seen'][:10]  # Just the date part
            users_list.append((username, files, downloads, last_seen))

        # Sort by files uploaded
        users_list.sort(key=lambda x: x[1], reverse=True)

        users_text = f"👥 **User List** (Total: {len(users_list)})\n\n"
        
        for i, (username, files, downloads, last_seen) in enumerate(users_list[:20], 1):
            users_text += f"{i}. @{username}\n"
            users_text += f"   📁 Files: {files} | 📥 Downloads: {downloads}\n"
            users_text += f"   📅 Last seen: {last_seen}\n\n"

        if len(users_list) > 20:
            users_text += f"... and {len(users_list) - 20} more users"

        await message.reply_text(users_text, parse_mode=None)
        logger.info(f"Admin {message.from_user.id} requested user list")

    except Exception as e:
        logger.error(f"Error in users handler: {e}")
        await message.reply_text("❌ An error occurred while retrieving user list.")

@app.on_message(filters.command("ban"))
async def ban_handler(client, message):
    """Handle /ban command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.")
            return

        args = message.text.split()
        if len(args) != 2:
            await message.reply_text("❌ Usage: /ban <user_id>\nExample: /ban 123456789")
            return

        try:
            user_id_to_ban = int(args[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")
            return

        # Prevent admin from banning themselves
        if user_id_to_ban == ADMIN_USER_ID:
            await message.reply_text("❌ You cannot ban yourself!")
            return

        if is_banned(user_id_to_ban):
            await message.reply_text(f"⚠️ User {user_id_to_ban} is already banned.")
            return

        if ban_user(user_id_to_ban):
            await message.reply_text(f"✅ User {user_id_to_ban} has been banned successfully.")
            logger.info(f"Admin {message.from_user.id} banned user {user_id_to_ban}")
        else:
            await message.reply_text("❌ Failed to ban user. Please try again.")

    except Exception as e:
        logger.error(f"Error in ban handler: {e}")
        await message.reply_text("❌ An error occurred while banning user.")

@app.on_message(filters.command("unban"))
async def unban_handler(client, message):
    """Handle /unban command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.")
            return

        args = message.text.split()
        if len(args) != 2:
            await message.reply_text("❌ Usage: /unban <user_id>\nExample: /unban 123456789")
            return

        try:
            user_id_to_unban = int(args[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")
            return

        if not is_banned(user_id_to_unban):
            await message.reply_text(f"⚠️ User {user_id_to_unban} is not banned.")
            return

        if unban_user(user_id_to_unban):
            await message.reply_text(f"✅ User {user_id_to_unban} has been unbanned successfully.")
            logger.info(f"Admin {message.from_user.id} unbanned user {user_id_to_unban}")
        else:
            await message.reply_text("❌ Failed to unban user. Please try again.")

    except Exception as e:
        logger.error(f"Error in unban handler: {e}")
        await message.reply_text("❌ An error occurred while unbanning user.")

@app.on_message(filters.command("banned"))
async def banned_list_handler(client, message):
    """Handle /banned command - Admin only - Show banned users list"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.")
            return

        banned_users = load_banned_users()
        
        if not banned_users:
            await message.reply_text("✅ No users are currently banned.")
            return

        stats = load_stats()
        banned_text = f"🚫 **Banned Users** (Total: {len(banned_users)})\n\n"

        for i, user_id in enumerate(banned_users, 1):
            user_str = str(user_id)
            username = "Unknown"
            
            # Try to get username from stats
            if user_str in stats["users"]:
                username = stats["users"][user_str].get("username", "Unknown")
            
            banned_text += f"{i}. @{username} (ID: {user_id})\n"

        await message.reply_text(banned_text, parse_mode=None)
        logger.info(f"Admin {message.from_user.id} requested banned users list")

    except Exception as e:
        logger.error(f"Error in banned list handler: {e}")
        await message.reply_text("❌ An error occurred while retrieving banned users list.")

@app.on_message(filters.command("help"))
async def help_handler(client, message):
    """Handle /help command"""
    help_text = (
        "📖 Help - File Saver Bot\n\n"
        "🔧 Commands:\n"
        "• /start - Start the bot or retrieve a file\n"
        "• /help - Show this help message\n\n"
        "📤 Uploading Files:\n"
        "• Send any document, video, audio, or photo\n"
        "• Get a unique shareable link instantly\n"
        "• Share the link with anyone\n\n"
        "📥 Downloading Files:\n"
        "• Click any file link you received\n"
        "• Files are sent back automatically\n\n"
        "💡 Tips:\n"
        "• Links work indefinitely\n"
        "• No file size limits (Telegram's limits apply)\n"
        "• All file types supported\n"
        "• Files stored securely on Telegram servers"
    )
    
    # Add admin commands if user is admin
    if is_admin(message.from_user.id):
        help_text += (
            "\n\n🔐 Admin Commands:\n"
            "• /stats - View bot statistics\n"
            "• /users - View user list\n"
            "• /ban <user_id> - Ban a user\n"
            "• /unban <user_id> - Unban a user\n"
            "• /banned - View banned users list"
        )

    await message.reply_text(help_text, parse_mode=None)

@app.on_message(filters.text & ~filters.command(["start", "help", "stats", "users", "ban", "unban", "banned"]))
async def text_handler(client, message):
    """Handle regular text messages"""
    # Check if user is banned
    if is_banned(message.from_user.id):
        await message.reply_text("❌ You have been banned from using this bot.")
        logger.info(f"Banned user {message.from_user.id} tried to send text message")
        
        
    
        
    

if __name__ == "__main__":
    logger.info("Starting File Saver Bot Sug waxyar...")
    try:
        # Import and start the keep-alive server (optional for some deployments)
        try:
            from keep_alive import keep_alive
            keep_alive()
        except ImportError:
            logger.info("keep_alive module not found, skipping web server")
        
        # Start the bot
        app.run()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
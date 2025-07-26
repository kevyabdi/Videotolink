from pyrogram import filters
from pyrogram.client import Client
import json
import os
import uuid
import logging
from datetime import datetime, timedelta
import asyncio
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get credentials from environment variables
API_ID = int(os.getenv("API_ID", "26176218"))
API_HASH = os.getenv("API_HASH", "4a50bc8acb0169930f5914eb88091736")
BOT_TOKEN = os.getenv("BOT_TOKEN", "6847890390:AAG7sASVY1IJbrbjX6GT5CCXUxD7_mtY_VA")

# Admin user ID (replace with your Telegram user ID)
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "1096693642"))  # Set via environment variable

# Initialize the Pyrogram client
app = Client("filetobot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Command cooldown settings (in seconds)
COMMAND_COOLDOWN = 2  # 2 seconds between commands
FILE_UPLOAD_COOLDOWN = 1  # 1 second between file uploads

# User session tracking for duplicate prevention
user_sessions = {}
user_last_command = {}

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

# Ensure user_sessions.json exists for session tracking
if not os.path.exists("user_sessions.json"):
    with open("user_sessions.json", "w") as f:
        json.dump({}, f)
        logger.info("Created new user_sessions.json database")

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

def load_user_sessions():
    """Load user sessions from JSON database"""
    try:
        with open("user_sessions.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading user_sessions.json: {e}")
        return {}

def save_user_sessions(sessions):
    """Save user sessions to JSON database"""
    try:
        with open("user_sessions.json", "w") as f:
            json.dump(sessions, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving user_sessions.json: {e}")
        return False

def check_command_cooldown(user_id, command_type="general"):
    """Check if user is on cooldown for commands"""
    current_time = time.time()
    user_key = f"{user_id}_{command_type}"
    
    if user_key in user_last_command:
        time_diff = current_time - user_last_command[user_key]
        cooldown_time = FILE_UPLOAD_COOLDOWN if command_type == "file" else COMMAND_COOLDOWN
        
        if time_diff < cooldown_time:
            return False, cooldown_time - time_diff
    
    user_last_command[user_key] = current_time
    return True, 0

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
    """Handle incoming file uploads with duplicate prevention"""
    try:
        # Check if user is banned
        if is_banned(message.from_user.id):
            await message.reply_text("❌ You have been banned from using this bot.")
            logger.info(f"Banned user {message.from_user.id} tried to upload file")
            return

        # Check cooldown for file uploads
        can_proceed, wait_time = check_command_cooldown(message.from_user.id, "file")
        if not can_proceed:
            await message.reply_text(f"⏰ Please wait {wait_time:.1f} seconds before uploading another file.")
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
    """Handle /start command and file retrieval with session tracking"""
    try:
        # Check if user is banned
        if is_banned(message.from_user.id):
            await message.reply_text("❌ You have been banned from using this bot.")
            logger.info(f"Banned user {message.from_user.id} tried to use start command")
            return

        # Check cooldown
        can_proceed, wait_time = check_command_cooldown(message.from_user.id)
        if not can_proceed:
            await message.reply_text(f"⏰ Please wait {wait_time:.1f} seconds before using commands.")
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
            # Check if user already received welcome message in this session
            sessions = load_user_sessions()
            user_str = str(message.from_user.id)
            current_time = datetime.utcnow().isoformat()
            
            # Only send welcome if user hasn't been welcomed in the last hour
            should_welcome = True
            if user_str in sessions:
                last_welcome = sessions[user_str].get("last_welcome")
                if last_welcome:
                    last_welcome_time = datetime.fromisoformat(last_welcome)
                    if datetime.utcnow() - last_welcome_time < timedelta(hours=1):
                        should_welcome = False
            
            if should_welcome:
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
                    "📤 Send me a file to get started!\n"
                    "💡 Use /help for more commands"
                )

                await message.reply_text(welcome_text, parse_mode=None)
                
                # Update session
                if user_str not in sessions:
                    sessions[user_str] = {}
                sessions[user_str]["last_welcome"] = current_time
                save_user_sessions(sessions)
                
                logger.info(f"Welcome message sent to user: {message.from_user.id}")
            else:
                # Just acknowledge without spam
                await message.reply_text("👋 Welcome back! Send me a file to get a shareable link.")

    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@app.on_message(filters.command("help"))
async def help_handler(client, message):
    """Handle /help command"""
    try:
        # Check if user is banned
        if is_banned(message.from_user.id):
            await message.reply_text("❌ You have been banned from using this bot.")
            return

        # Check cooldown
        can_proceed, wait_time = check_command_cooldown(message.from_user.id)
        if not can_proceed:
            await message.reply_text(f"⏰ Please wait {wait_time:.1f} seconds before using commands.")
            return

        help_text = (
            "🆘 **File Saver Bot Help**\n\n"
            "**📁 Basic Commands:**\n"
            "• Send any file → Get shareable download link\n"
            "• /start → Welcome message and bot info\n"
            "• /help → Show this help message\n\n"
            "**📂 Supported File Types:**\n"
            "• 📄 Documents (PDF, DOC, ZIP, etc.)\n"
            "• 🎥 Videos (MP4, AVI, MKV, etc.)\n"
            "• 🎵 Audio (MP3, WAV, OGG, etc.)\n"
            "• 🖼️ Photos (JPG, PNG, GIF, etc.)\n\n"
            "**🔒 Privacy & Security:**\n"
            "• Files stored on Telegram's secure servers\n"
            "• No third-party hosting\n"
            "• Permanent download links\n"
            "• Original file quality preserved\n\n"
            "**💡 Tips:**\n"
            "• Videos keep their original captions\n"
            "• Share links work indefinitely\n"
            "• No file size limits (Telegram limits apply)\n"
            "• Fast upload and download speeds"
        )

        if is_admin(message.from_user.id):
            help_text += (
                "\n\n**🔧 Admin Commands:**\n"
                "• /stats → View bot statistics\n"
                "• /users → List all users\n"
                "• /ban <user_id> → Ban a user\n"
                "• /unban <user_id> → Unban a user\n"
                "• /banned → View banned users list"
            )

        await message.reply_text(help_text, parse_mode="Markdown")
        logger.info(f"Help command used by user: {message.from_user.id}")

    except Exception as e:
        logger.error(f"Error in help handler: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@app.on_message(filters.command("stats"))
async def stats_handler(client, message):
    """Handle /stats command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.")
            return

        # Check cooldown
        can_proceed, wait_time = check_command_cooldown(message.from_user.id)
        if not can_proceed:
            await message.reply_text(f"⏰ Please wait {wait_time:.1f} seconds before using commands.")
            return

        stats = load_stats()
        
        # Calculate active users (users who interacted in last 30 days)
        active_users = 0
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
            username = data.get("username", "Unknown")
            files_count = data.get("files_uploaded", 0)
            stats_text += f"{i}. {username}: {files_count} files\n"

        if not top_uploaders:
            stats_text += "None yet\n"

        # Add banned users count
        banned_count = len(load_banned_users())
        stats_text += f"\n🚫 **Banned Users:** {banned_count}"

        await message.reply_text(stats_text, parse_mode="Markdown")
        logger.info(f"Stats command used by admin: {message.from_user.id}")

    except Exception as e:
        logger.error(f"Error in stats handler: {e}")
        await message.reply_text("❌ An error occurred while fetching statistics.")

@app.on_message(filters.command("users"))
async def users_handler(client, message):
    """Handle /users command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.")
            return

        # Check cooldown
        can_proceed, wait_time = check_command_cooldown(message.from_user.id)
        if not can_proceed:
            await message.reply_text(f"⏰ Please wait {wait_time:.1f} seconds before using commands.")
            return

        stats = load_stats()
        users = stats.get("users", {})

        if not users:
            await message.reply_text("📭 No users found in the database.")
            return

        # Sort users by last seen (most recent first)
        sorted_users = sorted(
            users.items(),
            key=lambda x: x[1].get("last_seen", ""),
            reverse=True
        )

        users_text = f"👥 **Bot Users** (Total: {len(users)})\n\n"
        
        for i, (uid, data) in enumerate(sorted_users[:20], 1):  # Show first 20 users
            username = data.get("username", "Unknown")
            files_uploaded = data.get("files_uploaded", 0)
            downloads = data.get("downloads", 0)
            last_seen = data.get("last_seen", "Unknown")
            
            # Format last seen
            try:
                last_seen_dt = datetime.fromisoformat(last_seen)
                days_ago = (datetime.utcnow() - last_seen_dt).days
                if days_ago == 0:
                    last_seen_str = "Today"
                elif days_ago == 1:
                    last_seen_str = "Yesterday"
                else:
                    last_seen_str = f"{days_ago} days ago"
            except:
                last_seen_str = "Unknown"

            users_text += (
                f"{i}. **{username}** (ID: {uid})\n"
                f"   📤 Files: {files_uploaded} | 📥 Downloads: {downloads}\n"
                f"   🕐 Last seen: {last_seen_str}\n\n"
            )

        if len(users) > 20:
            users_text += f"... and {len(users) - 20} more users\n"

        users_text += "\n💡 Use /ban <user_id> to ban a user"

        await message.reply_text(users_text, parse_mode="Markdown")
        logger.info(f"Users command used by admin: {message.from_user.id}")

    except Exception as e:
        logger.error(f"Error in users handler: {e}")
        await message.reply_text("❌ An error occurred while fetching users list.")

@app.on_message(filters.command("ban"))
async def ban_handler(client, message):
    """Handle /ban command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.")
            return

        # Check cooldown
        can_proceed, wait_time = check_command_cooldown(message.from_user.id)
        if not can_proceed:
            await message.reply_text(f"⏰ Please wait {wait_time:.1f} seconds before using commands.")
            return

        args = message.text.split()
        if len(args) != 2:
            await message.reply_text("❌ Usage: /ban <user_id>\n\nExample: /ban 123456789")
            return

        try:
            user_id_to_ban = int(args[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a valid numeric user ID.")
            return

        # Prevent admin from banning themselves
        if user_id_to_ban == ADMIN_USER_ID:
            await message.reply_text("❌ You cannot ban yourself!")
            return

        # Check if user exists in stats
        stats = load_stats()
        user_str = str(user_id_to_ban)
        username = "Unknown"
        
        if user_str in stats.get("users", {}):
            username = stats["users"][user_str].get("username", "Unknown")

        if ban_user(user_id_to_ban):
            await message.reply_text(f"✅ User banned successfully!\n\n👤 User: {username}\n🆔 ID: {user_id_to_ban}")
            logger.info(f"User {user_id_to_ban} banned by admin {message.from_user.id}")
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

        # Check cooldown
        can_proceed, wait_time = check_command_cooldown(message.from_user.id)
        if not can_proceed:
            await message.reply_text(f"⏰ Please wait {wait_time:.1f} seconds before using commands.")
            return

        args = message.text.split()
        if len(args) != 2:
            await message.reply_text("❌ Usage: /unban <user_id>\n\nExample: /unban 123456789")
            return

        try:
            user_id_to_unban = int(args[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a valid numeric user ID.")
            return

        # Check if user is actually banned
        if not is_banned(user_id_to_unban):
            await message.reply_text("❌ This user is not banned.")
            return

        # Get username from stats
        stats = load_stats()
        user_str = str(user_id_to_unban)
        username = "Unknown"
        
        if user_str in stats.get("users", {}):
            username = stats["users"][user_str].get("username", "Unknown")

        if unban_user(user_id_to_unban):
            await message.reply_text(f"✅ User unbanned successfully!\n\n👤 User: {username}\n🆔 ID: {user_id_to_unban}")
            logger.info(f"User {user_id_to_unban} unbanned by admin {message.from_user.id}")
        else:
            await message.reply_text("❌ Failed to unban user. Please try again.")

    except Exception as e:
        logger.error(f"Error in unban handler: {e}")
        await message.reply_text("❌ An error occurred while unbanning user.")

@app.on_message(filters.command("banned"))
async def banned_handler(client, message):
    """Handle /banned command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.")
            return

        # Check cooldown
        can_proceed, wait_time = check_command_cooldown(message.from_user.id)
        if not can_proceed:
            await message.reply_text(f"⏰ Please wait {wait_time:.1f} seconds before using commands.")
            return

        banned_users = load_banned_users()
        
        if not banned_users:
            await message.reply_text("📋 No banned users found.")
            return

        stats = load_stats()
        banned_text = f"🚫 **Banned Users** (Total: {len(banned_users)})\n\n"

        for i, user_id in enumerate(banned_users, 1):
            user_str = str(user_id)
            username = "Unknown"
            
            # Get username from stats if available
            if user_str in stats.get("users", {}):
                username = stats["users"][user_str].get("username", "Unknown")
            
            banned_text += f"{i}. **{username}** (ID: {user_id})\n"

        banned_text += "\n💡 Use /unban <user_id> to unban a user"

        await message.reply_text(banned_text, parse_mode="Markdown")
        logger.info(f"Banned users list viewed by admin: {message.from_user.id}")

    except Exception as e:
        logger.error(f"Error in banned handler: {e}")
        await message.reply_text("❌ An error occurred while fetching banned users list.")

# Handle unknown commands
@app.on_message(filters.command(["unknown"]) | (filters.text & filters.regex("^/")))
async def unknown_command_handler(client, message):
    """Handle unknown commands"""
    try:
        # Check if user is banned
        if is_banned(message.from_user.id):
            return

        # Don't respond to known commands
        known_commands = ["start", "help", "stats", "users", "ban", "unban", "banned"]
        command = message.text.split()[0][1:]  # Remove the '/' prefix
        
        if command in known_commands:
            return

        await message.reply_text(
            "❓ Unknown command. Use /help to see available commands.",
            parse_mode=None
        )

    except Exception as e:
        logger.error(f"Error in unknown command handler: {e}")

# Start the keep_alive server in a separate thread
def start_keep_alive():
    """Start the keep-alive web server"""
    try:
        from keep_alive import keep_alive
        keep_alive()
        logger.info("Keep-alive server started")
    except ImportError:
        logger.warning("keep_alive module not found, skipping web server")
    except Exception as e:
        logger.error(f"Error starting keep-alive server: {e}")

if __name__ == "__main__":
    try:
        # Start keep-alive server
        start_keep_alive()
        
        # Verify credentials
        if not API_ID or not API_HASH or not BOT_TOKEN:
            logger.error("Missing required environment variables: API_ID, API_HASH, or BOT_TOKEN")
            exit(1)
        
        if not ADMIN_USER_ID:
            logger.warning("ADMIN_USER_ID not set. Admin commands will not work.")
        
        logger.info("Starting Telegram File Saver Bot...")
        logger.info(f"Admin User ID: {ADMIN_USER_ID}")
        
        # Run the bot
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

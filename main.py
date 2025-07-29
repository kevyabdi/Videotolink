from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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
BOT_TOKEN = os.getenv("BOT_TOKEN", "8452579938:AAGeNe_GEes9iiCDRz99bk94ubkbTbbzm7M")

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
    if upload_count < 5:
        return True, None
    
    last_upload_time = get_user_last_upload_time(user_id)
    if last_upload_time:
        last_upload = datetime.fromisoformat(last_upload_time)
        time_since_last = datetime.utcnow() - last_upload
        if time_since_last < timedelta(hours=4):
            remaining_time = timedelta(hours=4) - time_since_last
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

@app.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def file_handler(client, message):
    """Handle incoming file uploads"""
    try:
        # Check if user is banned
        if is_banned(message.from_user.id):
            await message.reply_text("❌ You have been banned from using this bot.\n\n📞 Contact Admin: @viizet")
            logger.info(f"Banned user {message.from_user.id} tried to upload file")
            return

        # Check upload limits
        can_upload, wait_time = can_user_upload(message.from_user.id)
        if not can_upload:
            limit_message = (
                "⚠️ **Upload Limit Reached**\n\n"
                "Free users can upload 5 files per day.\n"
                f"⏰ Please wait **{wait_time}** before uploading again.\n\n"
                "💎 **Upgrade to Premium** for unlimited uploads!\n"
                "Use /upgrade to learn more.\n\n"
                "📞 Contact Admin: @viizet"
            )
            await message.reply_text(limit_message)
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
            
            # Check if user is premium for status display
            premium_status = "💎 Premium User" if is_premium_user(message.from_user.id) else f"📊 Free User ({get_user_upload_count(message.from_user.id)}/5 uploads today)"
            
            response_text = (
                f"✅ File uploaded successfully!\n\n"
                f"📂 Type: {display_type}{file_size}"
                f"{file_name}\n"
                f"🔗 Share Link:\n{share_link}\n\n"
                f"{premium_status}\n"
                f"💡 Anyone with this link can download your file!\n\n"
                f"📞 Need help? Contact Admin: @viizet"
            )
            
            await message.reply_text(response_text, parse_mode=None)
            logger.info(f"File uploaded by user {message.from_user.id}: {display_type}")
        else:
            await message.reply_text("❌ Failed to save file. Please try again.\n\n📞 Contact Admin: @viizet")

    except Exception as e:
        logger.error(f"Error handling file upload: {e}")
        await message.reply_text("❌ An error occurred while processing your file. Please try again.\n\n📞 Contact Admin: @viizet")

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    """Handle /start command and file retrieval"""
    try:
        # Check if user is banned
        if is_banned(message.from_user.id):
            await message.reply_text("❌ You have been banned from using this bot.\n\n📞 Contact Admin: @viizet")
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
                        # Create inline keyboard for video with JOIN DAAWO button
                        keyboard = InlineKeyboardMarkup([
                            [InlineKeyboardButton("📺 JOIN DAAWO", url="https://t.me/daawotv")]
                        ])
                        await client.send_video(message.chat.id, file_id, caption=original_caption, reply_markup=keyboard)
                    elif file_type == "audio":
                        await client.send_audio(message.chat.id, file_id, caption=original_caption)
                    else:
                        await client.send_document(message.chat.id, file_id, caption=original_caption)
                    
                    logger.info(f"File retrieved by user {message.from_user.id}: {file_key}")
                except Exception as e:
                    logger.error(f"Error sending file {file_key}: {e}")
                    await message.reply_text(
                        "❌ File not accessible\n\n"
                        "This file may have been deleted from Telegram's servers or is no longer available.\n\n"
                        "📞 Contact Admin: @viizet"
                    )
            else:
                await message.reply_text(
                    "❌ File not found\n\n"
                    "The file you're looking for doesn't exist or the link is invalid.\n\n"
                    "📞 Contact Admin: @viizet"
                )
        else:
            welcome_text = (
                "👋 Welcome to File Saver Bot! @DAAWOTV \n\n"
                "📁 How it works:\n"
                "1️⃣ Send me any file (document, video, audio, or photo)\n"
                "2️⃣ Get a unique shareable download link\n"
                "3️⃣ Anyone with the link can download your file\n\n"
                "🆓 **Free Plan**: 5 uploads per day\n"
                "💎 **Premium Plan**: Unlimited uploads\n\n"
                "🔒 Secure & Private\n"
                "• Files are stored using Telegram's infrastructure\n"
                "• No external hosting required\n"
                "• Links work indefinitely\n\n"
                "📤 Send me a file to get started!\n"
                "💎 Use /upgrade to learn about Premium\n"
                "📊 Use /myplan to check your current plan\n\n"
                "📞 Need help? Contact Admin: @viizet"
            )
            await message.reply_text(welcome_text, parse_mode=None)
            logger.info(f"New user started the bot: {message.from_user.id}")

    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await message.reply_text("❌ An error occurred. Please try again.\n\n📞 Contact Admin: @viizet")

@app.on_message(filters.command("premium"))
async def premium_handler(client, message):
    """Handle /premium command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.\n\n📞 Contact Admin: @viizet")
            return

        args = message.text.split()
        if len(args) != 2:
            await message.reply_text("Usage: /premium <user_id>\n\nExample: /premium 123456789")
            return

        try:
            target_user_id = int(args[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a valid numeric user ID.")
            return

        # Get user info from stats
        stats = load_stats()
        user_str = str(target_user_id)
        username = "Unknown"
        if user_str in stats["users"]:
            username = stats["users"][user_str].get("username", "Unknown")

        if add_premium_user(target_user_id, username):
            await message.reply_text(f"✅ User {target_user_id} ({username}) has been upgraded to Premium!")
            logger.info(f"Admin {message.from_user.id} upgraded user {target_user_id} to premium")
        else:
            await message.reply_text("❌ Failed to upgrade user. Please try again.")

    except Exception as e:
        logger.error(f"Error in premium handler: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@app.on_message(filters.command("unpremium"))
async def unpremium_handler(client, message):
    """Handle /unpremium command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.\n\n📞 Contact Admin: @viizet")
            return

        args = message.text.split()
        if len(args) != 2:
            await message.reply_text("Usage: /unpremium <user_id>\n\nExample: /unpremium 123456789")
            return

        try:
            target_user_id = int(args[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a valid numeric user ID.")
            return

        # Get user info from stats
        stats = load_stats()
        user_str = str(target_user_id)
        username = "Unknown"
        if user_str in stats["users"]:
            username = stats["users"][user_str].get("username", "Unknown")

        if remove_premium_user(target_user_id):
            await message.reply_text(f"✅ User {target_user_id} ({username}) has been downgraded to Free plan!")
            logger.info(f"Admin {message.from_user.id} downgraded user {target_user_id} from premium")
        else:
            await message.reply_text("❌ Failed to downgrade user. Please try again.")

    except Exception as e:
        logger.error(f"Error in unpremium handler: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@app.on_message(filters.command("upgrade"))
async def upgrade_handler(client, message):
    """Handle /upgrade command"""
    try:
        # Check if user is banned
        if is_banned(message.from_user.id):
            await message.reply_text("❌ You have been banned from using this bot.\n\n📞 Contact Admin: @viizet")
            return

        upgrade_text = (
            "💎 **Premium Plan Benefits**\n\n"
            "🚀 **What you get with Premium:**\n"
            "• ♾️ Unlimited file uploads\n"
            "• 🚫 No daily limits\n"
            "• ⚡ No waiting periods\n"
            "• 🎯 Priority support\n"
            "• 📊 Advanced statistics\n\n"
            "🆓 **Free Plan:**\n"
            "• 📁 5 uploads per day\n"
            "• ⏰ 4-hour cooldown after limit\n\n"
            "💰 **How to upgrade:**\n"
            "Contact our admin to upgrade to Premium!\n\n"
            "📞 **Contact Admin: @viizet**\n"
            "💬 Send a message to discuss Premium options"
        )
        
        await message.reply_text(upgrade_text)
        logger.info(f"User {message.from_user.id} requested upgrade information")

    except Exception as e:
        logger.error(f"Error in upgrade handler: {e}")
        await message.reply_text("❌ An error occurred. Please try again.\n\n📞 Contact Admin: @viizet")

@app.on_message(filters.command("myplan"))
async def myplan_handler(client, message):
    """Handle /myplan command"""
    try:
        # Check if user is banned
        if is_banned(message.from_user.id):
            await message.reply_text("❌ You have been banned from using this bot.\n\n📞 Contact Admin: @viizet")
            return

        user_id = message.from_user.id
        is_premium = is_premium_user(user_id)
        upload_count = get_user_upload_count(user_id)
        
        if is_premium:
            plan_text = (
                "💎 **Your Current Plan: Premium**\n\n"
                "✅ **Active Benefits:**\n"
                "• ♾️ Unlimited file uploads\n"
                "• 🚫 No daily limits\n"
                "• ⚡ No waiting periods\n"
                "• 🎯 Priority support\n\n"
                "📊 **Today's Activity:**\n"
                f"📁 Files uploaded: {upload_count}\n\n"
                "🎉 Thank you for being a Premium user!\n\n"
                "📞 Need help? Contact Admin: @viizet"
            )
        else:
            remaining_uploads = max(0, 5 - upload_count)
            plan_text = (
                "🆓 **Your Current Plan: Free**\n\n"
                "📊 **Today's Usage:**\n"
                f"📁 Files uploaded: {upload_count}/5\n"
                f"📤 Remaining uploads: {remaining_uploads}\n\n"
                "💎 **Upgrade to Premium for:**\n"
                "• ♾️ Unlimited uploads\n"
                "• 🚫 No daily limits\n"
                "• ⚡ No waiting periods\n\n"
                "🚀 Use /upgrade to learn more!\n\n"
                "📞 Contact Admin: @viizet"
            )
        
        await message.reply_text(plan_text)
        logger.info(f"User {message.from_user.id} checked their plan status")

    except Exception as e:
        logger.error(f"Error in myplan handler: {e}")
        await message.reply_text("❌ An error occurred. Please try again.\n\n📞 Contact Admin: @viizet")

@app.on_message(filters.command("stats"))
async def stats_handler(client, message):
    """Handle /stats command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.\n\n📞 Contact Admin: @viizet")
            return

        stats = load_stats()
        premium_users = load_premium_users()
        
        # Calculate active users (users who interacted in last 30 days)
        active_users = 0
        from datetime import datetime, timedelta
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        
        for user_data in stats["users"].values():
            if user_data["last_seen"] > thirty_days_ago:
                active_users += 1
        
        # Count premium users
        premium_count = sum(1 for user in premium_users.values() if user.get("is_premium", False))
        
        # Get top uploaders
        top_uploaders = sorted(
            [(user_id, data) for user_id, data in stats["users"].items()],
            key=lambda x: x[1]["files_uploaded"],
            reverse=True
        )[:5]
        
        top_uploaders_text = ""
        for i, (user_id, data) in enumerate(top_uploaders, 1):
            username = data.get("username", "Unknown")
            files = data["files_uploaded"]
            premium_badge = "💎" if is_premium_user(int(user_id)) else "🆓"
            top_uploaders_text += f"{i}. {premium_badge} {username} - {files} files\n"
        
        stats_text = (
            f"📊 **Bot Statistics**\n\n"
            f"👥 **Users:**\n"
            f"• Total: {stats['total_users']}\n"
            f"• Active (30d): {active_users}\n"
            f"• Premium: {premium_count}\n"
            f"• Free: {stats['total_users'] - premium_count}\n\n"
            f"📁 **Files:**\n"
            f"• Total: {stats['total_files']}\n"
            f"• Documents: {stats['files_by_type']['document']}\n"
            f"• Videos: {stats['files_by_type']['video']}\n"
            f"• Audio: {stats['files_by_type']['audio']}\n"
            f"• Photos: {stats['files_by_type']['photo']}\n\n"
            f"📥 **Downloads:** {stats['downloads']}\n\n"
            f"🏆 **Top Uploaders:**\n{top_uploaders_text}\n"
            f"📞 Admin Contact: @viizet"
        )
        
        await message.reply_text(stats_text)
        logger.info(f"Admin {message.from_user.id} viewed bot statistics")

    except Exception as e:
        logger.error(f"Error in stats handler: {e}")
        await message.reply_text("❌ An error occurred while fetching statistics.\n\n📞 Contact Admin: @viizet")

@app.on_message(filters.command("users"))
async def users_handler(client, message):
    """Handle /users command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.\n\n📞 Contact Admin: @viizet")
            return

        stats = load_stats()
        users_list = []
        
        for user_id, data in stats["users"].items():
            username = data.get("username", "Unknown")
            files = data["files_uploaded"]
            downloads = data["downloads"]
            last_seen = data["last_seen"][:10]  # Get date only
            premium_badge = "💎" if is_premium_user(int(user_id)) else "🆓"
            
            users_list.append(f"{premium_badge} {username} (ID: {user_id})\n"
                            f"   📁 {files} files | 📥 {downloads} downloads | 🕒 {last_seen}")
        
        if not users_list:
            await message.reply_text("No users found in the database.")
            return
        
        # Split into chunks if too long
        users_text = "\n\n".join(users_list)
        if len(users_text) > 4000:
            # Send in chunks
            chunks = [users_list[i:i+10] for i in range(0, len(users_list), 10)]
            for i, chunk in enumerate(chunks, 1):
                chunk_text = f"👥 **User List ({i}/{len(chunks)})**\n\n" + "\n\n".join(chunk)
                await message.reply_text(chunk_text)
        else:
            full_text = f"👥 **User List**\n\n{users_text}\n\n📞 Admin Contact: @viizet"
            await message.reply_text(full_text)

    except Exception as e:
        logger.error(f"Error in users handler: {e}")
        await message.reply_text("❌ An error occurred while fetching user list.\n\n📞 Contact Admin: @viizet")

@app.on_message(filters.command("ban"))
async def ban_handler(client, message):
    """Handle /ban command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.\n\n📞 Contact Admin: @viizet")
            return

        args = message.text.split()
        if len(args) != 2:
            await message.reply_text("Usage: /ban <user_id>\n\nExample: /ban 123456789")
            return

        try:
            target_user_id = int(args[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a valid numeric user ID.")
            return

        if target_user_id == ADMIN_USER_ID:
            await message.reply_text("❌ Cannot ban the admin user.")
            return

        if ban_user(target_user_id):
            await message.reply_text(f"✅ User {target_user_id} has been banned successfully.")
            logger.info(f"Admin {message.from_user.id} banned user {target_user_id}")
        else:
            await message.reply_text("❌ Failed to ban user. Please try again.")

    except Exception as e:
        logger.error(f"Error in ban handler: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@app.on_message(filters.command("unban"))
async def unban_handler(client, message):
    """Handle /unban command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.\n\n📞 Contact Admin: @viizet")
            return

        args = message.text.split()
        if len(args) != 2:
            await message.reply_text("Usage: /unban <user_id>\n\nExample: /unban 123456789")
            return

        try:
            target_user_id = int(args[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a valid numeric user ID.")
            return

        if unban_user(target_user_id):
            await message.reply_text(f"✅ User {target_user_id} has been unbanned successfully.")
            logger.info(f"Admin {message.from_user.id} unbanned user {target_user_id}")
        else:
            await message.reply_text("❌ Failed to unban user. Please try again.")

    except Exception as e:
        logger.error(f"Error in unban handler: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@app.on_message(filters.command("banned"))
async def banned_handler(client, message):
    """Handle /banned command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.\n\n📞 Contact Admin: @viizet")
            return

        banned_users = load_banned_users()
        
        if not banned_users:
            await message.reply_text("✅ No banned users found.")
            return

        banned_text = "🚫 **Banned Users:**\n\n"
        for user_id in banned_users:
            banned_text += f"• {user_id}\n"
        
        banned_text += f"\n📊 Total banned users: {len(banned_users)}\n📞 Admin Contact: @viizet"
        await message.reply_text(banned_text)

    except Exception as e:
        logger.error(f"Error in banned handler: {e}")
        await message.reply_text("❌ An error occurred while fetching banned users list.\n\n📞 Contact Admin: @viizet")

@app.on_message(filters.command("broadcast"))
async def broadcast_handler(client, message):
    """Handle /broadcast command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.\n\n📞 Contact Admin: @viizet")
            return

        # Extract message text
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply_text("Usage: /broadcast <message>\n\nExample: /broadcast Hello everyone!")
            return

        broadcast_message = command_parts[1]
        
        # Load users
        stats = load_stats()
        banned_users = load_banned_users()
        
        if not stats["users"]:
            await message.reply_text("No users found to broadcast to.")
            return

        # Filter out banned users
        active_users = [user_id for user_id in stats["users"].keys() if int(user_id) not in banned_users]
        
        if not active_users:
            await message.reply_text("No active users found to broadcast to.")
            return

        # Start broadcast
        progress_msg = await message.reply_text(f"📡 Starting broadcast to {len(active_users)} users...")
        
        success_count = 0
        failed_count = 0
        
        for i, user_id in enumerate(active_users):
            try:
                await app.send_message(int(user_id), broadcast_message)
                success_count += 1
                
                # Update progress every 50 messages
                if (i + 1) % 50 == 0:
                    await progress_msg.edit_text(
                        f"📡 Broadcasting... {i + 1}/{len(active_users)}\n"
                        f"✅ Sent: {success_count}\n"
                        f"❌ Failed: {failed_count}"
                    )
                
                # Rate limiting - 30 messages per second
                await asyncio.sleep(1/30)
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send broadcast to {user_id}: {e}")

        # Final report
        await progress_msg.edit_text(
            f"✅ **Broadcast Complete!**\n\n"
            f"📊 **Results:**\n"
            f"• Total users: {len(active_users)}\n"
            f"• Successfully sent: {success_count}\n"
            f"• Failed: {failed_count}\n"
            f"• Success rate: {(success_count/len(active_users)*100):.1f}%\n\n"
            f"📞 Admin Contact: @viizet"
        )
        
        logger.info(f"Broadcast completed by admin {message.from_user.id}: {success_count}/{len(active_users)} successful")

    except Exception as e:
        logger.error(f"Error in broadcast handler: {e}")
        await message.reply_text("❌ An error occurred during broadcast.\n\n📞 Contact Admin: @viizet")

if __name__ == "__main__":
    # Import and start keep-alive server if available
    try:
        from keep_alive import keep_alive
        keep_alive()
    except ImportError:
        logger.info("Keep-alive server not available, running bot only")
    
    logger.info("Starting Telegram File Saver Bot with Premium Features...")
    app.run()

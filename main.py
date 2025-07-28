from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
import uuid
import logging
import asyncio
import time
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get credentials from environment variables
API_ID = int(os.getenv("API_ID", "26176218"))
API_HASH = os.getenv("API_HASH", "4a50bc8acb0169930f5914eb88091736")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8452579938:AAGeNe_GEes9iiCDRz99bk94ubkbTbbzm7M")

# Admin user ID (replace with your Telegram user ID)
ADMIN_USER_ID = 1096693642  # Replace with your actual Telegram user ID

# Premium admin user IDs (users who can become admins)
PREMIUM_ADMIN_IDS = set()  # Will be populated from premium users

# Free user upload limit
FREE_USER_UPLOAD_LIMIT = 10

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
            "premium_users": 0,
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
            stats = json.load(f)
            # Ensure backward compatibility with new premium fields
            if "premium_users" not in stats:
                stats["premium_users"] = 0
            # Update existing users with premium status if not present
            for user_id, user_data in stats["users"].items():
                if "is_premium" not in user_data:
                    user_data["is_premium"] = False
                if "upload_count" not in user_data:
                    user_data["upload_count"] = user_data.get("files_uploaded", 0)
            return stats
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading stats.json: {e}")
        return {
            "total_users": 0,
            "total_files": 0,
            "files_by_type": {"document": 0, "video": 0, "audio": 0, "photo": 0},
            "downloads": 0,
            "premium_users": 0,
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
                "upload_count": 0,
                "downloads": 0,
                "is_premium": False,
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
            stats["users"][user_str]["upload_count"] += 1
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
    """Check if user is admin (main admin or premium admin)"""
    return user_id == ADMIN_USER_ID or user_id in PREMIUM_ADMIN_IDS

def is_main_admin(user_id):
    """Check if user is the main admin"""
    return user_id == ADMIN_USER_ID

def is_premium_user(user_id):
    """Check if user is premium"""
    try:
        stats = load_stats()
        user_str = str(user_id)
        return stats["users"].get(user_str, {}).get("is_premium", False)
    except Exception as e:
        logger.error(f"Error checking premium status: {e}")
        return False

def set_premium_status(user_id, username, is_premium):
    """Set premium status for a user"""
    try:
        stats = load_stats()
        user_str = str(user_id)
        
        # Initialize user if not exists
        if user_str not in stats["users"]:
            stats["users"][user_str] = {
                "username": username,
                "files_uploaded": 0,
                "upload_count": 0,
                "downloads": 0,
                "is_premium": False,
                "first_seen": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat()
            }
            stats["total_users"] += 1
        
        # Update premium status
        old_status = stats["users"][user_str].get("is_premium", False)
        stats["users"][user_str]["is_premium"] = is_premium
        stats["users"][user_str]["username"] = username
        stats["users"][user_str]["last_seen"] = datetime.utcnow().isoformat()
        
        # Update premium user count
        if is_premium and not old_status:
            stats["premium_users"] += 1
            # Add to premium admin IDs if premium
            PREMIUM_ADMIN_IDS.add(user_id)
        elif not is_premium and old_status:
            stats["premium_users"] -= 1
            # Remove from premium admin IDs if downgraded
            PREMIUM_ADMIN_IDS.discard(user_id)
        
        # Save updated stats
        with open("stats.json", "w") as f:
            json.dump(stats, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error setting premium status: {e}")
        return False

def get_user_upload_count(user_id):
    """Get user's current upload count"""
    try:
        stats = load_stats()
        user_str = str(user_id)
        return stats["users"].get(user_str, {}).get("upload_count", 0)
    except Exception as e:
        logger.error(f"Error getting upload count: {e}")
        return 0

def can_upload(user_id):
    """Check if user can upload more files"""
    if is_premium_user(user_id):
        return True  # Premium users have unlimited uploads
    
    current_uploads = get_user_upload_count(user_id)
    return current_uploads < FREE_USER_UPLOAD_LIMIT

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

def load_premium_admins():
    """Load premium users who can be admins into the PREMIUM_ADMIN_IDS set"""
    try:
        stats = load_stats()
        for user_id, user_data in stats["users"].items():
            if user_data.get("is_premium", False):
                PREMIUM_ADMIN_IDS.add(int(user_id))
        logger.info(f"Loaded {len(PREMIUM_ADMIN_IDS)} premium admin users")
    except Exception as e:
        logger.error(f"Error loading premium admins: {e}")

@app.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def file_handler(client, message):
    """Handle incoming file uploads"""
    try:
        # Check if user is banned
        if is_banned(message.from_user.id):
            await message.reply_text("❌ You have been banned from using this bot.")
            logger.info(f"Banned user {message.from_user.id} tried to upload file")
            return

        # Check upload limit for free users
        if not can_upload(message.from_user.id):
            current_uploads = get_user_upload_count(message.from_user.id)
            await message.reply_text(
                f"❌ **Upload Limit Reached**\n\n"
                f"You have reached the free user limit of {FREE_USER_UPLOAD_LIMIT} uploads.\n"
                f"Current uploads: {current_uploads}/{FREE_USER_UPLOAD_LIMIT}\n\n"
                f"💎 Upgrade to premium for unlimited uploads!\n"
                f"Contact an admin for premium access."
            )
            logger.info(f"User {message.from_user.id} reached upload limit ({current_uploads}/{FREE_USER_UPLOAD_LIMIT})")
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
            
            # Show premium status and remaining uploads for free users
            premium_status = "💎 Premium" if is_premium_user(message.from_user.id) else "🆓 Free"
            upload_info = ""
            if not is_premium_user(message.from_user.id):
                current_uploads = get_user_upload_count(message.from_user.id)
                remaining = FREE_USER_UPLOAD_LIMIT - current_uploads
                upload_info = f"\n📊 Uploads: {current_uploads}/{FREE_USER_UPLOAD_LIMIT} (Remaining: {remaining})"
            
            response_text = (
                f"✅ File uploaded successfully!\n\n"
                f"📂 Type: {display_type}{file_size}"
                f"{file_name}\n"
                f"👤 Status: {premium_status}{upload_info}\n"
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
                    # Create keyboard with JOIN DAAWO button for videos
                    keyboard = None
                    if file_type == "video":
                        keyboard = InlineKeyboardMarkup([
                            [InlineKeyboardButton("📺 JOIN DAAWO", url="https://t.me/daawotv")]
                        ])
                    
                    if file_type == "photo":
                        await client.send_photo(message.chat.id, file_id, caption=original_caption, reply_markup=keyboard)
                    elif file_type == "video":
                        await client.send_video(message.chat.id, file_id, caption=original_caption, reply_markup=keyboard)
                    elif file_type == "audio":
                        await client.send_audio(message.chat.id, file_id, caption=original_caption, reply_markup=keyboard)
                    else:
                        await client.send_document(message.chat.id, file_id, caption=original_caption, reply_markup=keyboard)
                    
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
            # Check user status for welcome message
            premium_status = "💎 Premium User" if is_premium_user(message.from_user.id) else "🆓 Free User"
            upload_info = ""
            if not is_premium_user(message.from_user.id):
                current_uploads = get_user_upload_count(message.from_user.id)
                remaining = FREE_USER_UPLOAD_LIMIT - current_uploads
                upload_info = f"\n📊 Your uploads: {current_uploads}/{FREE_USER_UPLOAD_LIMIT} (Remaining: {remaining})"
            
            welcome_text = (
                f"👋 Welcome to File Saver Bot! @DAAWOTV\n\n"
                f"👤 Status: {premium_status}{upload_info}\n\n"
                f"📁 How it works:\n"
                f"1️⃣ Send me any file (document, video, audio, or photo)\n"
                f"2️⃣ Get a unique shareable download link\n"
                f"3️⃣ Anyone with the link can download your file\n\n"
                f"🔒 Secure & Private\n"
                f"• Files are stored using Telegram's infrastructure\n"
                f"• No external hosting required\n"
                f"• Links work indefinitely\n\n"
                f"💎 Premium Features:\n"
                f"• Unlimited file uploads\n"
                f"• Admin privileges (premium only)\n"
                f"• Priority support\n\n"
                f"📤 Send me a file to get started!"
            )
            await message.reply_text(welcome_text, parse_mode=None)
            logger.info(f"New user started the bot: {message.from_user.id}")

    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@app.on_message(filters.command("premium"))
async def premium_handler(client, message):
    """Handle /premium command - Main admin only"""
    try:
        if not is_main_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for the main administrator only.")
            return

        args = message.text.split()
        if len(args) != 2:
            await message.reply_text(
                "❌ **Invalid usage**\n\n"
                "**Usage:** `/premium <user_id>`\n"
                "**Example:** `/premium 123456789`\n\n"
                "This will upgrade the specified user to premium status."
            )
            return

        try:
            target_user_id = int(args[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a valid numeric user ID.")
            return

        # Get user info
        stats = load_stats()
        user_str = str(target_user_id)
        
        if user_str not in stats["users"]:
            await message.reply_text(f"❌ User {target_user_id} not found in database. They need to interact with the bot first.")
            return

        user_data = stats["users"][user_str]
        username = user_data.get("username", "Unknown")
        
        if user_data.get("is_premium", False):
            await message.reply_text(f"ℹ️ User @{username} ({target_user_id}) is already premium.")
            return

        # Set premium status
        if set_premium_status(target_user_id, username, True):
            await message.reply_text(
                f"✅ **Premium Upgrade Successful**\n\n"
                f"👤 User: @{username} ({target_user_id})\n"
                f"💎 Status: Upgraded to Premium\n"
                f"🔧 Admin Access: Granted\n\n"
                f"The user now has unlimited uploads and admin privileges."
            )
            logger.info(f"User {target_user_id} upgraded to premium by admin {message.from_user.id}")
            
            # Notify the user if possible
            try:
                await client.send_message(
                    target_user_id,
                    f"🎉 **Congratulations!**\n\n"
                    f"You have been upgraded to **Premium User**!\n\n"
                    f"💎 Premium Benefits:\n"
                    f"• Unlimited file uploads\n"
                    f"• Admin privileges\n"
                    f"• Priority support\n\n"
                    f"Thank you for using our bot! @DAAWOTV"
                )
            except Exception as e:
                logger.warning(f"Could not notify user {target_user_id} about premium upgrade: {e}")
        else:
            await message.reply_text("❌ Failed to upgrade user to premium. Please try again.")

    except Exception as e:
        logger.error(f"Error in premium handler: {e}")
        await message.reply_text("❌ An error occurred while processing the premium upgrade.")

@app.on_message(filters.command("unpremium"))
async def unpremium_handler(client, message):
    """Handle /unpremium command - Main admin only"""
    try:
        if not is_main_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for the main administrator only.")
            return

        args = message.text.split()
        if len(args) != 2:
            await message.reply_text(
                "❌ **Invalid usage**\n\n"
                "**Usage:** `/unpremium <user_id>`\n"
                "**Example:** `/unpremium 123456789`\n\n"
                "This will downgrade the specified user from premium status."
            )
            return

        try:
            target_user_id = int(args[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a valid numeric user ID.")
            return

        # Get user info
        stats = load_stats()
        user_str = str(target_user_id)
        
        if user_str not in stats["users"]:
            await message.reply_text(f"❌ User {target_user_id} not found in database.")
            return

        user_data = stats["users"][user_str]
        username = user_data.get("username", "Unknown")
        
        if not user_data.get("is_premium", False):
            await message.reply_text(f"ℹ️ User @{username} ({target_user_id}) is already a free user.")
            return

        # Remove premium status
        if set_premium_status(target_user_id, username, False):
            await message.reply_text(
                f"✅ **Premium Downgrade Successful**\n\n"
                f"👤 User: @{username} ({target_user_id})\n"
                f"🆓 Status: Downgraded to Free User\n"
                f"🔧 Admin Access: Removed\n\n"
                f"The user now has limited uploads ({FREE_USER_UPLOAD_LIMIT} files) and no admin privileges."
            )
            logger.info(f"User {target_user_id} downgraded from premium by admin {message.from_user.id}")
            
            # Notify the user if possible
            try:
                await client.send_message(
                    target_user_id,
                    f"📢 **Account Status Update**\n\n"
                    f"Your account has been changed to **Free User**.\n\n"
                    f"🆓 Free User Limits:\n"
                    f"• {FREE_USER_UPLOAD_LIMIT} file uploads maximum\n"
                    f"• No admin privileges\n\n"
                    f"Contact an admin if you believe this was done in error."
                )
            except Exception as e:
                logger.warning(f"Could not notify user {target_user_id} about premium downgrade: {e}")
        else:
            await message.reply_text("❌ Failed to downgrade user from premium. Please try again.")

    except Exception as e:
        logger.error(f"Error in unpremium handler: {e}")
        await message.reply_text("❌ An error occurred while processing the premium downgrade.")

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
        
        # Get premium and free user counts
        premium_count = stats.get("premium_users", 0)
        free_count = stats["total_users"] - premium_count
        
        # Get top uploaders
        top_uploaders = sorted(
            [(uid, data) for uid, data in stats["users"].items()],
            key=lambda x: x[1]["files_uploaded"],
            reverse=True
        )[:5]
        
        top_uploaders_text = ""
        for i, (uid, data) in enumerate(top_uploaders, 1):
            status_icon = "💎" if data.get("is_premium", False) else "🆓"
            top_uploaders_text += f"{i}. {status_icon} @{data['username']} - {data['files_uploaded']} files\n"
        
        stats_text = (
            f"📊 **Bot Statistics**\n\n"
            f"👥 **Users:**\n"
            f"• Total: {stats['total_users']}\n"
            f"• Active (30 days): {active_users}\n"
            f"• 💎 Premium: {premium_count}\n"
            f"• 🆓 Free: {free_count}\n\n"
            f"📁 **Files:**\n"
            f"• Total uploaded: {stats['total_files']}\n"
            f"• Total downloads: {stats['downloads']}\n\n"
            f"📂 **By Type:**\n"
            f"• 📄 Documents: {stats['files_by_type']['document']}\n"
            f"• 🎥 Videos: {stats['files_by_type']['video']}\n"
            f"• 🎵 Audio: {stats['files_by_type']['audio']}\n"
            f"• 🖼️ Photos: {stats['files_by_type']['photo']}\n\n"
            f"🏆 **Top Uploaders:**\n{top_uploaders_text}\n"
            f"📅 **Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )
        
        await message.reply_text(stats_text)
        logger.info(f"Statistics requested by admin {message.from_user.id}")

    except Exception as e:
        logger.error(f"Error in stats handler: {e}")
        await message.reply_text("❌ An error occurred while generating statistics.")

@app.on_message(filters.command("users"))
async def users_handler(client, message):
    """Handle /users command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.")
            return

        args = message.text.split()
        page = 1
        if len(args) == 2:
            try:
                page = int(args[1])
            except ValueError:
                page = 1

        stats = load_stats()
        users = list(stats["users"].items())
        
        if not users:
            await message.reply_text("📭 No users found in the database.")
            return

        # Sort by last seen (most recent first)
        users.sort(key=lambda x: x[1]["last_seen"], reverse=True)
        
        # Pagination
        per_page = 10
        total_pages = (len(users) + per_page - 1) // per_page
        page = max(1, min(page, total_pages))
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_users = users[start_idx:end_idx]
        
        users_text = f"👥 **User List (Page {page}/{total_pages})**\n\n"
        
        for i, (user_id, user_data) in enumerate(page_users, start_idx + 1):
            username = user_data.get("username", "Unknown")
            files_uploaded = user_data.get("files_uploaded", 0)
            downloads = user_data.get("downloads", 0)
            is_premium = user_data.get("is_premium", False)
            status_icon = "💎" if is_premium else "🆓"
            
            # Format last seen
            try:
                last_seen = datetime.fromisoformat(user_data["last_seen"])
                last_seen_str = last_seen.strftime("%Y-%m-%d")
            except:
                last_seen_str = "Unknown"
            
            users_text += (
                f"{i}. {status_icon} @{username}\n"
                f"   ID: `{user_id}`\n"
                f"   📤 Uploads: {files_uploaded} | 📥 Downloads: {downloads}\n"
                f"   👀 Last seen: {last_seen_str}\n\n"
            )
        
        if total_pages > 1:
            users_text += f"📄 Use `/users <page>` to view other pages (1-{total_pages})"
        
        await message.reply_text(users_text)
        logger.info(f"User list requested by admin {message.from_user.id}, page {page}")

    except Exception as e:
        logger.error(f"Error in users handler: {e}")
        await message.reply_text("❌ An error occurred while fetching user list.")

@app.on_message(filters.command("ban"))
async def ban_handler(client, message):
    """Handle /ban command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.")
            return

        args = message.text.split()
        if len(args) != 2:
            await message.reply_text(
                "❌ **Invalid usage**\n\n"
                "**Usage:** `/ban <user_id>`\n"
                "**Example:** `/ban 123456789`"
            )
            return

        try:
            target_user_id = int(args[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a valid numeric user ID.")
            return

        # Prevent banning main admin
        if target_user_id == ADMIN_USER_ID:
            await message.reply_text("❌ Cannot ban the main administrator.")
            return

        # Get user info
        stats = load_stats()
        user_str = str(target_user_id)
        username = "Unknown"
        if user_str in stats["users"]:
            username = stats["users"][user_str].get("username", "Unknown")

        if ban_user(target_user_id):
            await message.reply_text(
                f"✅ **User Banned Successfully**\n\n"
                f"👤 User: @{username} ({target_user_id})\n"
                f"🚫 Status: Banned from using the bot\n\n"
                f"The user can no longer upload or download files."
            )
            logger.info(f"User {target_user_id} banned by admin {message.from_user.id}")
        else:
            await message.reply_text("❌ Failed to ban user. Please try again.")

    except Exception as e:
        logger.error(f"Error in ban handler: {e}")
        await message.reply_text("❌ An error occurred while banning the user.")

@app.on_message(filters.command("unban"))
async def unban_handler(client, message):
    """Handle /unban command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.")
            return

        args = message.text.split()
        if len(args) != 2:
            await message.reply_text(
                "❌ **Invalid usage**\n\n"
                "**Usage:** `/unban <user_id>`\n"
                "**Example:** `/unban 123456789`"
            )
            return

        try:
            target_user_id = int(args[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a valid numeric user ID.")
            return

        # Get user info
        stats = load_stats()
        user_str = str(target_user_id)
        username = "Unknown"
        if user_str in stats["users"]:
            username = stats["users"][user_str].get("username", "Unknown")

        if unban_user(target_user_id):
            await message.reply_text(
                f"✅ **User Unbanned Successfully**\n\n"
                f"👤 User: @{username} ({target_user_id})\n"
                f"✅ Status: Can now use the bot again\n\n"
                f"The user can now upload and download files."
            )
            logger.info(f"User {target_user_id} unbanned by admin {message.from_user.id}")
        else:
            await message.reply_text("❌ Failed to unban user. Please try again.")

    except Exception as e:
        logger.error(f"Error in unban handler: {e}")
        await message.reply_text("❌ An error occurred while unbanning the user.")

@app.on_message(filters.command("banned"))
async def banned_handler(client, message):
    """Handle /banned command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.")
            return

        banned_users = load_banned_users()
        
        if not banned_users:
            await message.reply_text("📭 No banned users found.")
            return

        # Get user info from stats
        stats = load_stats()
        
        banned_text = f"🚫 **Banned Users ({len(banned_users)})**\n\n"
        
        for i, user_id in enumerate(banned_users, 1):
            user_str = str(user_id)
            username = "Unknown"
            if user_str in stats["users"]:
                username = stats["users"][user_str].get("username", "Unknown")
            
            banned_text += f"{i}. @{username} (`{user_id}`)\n"
        
        banned_text += f"\n💡 Use `/unban <user_id>` to unban a user"
        
        await message.reply_text(banned_text)
        logger.info(f"Banned users list requested by admin {message.from_user.id}")

    except Exception as e:
        logger.error(f"Error in banned handler: {e}")
        await message.reply_text("❌ An error occurred while fetching banned users list.")

@app.on_message(filters.command("broadcast"))
async def broadcast_handler(client, message):
    """Handle /broadcast command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.")
            return

        # Get the broadcast message
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply_text(
                "❌ **Invalid usage**\n\n"
                "**Usage:** `/broadcast <message>`\n"
                "**Example:** `/broadcast Hello everyone! This is a test message.`"
            )
            return

        broadcast_message = args[1]
        
        # Get all users
        stats = load_stats()
        all_users = list(stats["users"].keys())
        banned_users = load_banned_users()
        
        # Filter out banned users
        target_users = [int(uid) for uid in all_users if int(uid) not in banned_users]
        
        if not target_users:
            await message.reply_text("📭 No users available for broadcast.")
            return

        # Start broadcast
        await message.reply_text(
            f"📢 **Starting Broadcast**\n\n"
            f"👥 Target users: {len(target_users)}\n"
            f"⏳ Estimated time: {len(target_users) // 30 + 1} seconds\n\n"
            f"Broadcasting message..."
        )

        success_count = 0
        failed_count = 0
        blocked_count = 0
        
        # Send messages with rate limiting
        for i, user_id in enumerate(target_users):
            try:
                await client.send_message(user_id, f"📢 **Broadcast Message**\n\n{broadcast_message}")
                success_count += 1
                
                # Rate limiting: 30 messages per second
                if (i + 1) % 30 == 0:
                    await asyncio.sleep(1)
                    
                # Progress update every 50 messages
                if (i + 1) % 50 == 0:
                    progress = (i + 1) / len(target_users) * 100
                    await message.reply_text(
                        f"📈 **Broadcast Progress**\n\n"
                        f"✅ Sent: {success_count}\n"
                        f"❌ Failed: {failed_count}\n"
                        f"🚫 Blocked: {blocked_count}\n"
                        f"📊 Progress: {progress:.1f}%"
                    )
                    
            except Exception as e:
                if "blocked" in str(e).lower() or "user not found" in str(e).lower():
                    blocked_count += 1
                else:
                    failed_count += 1
                logger.warning(f"Failed to send broadcast to user {user_id}: {e}")

        # Final report
        total_attempted = len(target_users)
        success_rate = (success_count / total_attempted * 100) if total_attempted > 0 else 0
        
        final_report = (
            f"📊 **Broadcast Completed**\n\n"
            f"📈 **Results:**\n"
            f"✅ Successfully sent: {success_count}\n"
            f"❌ Failed to send: {failed_count}\n"
            f"🚫 User blocked bot: {blocked_count}\n"
            f"📊 Success rate: {success_rate:.1f}%\n\n"
            f"👥 Total users targeted: {total_attempted}\n"
            f"⏰ Completed at: {datetime.utcnow().strftime('%H:%M:%S')} UTC"
        )
        
        await message.reply_text(final_report)
        logger.info(f"Broadcast completed by admin {message.from_user.id}: {success_count}/{total_attempted} successful")

    except Exception as e:
        logger.error(f"Error in broadcast handler: {e}")
        await message.reply_text("❌ An error occurred during broadcast.")

if __name__ == "__main__":
    # Import and start keep_alive server
    try:
        from keep_alive import keep_alive
        keep_alive()
    except ImportError:
        logger.warning("keep_alive.py not found, running without web server")
    
    # Load premium admins on startup
    load_premium_admins()
    
    # Start the bot
    logger.info("Starting Telegram File Saver Bot...")
    app.run()

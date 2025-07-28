from pyrogram import filters, types
from pyrogram.client import Client
import json
import os
import uuid
import logging
import asyncio
import time
from datetime import datetime
from keep_alive import keep_alive

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get credentials from environment variables
API_ID = int(os.getenv("API_ID", "26176218"))
API_HASH = os.getenv("API_HASH", "4a50bc8acb0169930f5914eb88091736")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8452579938:AAGeNe_GEes9iiCDRz99bk94ubkbTbbzm7M")

# Admin user ID (replace with your Telegram user ID)
ADMIN_USER_ID = 1096693642  # Replace with your actual Telegram user ID

# Free user upload limit
FREE_USER_LIMIT = 10

# Initialize the Pyrogram client
app = Client("file_saver_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

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
        json.dump([], f)
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
    """Load premium users list"""
    try:
        with open("premium_users.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading premium_users.json: {e}")
        return []

def save_premium_users(premium_list):
    """Save premium users list"""
    try:
        with open("premium_users.json", "w") as f:
            json.dump(premium_list, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving premium_users.json: {e}")
        return False

def is_premium_user(user_id):
    """Check if user has premium access"""
    premium_users = load_premium_users()
    return user_id in premium_users

def add_premium_user(user_id):
    """Add user to premium list"""
    premium_users = load_premium_users()
    if user_id not in premium_users:
        premium_users.append(user_id)
        return save_premium_users(premium_users)
    return True

def remove_premium_user(user_id):
    """Remove user from premium list"""
    premium_users = load_premium_users()
    if user_id in premium_users:
        premium_users.remove(user_id)
        return save_premium_users(premium_users)
    return True

def get_user_upload_count(user_id):
    """Get user's upload count"""
    stats = load_stats()
    user_str = str(user_id)
    if user_str in stats["users"]:
        return stats["users"][user_str]["files_uploaded"]
    return 0

def can_user_upload(user_id):
    """Check if user can upload files (premium or within free limit)"""
    if is_premium_user(user_id):
        return True, "Premium user - unlimited uploads"
    
    upload_count = get_user_upload_count(user_id)
    remaining = FREE_USER_LIMIT - upload_count
    
    if remaining > 0:
        return True, f"Free user - {remaining} uploads remaining"
    else:
        return False, "Upload limit reached. Contact admin for premium access."

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
        
        # Check if user can upload
        can_upload, upload_status = can_user_upload(message.from_user.id)
        if not can_upload:
            await message.reply_text(
                f"❌ {upload_status}\n\n"
                f"🎯 Free users are limited to {FREE_USER_LIMIT} file uploads.\n"
                f"💎 Upgrade to premium for unlimited uploads!\n\n"
                f"📞 Contact admin for premium access."
            )
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
            
            # Check remaining uploads for free users
            remaining_info = ""
            if not is_premium_user(message.from_user.id):
                remaining = FREE_USER_LIMIT - get_user_upload_count(message.from_user.id)
                remaining_info = f"\n\n📊 Uploads remaining: {remaining}/{FREE_USER_LIMIT}"
            else:
                remaining_info = "\n\n💎 Premium user - Unlimited uploads"
            
            response_text = (
                f"✅ File uploaded successfully!\n\n"
                f"📂 Type: {display_type}{file_size}"
                f"{file_name}\n"
                f"🔗 Share Link:\n{share_link}\n\n"
                f"💡 Anyone with this link can download your file!"
                f"{remaining_info}"
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
                    # Create Join Daawotv button
                    join_button = types.InlineKeyboardMarkup([
                        [types.InlineKeyboardButton("Join Daawotv", url="https://t.me/daawotv")]
                    ])
                    
                    if file_type == "photo":
                        await client.send_photo(
                            message.chat.id, 
                            file_id, 
                            caption=original_caption,
                            reply_markup=join_button
                        )
                    elif file_type == "video":
                        await client.send_video(
                            message.chat.id, 
                            file_id, 
                            caption=original_caption,
                            reply_markup=join_button
                        )
                    elif file_type == "audio":
                        await client.send_audio(
                            message.chat.id, 
                            file_id, 
                            caption=original_caption,
                            reply_markup=join_button
                        )
                    else:
                        await client.send_document(
                            message.chat.id, 
                            file_id, 
                            caption=original_caption,
                            reply_markup=join_button
                        )
                    
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
                "👋 Welcome to Video to link Bot! @DAAWOTV \n\n"
                "📁 How it works:\n"
                "1️⃣ Send me any file (document, video, audio, or photo)\n"
                "2️⃣ Get a unique shareable download link\n"
                "3️⃣ Anyone with the link can download your file\n\n"
                "🔒 Secure & Private\n"
                "• Files are stored using Telegram's infrastructure\n"
                "• No external hosting required\n"
                "• Links work indefinitely\n\n"
                "💎 Premium Features:\n"
                "• Free users: 10 file uploads maximum\n"
                "• Premium users: Unlimited uploads\n\n"
                "📤 Send me a file to get started!\n"
                "❓ Use /help for more commands"
            )
            
            # Add upgrade button for new users
            if not is_premium_user(message.from_user.id) and not is_admin(message.from_user.id):
                upgrade_button = types.InlineKeyboardMarkup([
                    [types.InlineKeyboardButton("💎 Upgrade to Premium", callback_data=f"upgrade_{message.from_user.id}")],
                    [types.InlineKeyboardButton("📞 Join Channel", url="https://t.me/daawotv")]
                ])
                await message.reply_text(welcome_text, parse_mode=None, reply_markup=upgrade_button)
            else:
                await message.reply_text(welcome_text, parse_mode=None)
            logger.info(f"New user started the bot: {message.from_user.id}")
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@app.on_message(filters.command("help"))
async def help_handler(client, message):
    """Handle /help command"""
    try:
        user_id = message.from_user.id
        is_user_premium = is_premium_user(user_id)
        is_user_admin = is_admin(user_id)
        
        help_text = (
            "📋 **Available Commands**\n\n"
            "🔹 **For All Users:**\n"
            "• Send any file - Get a shareable download link\n"
            "• /start - Welcome message and bot info\n"
            "• /help - Show this help message\n\n"
        )
        
        if is_user_premium:
            help_text += (
                "💎 **Premium Status:** Active\n"
                "• Unlimited file uploads\n"
                "• Priority support\n\n"
            )
        else:
            upload_count = get_user_upload_count(user_id)
            remaining = FREE_USER_LIMIT - upload_count
            help_text += (
                f"🆓 **Free User Status:**\n"
                f"• Uploads used: {upload_count}/{FREE_USER_LIMIT}\n"
                f"• Uploads remaining: {remaining}\n"
                f"• Contact admin for premium upgrade\n\n"
                f"💎 **Premium Plan:**\n"
                f"• Unlimited file uploads\n"
                f"• No size restrictions\n"
                f"• Priority support\n"
                f"• Permanent file storage\n\n"
            )
        
        if is_user_admin:
            help_text += (
                "👑 **Admin Commands:**\n"
                "• /stats - View bot statistics\n"
                "• /users - View user list\n"
                "• /ban <user_id> - Ban a user\n"
                "• /unban <user_id> - Unban a user\n"
                "• /banned - View banned users\n"
                "• /premium <user_id> - Grant premium access\n"
                "• /unpremium <user_id> - Remove premium access\n"
                "• /broadcast <message> - Send message to all users\n\n"
            )
        
        help_text += (
            "📞 **Support:**\n"
            "• Join our channel: @daawotv\n"
            "• Contact admin for premium access\n"
            "• Report issues or get help\n\n"
            "🔒 **Privacy & Security:**\n"
            "• Files stored on Telegram servers\n"
            "• No data stored externally\n"
            "• Links work permanently"
        )
        
        # Create upgrade button for free users
        if not is_user_premium and not is_user_admin:
            upgrade_button = types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton("💎 Upgrade to Premium", callback_data=f"upgrade_{user_id}")]
            ])
            await message.reply_text(help_text, parse_mode="Markdown", reply_markup=upgrade_button)
        else:
            await message.reply_text(help_text, parse_mode="Markdown")
        
        logger.info(f"Help command used by user {user_id}")
    except Exception as e:
        logger.error(f"Error in help handler: {e}")
        await message.reply_text("❌ An error occurred while displaying help information.")

@app.on_callback_query()
async def callback_handler(client, callback_query):
    """Handle callback queries from inline buttons"""
    try:
        data = callback_query.data
        user_id = callback_query.from_user.id
        
        if data.startswith("upgrade_"):
            # Handle upgrade button press
            upgrade_text = (
                "💎 **Premium Plan Details**\n\n"
                "🎯 **Benefits:**\n"
                "• Unlimited file uploads\n"
                "• No file size restrictions\n"
                "• Priority support\n"
                "• Permanent file storage\n"
                "• Early access to new features\n\n"
                "💰 **Pricing:**\n"
                "• Monthly: Contact admin\n"
                "• Lifetime: Contact admin\n\n"
                "📞 **How to Upgrade:**\n"
                "Contact our admin to get premium access!\n"
                "Channel: @daawotv\n\n"
                "📝 **Note:** Include your user ID when contacting admin.\n"
                f"Your ID: `{user_id}`"
            )
            
            contact_button = types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton("📞 Contact Admin", url="https://t.me/daawotv")]
            ])
            
            await callback_query.edit_message_text(
                upgrade_text, 
                parse_mode="Markdown", 
                reply_markup=contact_button
            )
            
        await callback_query.answer()
        logger.info(f"Callback query handled: {data} from user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in callback handler: {e}")
        await callback_query.answer("❌ An error occurred. Please try again.")

@app.on_message(filters.command("premium"))
async def premium_handler(client, message):
    """Handle /premium command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.")
            return
        
        args = message.text.split()
        if len(args) != 2:
            await message.reply_text("❌ Usage: /premium <user_id>")
            return
        
        try:
            target_user_id = int(args[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")
            return
        
        if add_premium_user(target_user_id):
            await message.reply_text(f"✅ User {target_user_id} has been granted premium access!")
            logger.info(f"Admin {message.from_user.id} granted premium to user {target_user_id}")
            
            # Try to notify the user
            try:
                await client.send_message(
                    target_user_id,
                    "🎉 Congratulations! You have been granted premium access!\n\n"
                    "💎 Premium Benefits:\n"
                    "• Unlimited file uploads\n"
                    "• No file size restrictions\n"
                    "• Priority support\n"
                    "• Permanent file storage\n\n"
                    "Thank you for using our bot!"
                )
            except Exception as e:
                logger.warning(f"Could not notify user {target_user_id} about premium access: {e}")
        else:
            await message.reply_text("❌ Failed to grant premium access. Please try again.")
    except Exception as e:
        logger.error(f"Error in premium handler: {e}")
        await message.reply_text("❌ An error occurred while processing the premium command.")

@app.on_message(filters.command("unpremium"))
async def unpremium_handler(client, message):
    """Handle /unpremium command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.")
            return
        
        args = message.text.split()
        if len(args) != 2:
            await message.reply_text("❌ Usage: /unpremium <user_id>")
            return
        
        try:
            target_user_id = int(args[1])
        except ValueError:
            await message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")
            return
        
        if remove_premium_user(target_user_id):
            await message.reply_text(f"✅ Premium access removed from user {target_user_id}")
            logger.info(f"Admin {message.from_user.id} removed premium from user {target_user_id}")
            
            # Try to notify the user
            try:
                await client.send_message(
                    target_user_id,
                    "📢 Your premium access has been revoked.\n\n"
                    "You are now limited to the free plan:\n"
                    f"• Maximum {FREE_USER_LIMIT} file uploads\n"
                    "• Contact admin if you have questions\n\n"
                    "Thank you for understanding."
                )
            except Exception as e:
                logger.warning(f"Could not notify user {target_user_id} about premium removal: {e}")
        else:
            await message.reply_text("❌ Failed to remove premium access. Please try again.")
    except Exception as e:
        logger.error(f"Error in unpremium handler: {e}")
        await message.reply_text("❌ An error occurred while processing the unpremium command.")

@app.on_message(filters.command("stats"))
async def stats_handler(client, message):
    """Handle /stats command - Admin only"""
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied. This command is for administrators only.")
            return
        
        stats = load_stats()
        premium_users = load_premium_users()
        premium_count = len(premium_users)
        free_users = stats["total_users"] - premium_count
        
        stats_text = (
            f"📊 **Bot Statistics**\n\n"
            f"👥 **Users:**\n"
            f"• Total Users: {stats['total_users']}\n"
            f"• Free Users: {free_users}\n"
            f"• Premium Users: {premium_count}\n\n"
            f"📁 **Files:**\n"
            f"• Total Files: {stats['total_files']}\n"
            f"• Documents: {stats['files_by_type']['document']}\n"
            f"• Videos: {stats['files_by_type']['video']}\n"
            f"• Audio: {stats['files_by_type']['audio']}\n"
            f"• Photos: {stats['files_by_type']['photo']}\n\n"
            f"📥 **Downloads:** {stats['downloads']}\n\n"
            f"🔝 **Top Users:**\n"
        )
        
        # Get top users by file uploads
        users_by_files = []
        for uid, user_data in stats["users"].items():
            username = user_data.get("username", "Unknown")
            files = user_data.get("files_uploaded", 0)
            if files > 0:
                users_by_files.append((username, files, uid))
        
        users_by_files.sort(key=lambda x: x[1], reverse=True)
        
        for i, (username, files, uid) in enumerate(users_by_files[:10], 1):
            premium_status = "💎" if int(uid) in premium_users else "🆓"
            stats_text += f"{i}. {premium_status} @{username}: {files} files\n"
        
        await message.reply_text(stats_text, parse_mode="Markdown")
        logger.info(f"Stats command used by admin {message.from_user.id}")
    except Exception as e:
        logger.error(f"Error in stats handler: {e}")
        await message.reply_text("❌ An error occurred while retrieving statistics.")

if __name__ == "__main__":
    print("🤖 Starting File Saver Bot...")
    print("📊 Bot features:")
    print("   • File upload and sharing")
    print("   • Premium user system")
    print("   • Usage limits for free users")
    print("   • Admin management commands")
    print("   • User statistics and analytics")
    print("   • Ban/unban system")
    print("   • Broadcast messaging")
    print("✅ Bot is ready!")
    
    # Start keep-alive server
    keep_alive()
    
    # Start the bot
    app.run()
"""
Message handlers for YukkiChatBot
Handles all bot commands and message processing
"""

import logging
from typing import Dict, Any
from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import Message
from storage import Storage
from config import Config
from utils import format_stats, escape_markdown, get_user_info

logger = logging.getLogger(__name__)

def register_handlers(app: Client, storage: Storage, config: Config):
    """Register all message handlers"""
    
    @app.on_message(filters.command("start") & filters.private)
    async def start_command(client: Client, message: Message):
        """Handle /start command"""
        try:
            user_id = message.from_user.id
            user_data = get_user_info(message.from_user)
            
            # Add user to storage
            storage.add_user(user_id, user_data)
            
            # Check if user is blocked
            if storage.is_user_blocked(user_id):
                await message.reply_text(
                    "❌ You have been blocked from using this bot.\n"
                    "Contact the administrator if you believe this is an error."
                )
                return
            
            # Send welcome message without buttons
            await message.reply_text(
                config.WELCOME_MESSAGE,
                disable_web_page_preview=True
            )
            
            logger.info(f"User {user_id} started the bot")
            
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await message.reply_text("❌ An error occurred. Please try again later.")
    
    @app.on_message(filters.command("help") & filters.private)
    async def help_command(client: Client, message: Message):
        """Handle /help command"""
        try:
            help_text = (
                "🤖 YukkiChatBot Help\n\n"
                "📝 How to use:\n"
                "• Send any message to submit anonymous feedback\n"
                "• Your identity will remain completely anonymous\n"
                "• Admins will receive your message and can respond\n\n"
                "🔧 Available Commands:\n"
                "• /start - Start the bot\n"
                "• /help - Show this help message\n\n"
                "⚠️ Rules:\n"
                "• Be respectful and constructive\n"
                "• No spam or inappropriate content\n"
                "• Follow community guidelines\n\n"
                "📞 Support:\n"
                "If you encounter any issues, please contact the administrators."
            )
            
            await message.reply_text(help_text, disable_web_page_preview=True)
            
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await message.reply_text("❌ An error occurred. Please try again later.")
    
    @app.on_message(filters.command("stats") & filters.private)
    async def stats_command(client: Client, message: Message):
        """Handle /stats command (admin only)"""
        try:
            user_id = message.from_user.id
            
            if not config.is_admin(user_id):
                await message.reply_text("❌ You don't have permission to use this command.")
                return
            
            stats = storage.get_stats()
            stats_text = format_stats(stats)
            
            await message.reply_text(f"📊 Bot Statistics\n\n{stats_text}")
            
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await message.reply_text("❌ An error occurred while fetching statistics.")
    
    @app.on_message(filters.command("block") & filters.private)
    async def block_command(client: Client, message: Message):
        """Handle /block command (admin only)"""
        try:
            user_id = message.from_user.id
            
            if not config.is_admin(user_id):
                await message.reply_text("❌ You don't have permission to use this command.")
                return
            
            # Extract user ID from command
            if len(message.command) < 2:
                await message.reply_text(
                    "❌ Please provide a user ID to block.\n"
                    "Usage: /block <user_id>"
                )
                return
            
            try:
                target_user_id = int(message.command[1])
            except ValueError:
                await message.reply_text("❌ Invalid user ID. Please provide a valid number.")
                return
            
            if config.is_admin(target_user_id):
                await message.reply_text("❌ Cannot block an administrator.")
                return
            
            storage.block_user(target_user_id)
            await storage.save_data()
            
            await message.reply_text(f"✅ User {target_user_id} has been blocked.")
            
        except Exception as e:
            logger.error(f"Error in block command: {e}")
            await message.reply_text("❌ An error occurred while blocking the user.")
    
    @app.on_message(filters.command("unblock") & filters.private)
    async def unblock_command(client: Client, message: Message):
        """Handle /unblock command (admin only)"""
        try:
            user_id = message.from_user.id
            
            if not config.is_admin(user_id):
                await message.reply_text("❌ You don't have permission to use this command.")
                return
            
            # Extract user ID from command
            if len(message.command) < 2:
                await message.reply_text(
                    "❌ Please provide a user ID to unblock.\n"
                    "Usage: /unblock <user_id>"
                )
                return
            
            try:
                target_user_id = int(message.command[1])
            except ValueError:
                await message.reply_text("❌ Invalid user ID. Please provide a valid number.")
                return
            
            storage.unblock_user(target_user_id)
            await storage.save_data()
            
            await message.reply_text(f"✅ User {target_user_id} has been unblocked.")
            
        except Exception as e:
            logger.error(f"Error in unblock command: {e}")
            await message.reply_text("❌ An error occurred while unblocking the user.")
    
    @app.on_message(filters.command("mode") & filters.private)
    async def mode_command(client: Client, message: Message):
        """Handle /mode command (admin only)"""
        try:
            user_id = message.from_user.id
            
            if not config.is_admin(user_id):
                await message.reply_text("❌ You don't have permission to use this command.")
                return
            
            if len(message.command) < 2:
                current_mode = storage.get_bot_mode()
                target_group = storage.get_target_group_id()
                
                mode_text = f"🔧 Current Mode: {current_mode}\n"
                if target_group:
                    mode_text += f"📍 Target Group: {target_group}\n"
                
                mode_text += (
                    "\nAvailable modes:\n"
                    "• private - Send messages to admin DMs\n"
                    "• group - Send messages to a group\n\n"
                    "Usage:\n"
                    "• /mode private - Switch to private mode\n"
                    "• /mode group <group_id> - Switch to group mode"
                )
                
                await message.reply_text(mode_text)
                return
            
            new_mode = message.command[1].lower()
            
            if new_mode == "private":
                storage.set_bot_mode("private")
                config.BOT_MODE = "private"
                await storage.save_data()
                await message.reply_text("✅ Mode changed to private. Messages will be sent to admin DMs.")
                
            elif new_mode == "group":
                if len(message.command) < 3:
                    await message.reply_text(
                        "❌ Please provide a group ID.\n"
                        "Usage: /mode group <group_id>"
                    )
                    return
                
                try:
                    group_id = int(message.command[2])
                    storage.set_bot_mode("group", group_id)
                    config.BOT_MODE = "group"
                    config.TARGET_GROUP_ID = group_id
                    await storage.save_data()
                    await message.reply_text(f"✅ Mode changed to group. Messages will be sent to group {group_id}.")
                except ValueError:
                    await message.reply_text("❌ Invalid group ID. Please provide a valid number.")
            
            else:
                await message.reply_text(
                    "❌ Invalid mode. Available modes: private, group"
                )
            
        except Exception as e:
            logger.error(f"Error in mode command: {e}")
            await message.reply_text("❌ An error occurred while changing mode.")
    
    @app.on_message(filters.command("broadcast") & filters.private)
    async def broadcast_command(client: Client, message: Message):
        """Handle /broadcast command (admin only)"""
        try:
            user_id = message.from_user.id
            
            if not config.is_admin(user_id):
                await message.reply_text("❌ You don't have permission to use this command.")
                return
            
            # Get broadcast message
            broadcast_text = ""
            if message.reply_to_message:
                broadcast_message = message.reply_to_message
            elif len(message.text.split(None, 1)) > 1:
                broadcast_text = message.text.split(None, 1)[1]
                broadcast_message = None
            else:
                await message.reply_text(
                    "❌ Please provide a message to broadcast.\n"
                    "Usage: /broadcast <message> or reply to a message with /broadcast"
                )
                return
            
            # Get all user IDs
            user_ids = storage.get_all_user_ids()
            
            if not user_ids:
                await message.reply_text("❌ No users found to broadcast to.")
                return
            
            # Send confirmation
            confirm_msg = await message.reply_text(
                f"🚀 Starting broadcast to {len(user_ids)} users..."
            )
            
            success_count = 0
            failed_count = 0
            
            # Send broadcast
            for target_user_id in user_ids:
                try:
                    if broadcast_message:
                        await broadcast_message.copy(target_user_id)
                    else:
                        await client.send_message(target_user_id, broadcast_text)
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    logger.debug(f"Failed to send broadcast to {target_user_id}: {e}")
            
            # Update confirmation message
            await confirm_msg.edit_text(
                f"📊 Broadcast Complete\n\n"
                f"✅ Successfully sent: {success_count}\n"
                f"❌ Failed: {failed_count}\n"
                f"📤 Total users: {len(user_ids)}"
            )
            
        except Exception as e:
            logger.error(f"Error in broadcast command: {e}")
            await message.reply_text("❌ An error occurred while broadcasting.")
    
    @app.on_message(filters.command("reply") & filters.private)
    async def reply_command(client: Client, message: Message):
        """Handle /reply command (admin only)"""
        try:
            user_id = message.from_user.id
            
            if not config.is_admin(user_id):
                await message.reply_text("❌ You don't have permission to use this command.")
                return
            
            # Extract user ID and reply message
            if len(message.command) < 3:
                await message.reply_text(
                    "❌ Please provide a user ID and reply message.\n"
                    "Usage: /reply <user_id> <your_message>"
                )
                return
            
            try:
                target_user_id = int(message.command[1])
                reply_text = " ".join(message.command[2:])
            except ValueError:
                await message.reply_text("❌ Invalid user ID. Please provide a valid number.")
                return
            
            if not reply_text.strip():
                await message.reply_text("❌ Please provide a reply message.")
                return
            
            # Check if user exists
            user_data = storage.get_user(target_user_id)
            if not user_data:
                await message.reply_text("❌ User not found in database.")
                return
            
            # Check if user is blocked
            if storage.is_user_blocked(target_user_id):
                await message.reply_text("❌ Cannot reply to a blocked user.")
                return
            
            # Send reply to user
            try:
                admin_reply = (
                    f"📨 Reply from Administrator:\n\n"
                    f"{reply_text}\n\n"
                    f"You can continue sending messages for more assistance."
                )
                await client.send_message(target_user_id, admin_reply)
                
                # Confirm to admin
                await message.reply_text(f"✅ Reply sent to user {target_user_id}")
                
            except Exception as e:
                logger.error(f"Error sending reply to user {target_user_id}: {e}")
                await message.reply_text(
                    f"❌ Failed to send reply to user {target_user_id}. "
                    f"User may have blocked the bot or deleted their account."
                )
            
        except Exception as e:
            logger.error(f"Error in reply command: {e}")
            await message.reply_text("❌ An error occurred while sending reply.")
    
    @app.on_message(filters.private & ~filters.command(["start", "help", "stats", "block", "unblock", "mode", "broadcast", "reply"]))
    async def handle_private_message(client: Client, message: Message):
        """Handle private messages (feedback submission or admin replies)"""
        try:
            user_id = message.from_user.id
            user_data = get_user_info(message.from_user)
            
            # Add/update user
            is_new_user = storage.add_user(user_id, user_data)
            
            # Check if user is blocked
            if storage.is_user_blocked(user_id):
                await message.reply_text(
                    "❌ You have been blocked from using this bot.\n"
                    "Contact the administrator if you believe this is an error."
                )
                return
            
            # Check if message is from admin replying to a user message
            if config.is_admin(user_id) and message.reply_to_message:
                await handle_admin_reply(client, message, storage, config)
                return
            
            # Check if message is from admin (but not a reply)
            if config.is_admin(user_id):
                await message.reply_text(
                    "👨‍💼 You are an administrator. To reply to users, reply directly to their forwarded messages in this chat."
                )
                return
            
            # Check rate limiting
            if storage.check_rate_limit(user_id, config.RATE_LIMIT_MESSAGES, config.RATE_LIMIT_WINDOW):
                await message.reply_text(
                    f"⏰ You're sending messages too quickly. Please wait a moment before sending another message.\n"
                    f"Limit: {config.RATE_LIMIT_MESSAGES} messages per {config.RATE_LIMIT_WINDOW} seconds."
                )
                return
            
            # Send welcome message only once per user (Fix #1)
            if not storage.is_user_welcomed(user_id):
                await message.reply_text("Welcome, I will reply to you.")
                storage.set_user_welcomed(user_id)
            
            # Increment message count
            storage.increment_message_count(user_id)
            
            # Add to message history
            storage.add_message_to_history({
                'user_id': user_id,
                'message_type': message.media.value if message.media else 'text',
                'text': message.text[:100] if message.text else None
            })
            
            # Get username for display
            user = message.from_user
            if user.username:
                display_name = f"@{user.username}"
            else:
                # Use first name if available, otherwise use User ID
                display_name = user.first_name or f"User{user_id}"
            
            # Determine target chat
            target_chat_id = config.get_target_chat_id()
            
            # Create a single message that looks like a forward with username
            try:
                if message.text:
                    # Text message - create forward-like format
                    forward_text = f"Forwarded from {display_name}\n\n{message.text}"
                    sent_msg = await client.send_message(target_chat_id, forward_text)
                elif message.photo:
                    # Photo - use caption to show forward info
                    caption = f"Forwarded from {display_name}"
                    if message.caption:
                        caption += f"\n\n{message.caption}"
                    sent_msg = await client.send_photo(target_chat_id, message.photo.file_id, caption=caption)
                elif message.video:
                    # Video - use caption to show forward info
                    caption = f"Forwarded from {display_name}"
                    if message.caption:
                        caption += f"\n\n{message.caption}"
                    sent_msg = await client.send_video(target_chat_id, message.video.file_id, caption=caption)
                elif message.document:
                    # Document - use caption to show forward info
                    caption = f"Forwarded from {display_name}"
                    if message.caption:
                        caption += f"\n\n{message.caption}"
                    sent_msg = await client.send_document(target_chat_id, message.document.file_id, caption=caption)
                elif message.audio:
                    # Audio - use caption to show forward info
                    caption = f"Forwarded from {display_name}"
                    if message.caption:
                        caption += f"\n\n{message.caption}"
                    sent_msg = await client.send_audio(target_chat_id, message.audio.file_id, caption=caption)
                elif message.voice:
                    # Voice - use caption to show forward info  
                    sent_msg = await client.send_voice(target_chat_id, message.voice.file_id, caption=f"Forwarded from {display_name}")
                elif message.video_note:
                    # Video note doesn't support captions, so send with text after
                    sent_msg = await client.send_video_note(target_chat_id, message.video_note.file_id)
                    await client.send_message(target_chat_id, f"👆 Forwarded from {display_name}")
                elif message.sticker:
                    # Sticker doesn't support captions, so send with text after
                    sent_msg = await client.send_sticker(target_chat_id, message.sticker.file_id)
                    await client.send_message(target_chat_id, f"👆 Forwarded from {display_name}")
                elif message.animation:
                    # GIF/Animation - use caption to show forward info
                    caption = f"Forwarded from {display_name}"
                    if message.caption:
                        caption += f"\n\n{message.caption}"
                    sent_msg = await client.send_animation(target_chat_id, message.animation.file_id, caption=caption)
                else:
                    # Fallback
                    sent_msg = await client.send_message(target_chat_id, f"Forwarded from {display_name}\n\n[Media message]")
                
                # Store message mapping for proper reply linking
                message_key = f"{user_id}_{message.id}"
                if sent_msg:
                    storage.store_message_mapping(message_key, sent_msg.id)
                
            except Exception as e:
                logger.error(f"Error forwarding message to admin: {e}")
                await message.reply_text(
                    "❌ Sorry, there was an error processing your message. Please try again later."
                )
                return
            
            # Save data
            await storage.save_data()
            
        except Exception as e:
            logger.error(f"Error handling private message: {e}")
            await message.reply_text("❌ An error occurred. Please try again later.")
    
    async def handle_admin_reply(client: Client, message: Message, storage: Storage, config: Config):
        """Handle admin replies to user messages with proper linking"""
        try:
            # Get the message being replied to
            replied_message = message.reply_to_message
            
            # Extract user ID from "Forwarded from" message format
            target_user_id = None
            
            # Get content from text or caption
            content = replied_message.text or replied_message.caption or ""
            
            # Look for "Forwarded from @username" or "Forwarded from UserXXXX" pattern
            import re
            forward_match = re.search(r'Forwarded from (.+?)(?:\n|$)', content)
            
            if forward_match:
                display_name = forward_match.group(1).strip()
                
                # If it's UserXXXX format
                if display_name.startswith('User') and display_name[4:].isdigit():
                    target_user_id = int(display_name[4:])
                
                # If it's @username format
                elif display_name.startswith('@'):
                    clean_username = display_name[1:]
                    for uid, user_data in storage.users.items():
                        if user_data.get('username') == clean_username:
                            target_user_id = uid
                            break
                
                # If it's a first name, try to find by first name
                else:
                    for uid, user_data in storage.users.items():
                        if user_data.get('first_name') == display_name:
                            target_user_id = uid
                            break
            
            if not target_user_id:
                await message.reply_text("❌ Could not identify the user to reply to.")
                return
            
            # Check if user exists and is not blocked
            if not storage.get_user(target_user_id):
                await message.reply_text("❌ User not found in database.")
                return
            
            if storage.is_user_blocked(target_user_id):
                await message.reply_text("❌ Cannot reply to a blocked user.")
                return
            
            # Send only the admin's reply text to user as a proper reply
            try:
                # Find the original user message to reply to
                original_message_id = None
                
                # Look through message mapping to find the original message
                for key, admin_msg_id in storage.message_mapping.items():
                    if admin_msg_id == replied_message.id:
                        # Extract original message ID from key
                        parts = key.split('_')
                        if len(parts) >= 2:
                            original_message_id = int(parts[1])
                            break
                
                # Send reply with proper linking
                if original_message_id:
                    await client.send_message(
                        target_user_id, 
                        message.text or message.caption or "📨 [Media reply from administrator]",
                        reply_to_message_id=original_message_id
                    )
                else:
                    # Fallback: send without reply linking
                    await client.send_message(
                        target_user_id, 
                        message.text or message.caption or "📨 [Media reply from administrator]"
                    )
                
                # Confirm to admin
                await message.reply_text(f"✅ Reply sent to user")
                
            except Exception as e:
                logger.error(f"Error sending reply to user {target_user_id}: {e}")
                await message.reply_text(
                    f"❌ Failed to send reply to user. "
                    f"User may have blocked the bot or deleted their account."
                )
            
        except Exception as e:
            logger.error(f"Error in admin reply handler: {e}")
            await message.reply_text("❌ An error occurred while sending reply.")
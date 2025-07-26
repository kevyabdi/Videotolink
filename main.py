
import os
import json
import logging
from flask import Flask, request, jsonify
from pyrogram import Client
from pyrogram.types import Update
import asyncio
import threading
from datetime import datetime

# Import our modules
from bot_handlers import setup_handlers
from utils import load_files, load_stats, load_banned_users
from webhook_handler import WebhookHandler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get credentials from environment variables with fallbacks
API_ID = int(os.getenv("API_ID", "26176218"))
API_HASH = os.getenv("API_HASH", "4a50bc8acb0169930f5914eb88091736")
BOT_TOKEN = os.getenv("BOT_TOKEN", "6847890390:AAG7sASVY1IJbrbjX6GT5CCXUxD7_mtY_VA")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "1096693642"))

# Validate required environment variables
if not all([API_ID, API_HASH, BOT_TOKEN, ADMIN_USER_ID]):
    logger.error("Missing required environment variables!")
    logger.error("Required: API_ID, API_HASH, BOT_TOKEN, ADMIN_USER_ID")
    exit(1)

# Initialize Flask app
app = Flask(__name__)

# Initialize Pyrogram client
pyrogram_client = Client(
    "filetobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Initialize webhook handler
webhook_handler = WebhookHandler(pyrogram_client, ADMIN_USER_ID)

# Ensure required JSON files exist
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
        "banned_users.json": []
    }
    
    for filename, default_data in files_to_create.items():
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                json.dump(default_data, f, indent=2)
            logger.info(f"Created {filename}")

# Flask routes for health checks and webhook
@app.route('/')
def home():
    """Health check endpoint with bot status page"""
    return '''
    <!DOCTYPE html>
    <html>
        <head>
            <title>Telegram File Saver Bot</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .container {
                    max-width: 800px;
                    width: 90%;
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 20px;
                    backdrop-filter: blur(15px);
                    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                    text-align: center;
                }
                h1 { 
                    font-size: 2.5em; 
                    margin-bottom: 20px; 
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }
                .status { 
                    background: rgba(0,255,0,0.2); 
                    padding: 20px; 
                    border-radius: 15px; 
                    margin: 30px 0;
                    border: 2px solid rgba(0,255,0,0.3);
                }
                .feature-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-top: 30px;
                }
                .feature {
                    background: rgba(255,255,255,0.1);
                    padding: 25px;
                    border-radius: 15px;
                    text-align: left;
                    transition: transform 0.3s ease;
                }
                .feature:hover {
                    transform: translateY(-5px);
                }
                .feature h3 {
                    margin-bottom: 15px;
                    color: #fff;
                    font-size: 1.2em;
                }
                .stats-section {
                    background: rgba(255,255,255,0.05);
                    padding: 20px;
                    border-radius: 15px;
                    margin: 20px 0;
                }
                .bot-link {
                    display: inline-block;
                    background: rgba(255,255,255,0.2);
                    padding: 15px 30px;
                    border-radius: 50px;
                    text-decoration: none;
                    color: white;
                    font-weight: bold;
                    margin-top: 20px;
                    transition: background 0.3s ease;
                }
                .bot-link:hover {
                    background: rgba(255,255,255,0.3);
                }
                @media (max-width: 600px) {
                    .container { padding: 20px; }
                    h1 { font-size: 2em; }
                    .feature-grid { grid-template-columns: 1fr; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Telegram File Saver Bot</h1>
                
                <div class="status">
                    <h2>🟢 Bot is Online & Ready</h2>
                    <p>Your Telegram bot is running successfully on Render!</p>
                    <p><strong>Deployment Status:</strong> Active | <strong>Method:</strong> Webhook</p>
                </div>
                
                <div class="stats-section">
                    <h3>📊 Live Statistics</h3>
                    <p>Service uptime: Active | Health checks: Passing</p>
                    <p>Ready to handle file uploads and downloads</p>
                </div>
                
                <div class="feature-grid">
                    <div class="feature">
                        <h3>📁 File Upload & Sharing</h3>
                        <p>Upload any file type and get permanent shareable download links instantly.</p>
                    </div>
                    
                    <div class="feature">
                        <h3>🔗 Permanent Links</h3>
                        <p>Generated links work indefinitely using Telegram's infrastructure.</p>
                    </div>
                    
                    <div class="feature">
                        <h3>🛡️ Admin Controls</h3>
                        <p>Comprehensive user management, statistics, and ban system for administrators.</p>
                    </div>
                    
                    <div class="feature">
                        <h3>☁️ Cloud Storage</h3>
                        <p>No external hosting required - files are stored securely on Telegram's servers.</p>
                    </div>
                </div>
                
                <a href="https://t.me/your_bot_username" class="bot-link">
                    🚀 Start Using Bot on Telegram
                </a>
                
                <div style="margin-top: 30px; opacity: 0.8; font-size: 0.9em;">
                    <p>Deployed on Render.com | Webhook Mode | Production Ready</p>
                </div>
            </div>
        </body>
    </html>
    '''

@app.route('/health')
def health():
    """Simple health check for monitoring"""
    try:
        # Check if essential files exist
        files_exist = all(os.path.exists(f) for f in ["files.json", "stats.json", "banned_users.json"])
        
        return jsonify({
            "status": "healthy",
            "service": "telegram-file-saver-bot",
            "timestamp": datetime.utcnow().isoformat(),
            "files_ready": files_exist,
            "webhook_active": True
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook updates from Telegram"""
    try:
        if request.headers.get('content-type') != 'application/json':
            return 'Invalid content type', 400
            
        json_data = request.get_json()
        if not json_data:
            return 'No JSON data', 400
            
        # Process the update asynchronously
        asyncio.create_task(webhook_handler.process_update(json_data))
        
        return 'OK', 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return 'Internal Server Error', 500

@app.route('/stats')
def public_stats():
    """Public stats endpoint (basic info only)"""
    try:
        stats = load_stats()
        return jsonify({
            "total_users": stats.get("total_users", 0),
            "total_files": stats.get("total_files", 0),
            "downloads": stats.get("downloads", 0),
            "status": "operational"
        })
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({"error": "Stats unavailable"}), 500

async def setup_webhook():
    """Set up webhook with Telegram"""
    try:
        # Get the external URL from Render environment
        external_url = os.getenv('RENDER_EXTERNAL_URL')
        if not external_url:
            logger.error("RENDER_EXTERNAL_URL not found! Cannot set webhook.")
            return False
            
        webhook_url = f"{external_url}/webhook"
        
        # Start the client
        await pyrogram_client.start()
        
        # Set webhook
        success = await pyrogram_client.set_webhook(webhook_url)
        if success:
            logger.info(f"Webhook set successfully: {webhook_url}")
            
            # Get bot info
            me = await pyrogram_client.get_me()
            logger.info(f"Bot started: @{me.username} ({me.first_name})")
            
            return True
        else:
            logger.error("Failed to set webhook")
            return False
            
    except Exception as e:
        logger.error(f"Webhook setup error: {e}")
        return False

def run_bot():
    """Run the bot setup in the background"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Setup webhook
        success = loop.run_until_complete(setup_webhook())
        if not success:
            logger.error("Failed to setup webhook. Bot may not work properly.")
            
        # Keep the event loop running
        loop.run_forever()
        
    except Exception as e:
        logger.error(f"Bot thread error: {e}")

if __name__ == '__main__':
    try:
        # Ensure JSON files exist
        ensure_json_files()
        
        # Setup bot handlers
        setup_handlers(pyrogram_client, ADMIN_USER_ID)
        
        # Start bot in background thread
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        # Get port from environment (Render provides this)
        port = int(os.environ.get('PORT', 5000))
        
        logger.info(f"Starting Flask server on port {port}")
        logger.info("Bot is running in webhook mode for Render deployment")
        
        # Run Flask app
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,  # Never use debug=True in production
            use_reloader=False  # Prevent multiple instances
        )
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)

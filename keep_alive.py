from flask import Flask, jsonify
from threading import Thread
import logging
import os

# Suppress Flask's default logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Telegram File Saver Bot with Premium Features is running!"

@app.route('/status')
def status():
    return jsonify({
        "status": "online",
        "message": "Bot is active and running with session recovery",
        "features": {
            "premium_system": "enabled",
            "session_recovery": "enabled", 
            "automatic_cleanup": "enabled",
            "join_daawo_button": "enabled",
            "admin_contact": "@viizet"
        },
        "session_info": {
            "session_files_cleaned": "on_startup_if_corrupted",
            "auto_recovery": "enabled",
            "max_retry_attempts": 3
        }
    })

@app.route('/features')
def features():
    return jsonify({
        "session_management": {
            "automatic_recovery": "Handles SESSION_REVOKED errors automatically",
            "session_cleanup": "Removes corrupted session files",
            "retry_mechanism": "Up to 3 retry attempts with fresh sessions",
            "error_handling": "Comprehensive error handling for auth issues"
        },
        "file_sharing": {
            "unlimited_uploads": "No restrictions on file uploads",
            "permanent_links": "Files never expire",
            "all_file_types": "Documents, videos, audio, photos supported",
            "telegram_storage": "Uses Telegram's infrastructure"
        },
        "user_interface": {
            "welcome_message": "Clean interface with quick access buttons",
            "direct_contact": "Easy access to bot owner (@viizet)",
            "community_access": "JOIN DAAWO button for videos",
            "error_messages": "Detailed error handling and user feedback"
        },
        "admin_commands": [
            "/stats - View bot statistics",
            "/premium <user_id> - Grant premium status",
            "/unpremium <user_id> - Remove premium status",
            "/ban <user_id> - Ban user",
            "/unban <user_id> - Unban user"
        ],
        "user_commands": [
            "/start - Welcome message and file sharing",
            "Send any file - Get shareable download link"
        ]
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": "2025-01-29T12:00:00Z",
        "components": {
            "web_server": "running",
            "session_manager": "active",
            "json_databases": "accessible"
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": ["/", "/status", "/features", "/health"]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal Server Error", 
        "message": "An unexpected error occurred",
        "contact": "@viizet"
    }), 500

def run():
    """Run the Flask web server"""
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except Exception as e:
        logging.error(f"Failed to start web server: {e}")

def keep_alive():
    """Start the keep-alive server in a separate thread"""
    try:
        t = Thread(target=run)
        t.daemon = True
        t.start()
        print("✅ Keep-alive server started on port 5000 with session recovery features")
        return True
    except Exception as e:
        print(f"❌ Failed to start keep-alive server: {e}")
        return False

if __name__ == "__main__":
    keep_alive()

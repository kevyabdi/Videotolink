from flask import Flask
from threading import Thread
import logging

# Suppress Flask's default logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram File Saver Bot with Premium Features is running!"

@app.route('/status')
def status():
    return {
        "status": "online",
        "message": "Bot is active and running with premium features",
        "features": {
            "premium_system": "enabled",
            "usage_limits": "enabled",
            "join_daawo_button": "enabled",
            "admin_contact": "@viizet"
        }
    }

@app.route('/features')
def features():
    return {
        "premium_features": {
            "unlimited_uploads": "Premium users only",
            "no_daily_limits": "Premium users only",
            "no_waiting_periods": "Premium users only",
            "priority_support": "Premium users only"
        },
        "free_features": {
            "daily_uploads": "5 files per day",
            "cooldown_period": "4 hours after limit",
            "file_sharing": "Permanent download links"
        },
        "admin_commands": [
            "/premium <user_id>",
            "/unpremium <user_id>",
            "/stats",
            "/users",
            "/ban <user_id>",
            "/unban <user_id>",
            "/banned",
            "/broadcast <message>"
        ],
        "user_commands": [
            "/start",
            "/upgrade",
            "/myplan"
        ]
    }

def run():
    app.run(host='0.0.0.0', port=8080, debug=False)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("Keep-alive server started on port 8080 with premium features")

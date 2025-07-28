from flask import Flask
from threading import Thread
import logging

# Suppress Flask's default logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram File Saver Bot is running!"

@app.route('/status')
def status():
    return {
        "status": "online",
        "message": "Bot is active and running"
    }

def run():
    app.run(host='0.0.0.0', port=8080, debug=False)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("Keep-alive server started on port 8080")
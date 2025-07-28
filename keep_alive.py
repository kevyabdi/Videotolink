from flask import Flask
from threading import Thread
import time

# Create Flask app for keep-alive functionality
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
        <head>
            <title>Telegram File Saver Bot</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f0f0f0; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                .status { color: #28a745; font-weight: bold; font-size: 18px; }
                .feature { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Telegram File Saver Bot</h1>
                <div class="status">✅ Bot is running and active!</div>
                <br>
                <h3>📋 Features:</h3>
                <div class="feature">📁 File Upload & Sharing</div>
                <div class="feature">💎 Premium User System</div>
                <div class="feature">📊 Usage Limits & Analytics</div>
                <div class="feature">👑 Admin Management Tools</div>
                <div class="feature">🚫 Ban/Unban System</div>
                <div class="feature">📢 Broadcast Messaging</div>
                <div class="feature">🔗 Permanent Download Links</div>
                <br>
                <p><strong>Channel:</strong> <a href="https://t.me/daawotv" target="_blank">@daawotv</a></p>
                <p><em>Last updated: ''' + time.strftime('%Y-%m-%d %H:%M:%S UTC') + '''</em></p>
            </div>
        </body>
    </html>
    '''

@app.route('/health')
def health():
    return {'status': 'healthy', 'timestamp': time.time(), 'message': 'Bot is running successfully'}

def run():
    """Run the Flask app"""
    app.run(host='0.0.0.0', port=5000, debug=False)

def keep_alive():
    """Keep the bot alive by running Flask server in a separate thread"""
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("🌐 Keep-alive server started on port 5000")

if __name__ == '__main__':
    keep_alive()

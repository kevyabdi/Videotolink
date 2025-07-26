from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return '''
    <html>
        <head>
            <title>File Saver Bot</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    margin: 0;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                }
                h1 { color: #fff; margin-bottom: 20px; }
                .status { 
                    background: rgba(0,255,0,0.2); 
                    padding: 10px; 
                    border-radius: 10px; 
                    margin: 20px 0;
                }
                .feature {
                    background: rgba(255,255,255,0.1);
                    margin: 10px 0;
                    padding: 15px;
                    border-radius: 10px;
                    text-align: left;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📁 File Saver Bot</h1>
                <div class="status">
                    <h2>🟢 Bot is Running</h2>
                    <p>Your Telegram bot is active and ready to receive files!</p>
                </div>
                
                <div class="feature">
                    <h3>🔗 Generate Shareable Links</h3>
                    <p>Upload any file to the bot and get a unique download link that you can share with anyone.</p>
                </div>
                
                <div class="feature">
                    <h3>📂 Supported File Types</h3>
                    <p>Documents, Videos, Audio files, and Photos - all stored securely on Telegram's servers.</p>
                </div>
                
                <div class="feature">
                    <h3>🔒 Secure Storage</h3>
                    <p>No external hosting required. Files are stored using Telegram's infrastructure.</p>
                </div>
                
                <p style="margin-top: 30px; opacity: 0.8;">
                    Find your bot on Telegram and start sharing files!
                </p>
            </div>
        </body>
    </html>
    '''

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'file-saver-bot'}

def run():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

if __name__ == '__main__':
    run()

from flask import Flask
from threading import Thread
import time

app = Flask('')

@app.route('/')
def home():
    return "🎮 League Randomizer Bot is running! ✅"

@app.route('/health')
def health():
    return "Bot is healthy and online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Start the Flask server in a separate thread"""
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("🔄 Keep-alive server started on port 8080")

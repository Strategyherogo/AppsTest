import os
import threading
from flask import Flask
from mention_tracker import handler

# Create a simple Flask app for health checks
app = Flask(__name__)

@app.route('/health')
def health_check():
    return 'OK', 200

def run_bot():
    """Run the Slack bot in a separate thread"""
    handler.start()

if __name__ == "__main__":
    # Start the bot in a background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Run Flask for health checks
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
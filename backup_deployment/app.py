"""
RouteForce Routing Application (Backup Deployment)
Standalone backup app for test and regression purposes.
"""

import os
from flask import Flask
from flask_socketio import SocketIO

# Create application instance
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

@app.route("/")
def index():
    return "Backup Deployment App Running"

if __name__ == "__main__":
    # Development server with WebSocket support
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        debug=True,
    )

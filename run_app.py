#!/usr/bin/env python3
"""
RouteForce Routing Application Runner
Uses the app factory pattern for proper initialization
"""

import os
import sys
from app import create_app, socketio


def main():
    """Main application entry point"""
    # Get configuration from environment
    config_name = os.environ.get("FLASK_ENV", "development")

    # Create the application instance
    app = create_app(config_name)

    # Get port from environment; default 5000 (dev) / 8000 (prod)
    default_port = 8000 if config_name == "production" else 5000
    port = int(os.environ.get("PORT", default_port))

    print(f"🚀 Starting RouteForce Routing Server")
    print(f"📍 Environment: {config_name}")
    print(f"🌐 Port: {port}")
    print(f"🔗 URL: http://localhost:{port}")

    try:
        # Use SocketIO development server for WebSocket support
        socketio.run(
            app,
            host="0.0.0.0",
            port=port,
            debug=(config_name == "development"),
            use_reloader=True,
            allow_unsafe_werkzeug=True,
        )
    except KeyboardInterrupt:
        print("\n👋 Server shutdown requested")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

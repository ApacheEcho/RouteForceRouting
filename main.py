
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from config import Config
from sentry_config import init_sentry
from models.db import init_db
from routes.user_routes import user_bp

def create_app():
    # Initialize the Flask application
    app = Flask(__name__)

    # Load configuration settings
    app.config.from_object(Config)

    # Initialize Sentry monitoring
    init_sentry(app)

    # Initialize database connection
    init_db(app)

    # Register user-related routes under '/api/users'
    app.register_blueprint(user_bp, url_prefix='/api/users')

    return app

if __name__ == '__main__':
    # Run the app on all network interfaces at port 5000
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
import logging
import secrets
from flask import Flask

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    """
    Application factory function
    """
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(16)  # Generate a random secret key for sessions
    
    # Register routes
    from app.routes import register_routes
    register_routes(app)
    
    logger.info("Flask application initialized")
    return app
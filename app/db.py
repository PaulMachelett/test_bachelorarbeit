import logging
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mock database for testing
mock_users = [
    {"id": 1, "name": "admin", "email": "admin@example.com", "password": "admin123", "admin": True},
    {"id": 2, "name": "user", "email": "user@example.com", "password": "user123", "admin": False}
]

mock_notes = [
    {"id": 1, "title": "Admin Note", "content": "This is an admin note", "owner_id": 1},
    {"id": 2, "title": "User Note", "content": "This is a user note", "owner_id": 2}
]

def get_db_connection():
    """
    Mock function to simulate database connection
    In a real application, this would connect to SQLite
    """
    logger.info("Getting database connection")
    return None

def close_db_connection(conn):
    """
    Mock function to simulate closing database connection
    """
    logger.info("Closing database connection")
    return None
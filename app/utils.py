import logging
import secrets
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def generate_token():
    """
    Generate a secure token for user sessions
    """
    return secrets.token_hex(16)

def get_current_timestamp():
    """
    Get the current timestamp in ISO format
    """
    return datetime.now().isoformat()

def validate_request_data(data, required_fields):
    """
    Validate that the request data contains all required fields
    """
    if not data:
        return False
    
    return all(field in data for field in required_fields)
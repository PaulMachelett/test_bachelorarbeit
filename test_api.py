import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:12001/api"

def print_response(response):
    """Print the response in a formatted way"""
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_api():
    """Test the API endpoints"""
    # Check API status
    print("Checking API status...")
    response = requests.get(f"{BASE_URL}/status")
    print_response(response)
    
    # Register a new user
    print("Registering a new user...")
    register_data = {
        "name": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/register", json=register_data)
    print_response(response)
    
    # Login with the new user
    print("Logging in...")
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print_response(response)
    
    # Save the token for authenticated requests
    token = response.json().get("token")
    cookies = response.cookies
    
    # Create a new note
    print("Creating a new note...")
    note_data = {
        "title": "Test Note",
        "content": "This is a test note created by the API test script."
    }
    response = requests.post(f"{BASE_URL}/notes", json=note_data, cookies=cookies)
    print_response(response)
    
    # Get the note ID from the response
    note_id = response.json().get("note_id")
    
    # Get all notes
    print("Getting all notes...")
    response = requests.get(f"{BASE_URL}/notes", cookies=cookies)
    print_response(response)
    
    # Get a specific note
    print(f"Getting note with ID {note_id}...")
    response = requests.get(f"{BASE_URL}/notes/{note_id}", cookies=cookies)
    print_response(response)
    
    # Update the note
    print(f"Updating note with ID {note_id}...")
    update_data = {
        "title": "Updated Test Note",
        "content": "This note has been updated."
    }
    response = requests.put(f"{BASE_URL}/notes/{note_id}", json=update_data, cookies=cookies)
    print_response(response)
    
    # Delete the note
    print(f"Deleting note with ID {note_id}...")
    response = requests.delete(f"{BASE_URL}/notes/{note_id}", cookies=cookies)
    print_response(response)
    
    # Try to login as admin
    print("Logging in as admin...")
    admin_login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/login", json=admin_login_data)
    print_response(response)
    
    # Get admin cookies
    admin_cookies = response.cookies
    
    # Get all users (admin only)
    print("Getting all users (admin only)...")
    response = requests.get(f"{BASE_URL}/admin/users", cookies=admin_cookies)
    print_response(response)
    
    # Logout
    print("Logging out...")
    response = requests.post(f"{BASE_URL}/logout", cookies=admin_cookies)
    print_response(response)

if __name__ == "__main__":
    test_api()
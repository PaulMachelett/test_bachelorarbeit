import pytest
import json
from app import create_app
from app.db import mock_users, mock_notes

@pytest.fixture
def client():
    """Create a test client for the app."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    
    # Reset mock data before each test
    mock_users.clear()
    mock_users.extend([
        {"id": 1, "name": "admin", "email": "admin@example.com", "password": "admin123", "admin": True},
        {"id": 2, "name": "user", "email": "user@example.com", "password": "user123", "admin": False}
    ])
    
    mock_notes.clear()
    mock_notes.extend([
        {"id": 1, "title": "Admin Note", "content": "This is an admin note", "owner_id": 1},
        {"id": 2, "title": "User Note", "content": "This is a user note", "owner_id": 2}
    ])
    
    with app.test_client() as client:
        yield client

# Test user registration
def test_register_success(client):
    """Test successful user registration."""
    response = client.post('/api/register', 
                          json={
                              'name': 'testuser',
                              'email': 'test@example.com',
                              'password': 'password123'
                          })
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert 'message' in data
    assert 'user_id' in data
    assert data['message'] == 'User registered successfully'
    assert data['user_id'] == 3  # Should be the third user

def test_register_missing_fields(client):
    """Test registration with missing fields."""
    response = client.post('/api/register', 
                          json={
                              'name': 'incomplete',
                              'email': 'incomplete@example.com'
                              # Missing password
                          })
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert 'error' in data
    assert data['error'] == 'Missing required fields'

def test_register_duplicate_email(client):
    """Test registration with an email that already exists."""
    response = client.post('/api/register', 
                          json={
                              'name': 'duplicate',
                              'email': 'admin@example.com',  # Already exists
                              'password': 'password123'
                          })
    data = json.loads(response.data)
    
    assert response.status_code == 409
    assert 'error' in data
    assert data['error'] == 'Email already exists'

def test_register_duplicate_username(client):
    """Test registration with a username that already exists."""
    response = client.post('/api/register', 
                          json={
                              'name': 'admin',  # Already exists
                              'email': 'new@example.com',
                              'password': 'password123'
                          })
    data = json.loads(response.data)
    
    assert response.status_code == 409
    assert 'error' in data
    assert data['error'] == 'Username already exists'

# Test user login
def test_login_success(client):
    """Test successful login."""
    response = client.post('/api/login', 
                          json={
                              'email': 'user@example.com',
                              'password': 'user123'
                          })
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'message' in data
    assert 'user_id' in data
    assert 'name' in data
    assert 'is_admin' in data
    assert 'token' in data
    assert data['message'] == 'Login successful'
    assert data['user_id'] == 2
    assert data['name'] == 'user'
    assert data['is_admin'] is False

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post('/api/login', 
                          json={
                              'email': 'user@example.com',
                              'password': 'wrongpassword'
                          })
    data = json.loads(response.data)
    
    assert response.status_code == 401
    assert 'error' in data
    assert data['error'] == 'Invalid credentials'

def test_login_missing_fields(client):
    """Test login with missing fields."""
    response = client.post('/api/login', 
                          json={
                              'email': 'user@example.com'
                              # Missing password
                          })
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert 'error' in data
    assert data['error'] == 'Missing required fields'

# Test note creation
def test_create_note_success(client):
    """Test successful note creation."""
    # First login to get session
    login_response = client.post('/api/login', 
                                json={
                                    'email': 'user@example.com',
                                    'password': 'user123'
                                })
    
    # Then create a note
    response = client.post('/api/notes', 
                          json={
                              'title': 'Test Note',
                              'content': 'This is a test note.'
                          })
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert 'message' in data
    assert 'note_id' in data
    assert 'title' in data
    assert 'content' in data
    assert 'owner_id' in data
    assert data['message'] == 'Note created successfully'
    assert data['note_id'] == 3  # Should be the third note
    assert data['title'] == 'Test Note'
    assert data['content'] == 'This is a test note.'
    assert data['owner_id'] == 2  # User ID from login

def test_create_note_unauthorized(client):
    """Test note creation without login."""
    response = client.post('/api/notes', 
                          json={
                              'title': 'Unauthorized Note',
                              'content': 'This should fail.'
                          })
    data = json.loads(response.data)
    
    assert response.status_code == 401
    assert 'error' in data
    assert data['error'] == 'Unauthorized'

def test_create_note_missing_fields(client):
    """Test note creation with missing fields."""
    # First login
    login_response = client.post('/api/login', 
                                json={
                                    'email': 'user@example.com',
                                    'password': 'user123'
                                })
    
    # Then try to create an incomplete note
    response = client.post('/api/notes', 
                          json={
                              'title': 'Incomplete Note'
                              # Missing content
                          })
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert 'error' in data
    assert data['error'] == 'Missing required fields'

# Test getting notes
def test_get_notes_success(client):
    """Test successfully getting all notes for a user."""
    # First login
    login_response = client.post('/api/login', 
                                json={
                                    'email': 'user@example.com',
                                    'password': 'user123'
                                })
    
    # Then get notes
    response = client.get('/api/notes')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'notes' in data
    assert len(data['notes']) == 1  # User should have 1 note
    assert data['notes'][0]['id'] == 2
    assert data['notes'][0]['title'] == 'User Note'
    assert data['notes'][0]['owner_id'] == 2

def test_get_notes_unauthorized(client):
    """Test getting notes without login."""
    response = client.get('/api/notes')
    data = json.loads(response.data)
    
    assert response.status_code == 401
    assert 'error' in data
    assert data['error'] == 'Unauthorized'

def test_get_specific_note_success(client):
    """Test successfully getting a specific note."""
    # First login
    login_response = client.post('/api/login', 
                                json={
                                    'email': 'user@example.com',
                                    'password': 'user123'
                                })
    
    # Then get a specific note
    response = client.get('/api/notes/2')  # User's note
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'note' in data
    assert data['note']['id'] == 2
    assert data['note']['title'] == 'User Note'
    assert data['note']['content'] == 'This is a user note'
    assert data['note']['owner_id'] == 2

def test_get_specific_note_unauthorized(client):
    """Test getting a specific note without login."""
    response = client.get('/api/notes/1')
    data = json.loads(response.data)
    
    assert response.status_code == 401
    assert 'error' in data
    assert data['error'] == 'Unauthorized'

def test_get_specific_note_not_found(client):
    """Test getting a non-existent note."""
    # First login
    login_response = client.post('/api/login', 
                                json={
                                    'email': 'user@example.com',
                                    'password': 'user123'
                                })
    
    # Then try to get a non-existent note
    response = client.get('/api/notes/999')
    data = json.loads(response.data)
    
    assert response.status_code == 404
    assert 'error' in data
    assert data['error'] == 'Note not found'

def test_get_specific_note_forbidden(client):
    """Test getting another user's note."""
    # First login as regular user
    login_response = client.post('/api/login', 
                                json={
                                    'email': 'user@example.com',
                                    'password': 'user123'
                                })
    
    # Then try to get admin's note
    response = client.get('/api/notes/1')  # Admin's note
    data = json.loads(response.data)
    
    assert response.status_code == 403
    assert 'error' in data
    assert data['error'] == 'Unauthorized'

# Test admin access
def test_admin_get_all_users(client):
    """Test admin getting all users."""
    # Login as admin
    login_response = client.post('/api/login', 
                                json={
                                    'email': 'admin@example.com',
                                    'password': 'admin123'
                                })
    
    # Get all users
    response = client.get('/api/admin/users')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'users' in data
    assert len(data['users']) == 2  # Should be 2 users
    # Check that passwords are not included
    assert 'password' not in data['users'][0]
    assert 'password' not in data['users'][1]

def test_non_admin_get_all_users(client):
    """Test non-admin trying to get all users."""
    # Login as regular user
    login_response = client.post('/api/login', 
                                json={
                                    'email': 'user@example.com',
                                    'password': 'user123'
                                })
    
    # Try to get all users
    response = client.get('/api/admin/users')
    data = json.loads(response.data)
    
    assert response.status_code == 403
    assert 'error' in data
    assert data['error'] == 'Unauthorized'
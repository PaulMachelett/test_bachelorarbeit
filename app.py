from flask import Flask, request, jsonify, session
import sqlite3
import logging
import os
import json
from datetime import datetime
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key for sessions

# Mock database for testing
mock_users = [
    {"id": 1, "name": "admin", "email": "admin@example.com", "password": "admin123", "admin": True},
    {"id": 2, "name": "user", "email": "user@example.com", "password": "user123", "admin": False}
]

mock_notes = [
    {"id": 1, "title": "Admin Note", "content": "This is an admin note", "owner_id": 1},
    {"id": 2, "title": "User Note", "content": "This is a user note", "owner_id": 2}
]

# Mock database functions
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

def query_db(query, args=(), one=False):
    """
    Mock function to simulate database queries
    """
    logger.info(f"Executing query: {query} with args: {args}")
    
    # Mock implementation for different query types
    if "SELECT * FROM users WHERE" in query:
        if "email" in query:
            email = args[0]
            user = next((u for u in mock_users if u["email"] == email), None)
            return user if one else [user] if user else []
        elif "name" in query:
            name = args[0]
            user = next((u for u in mock_users if u["name"] == name), None)
            return user if one else [user] if user else []
        elif "id" in query:
            user_id = args[0]
            user = next((u for u in mock_users if u["id"] == user_id), None)
            return user if one else [user] if user else []
    
    elif "SELECT * FROM notes WHERE" in query:
        if "owner_id" in query:
            owner_id = args[0]
            notes = [n for n in mock_notes if n["owner_id"] == owner_id]
            return notes[0] if one and notes else notes if not one else None
        elif "id" in query:
            note_id = args[0]
            note = next((n for n in mock_notes if n["id"] == note_id), None)
            return note if one else [note] if note else []
    
    elif "INSERT INTO users" in query:
        # Mock user creation
        new_id = max([u["id"] for u in mock_users]) + 1 if mock_users else 1
        new_user = {
            "id": new_id,
            "name": args[0],
            "email": args[1],
            "password": args[2],
            "admin": args[3]
        }
        mock_users.append(new_user)
        logger.info(f"Created new user: {new_user}")
        return new_id
    
    elif "INSERT INTO notes" in query:
        # Mock note creation
        new_id = max([n["id"] for n in mock_notes]) + 1 if mock_notes else 1
        new_note = {
            "id": new_id,
            "title": args[0],
            "content": args[1],
            "owner_id": args[2]
        }
        mock_notes.append(new_note)
        logger.info(f"Created new note: {new_note}")
        return new_id
    
    elif "UPDATE notes SET" in query:
        # Mock note update
        note_id = args[-1]
        note = next((n for n in mock_notes if n["id"] == note_id), None)
        if note:
            if len(args) == 3:  # Both title and content updated
                note["title"] = args[0]
                note["content"] = args[1]
            elif "title" in query:
                note["title"] = args[0]
            elif "content" in query:
                note["content"] = args[0]
            logger.info(f"Updated note: {note}")
            return True
        return False
    
    elif "DELETE FROM notes WHERE" in query:
        # Mock note deletion
        note_id = args[0]
        note_index = next((i for i, n in enumerate(mock_notes) if n["id"] == note_id), None)
        if note_index is not None:
            deleted_note = mock_notes.pop(note_index)
            logger.info(f"Deleted note: {deleted_note}")
            return True
        return False
    
    elif "DELETE FROM users WHERE" in query:
        # Mock user deletion
        user_id = args[0]
        user_index = next((i for i, u in enumerate(mock_users) if u["id"] == user_id), None)
        if user_index is not None:
            deleted_user = mock_users.pop(user_index)
            # Also delete all notes owned by this user
            mock_notes[:] = [n for n in mock_notes if n["owner_id"] != user_id]
            logger.info(f"Deleted user: {deleted_user}")
            return True
        return False
    
    elif "SELECT * FROM users" in query:
        # Return all users
        return mock_users
    
    elif "SELECT * FROM notes" in query:
        # Return all notes
        return mock_notes
    
    return []

# User routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['name', 'email', 'password']):
        logger.warning("Registration failed: Missing required fields")
        return jsonify({"error": "Missing required fields"}), 400
    
    # Check if user already exists
    existing_user = query_db("SELECT * FROM users WHERE email = ?", (data['email'],), one=True)
    if existing_user:
        logger.warning(f"Registration failed: Email {data['email']} already exists")
        return jsonify({"error": "Email already exists"}), 409
    
    existing_name = query_db("SELECT * FROM users WHERE name = ?", (data['name'],), one=True)
    if existing_name:
        logger.warning(f"Registration failed: Username {data['name']} already exists")
        return jsonify({"error": "Username already exists"}), 409
    
    # Create new user (default non-admin)
    user_id = query_db(
        "INSERT INTO users (name, email, password, admin) VALUES (?, ?, ?, ?)",
        (data['name'], data['email'], data['password'], False)
    )
    
    logger.info(f"User registered successfully: {data['name']}")
    return jsonify({"message": "User registered successfully", "user_id": user_id}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['email', 'password']):
        logger.warning("Login failed: Missing required fields")
        return jsonify({"error": "Missing required fields"}), 400
    
    # Check user credentials
    user = query_db("SELECT * FROM users WHERE email = ?", (data['email'],), one=True)
    
    if not user or user['password'] != data['password']:
        logger.warning(f"Login failed: Invalid credentials for {data.get('email', 'unknown')}")
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Create session
    session['user_id'] = user['id']
    session['is_admin'] = user['admin']
    
    logger.info(f"User logged in: {user['name']}")
    return jsonify({
        "message": "Login successful",
        "user_id": user['id'],
        "name": user['name'],
        "is_admin": user['admin'],
        "token": secrets.token_hex(16)  # Simple session token
    }), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    logger.info("User logged out")
    return jsonify({"message": "Logout successful"}), 200

# Note routes
@app.route('/api/notes', methods=['GET'])
def get_notes():
    if 'user_id' not in session:
        logger.warning("Unauthorized access attempt to notes")
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    notes = query_db("SELECT * FROM notes WHERE owner_id = ?", (user_id,))
    
    logger.info(f"Retrieved {len(notes)} notes for user {user_id}")
    return jsonify({"notes": notes}), 200

@app.route('/api/notes', methods=['POST'])
def create_note():
    if 'user_id' not in session:
        logger.warning("Unauthorized attempt to create note")
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    
    if not data or not all(k in data for k in ['title', 'content']):
        logger.warning("Note creation failed: Missing required fields")
        return jsonify({"error": "Missing required fields"}), 400
    
    user_id = session['user_id']
    note_id = query_db(
        "INSERT INTO notes (title, content, owner_id) VALUES (?, ?, ?)",
        (data['title'], data['content'], user_id)
    )
    
    logger.info(f"Note created: {data['title']} by user {user_id}")
    return jsonify({
        "message": "Note created successfully",
        "note_id": note_id,
        "title": data['title'],
        "content": data['content'],
        "owner_id": user_id
    }), 201

@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    if 'user_id' not in session:
        logger.warning("Unauthorized access attempt to note")
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id1 = session['user_id']
    note = query_db("SELECT * FROM notes WHERE id = ?", (note_id,), one=True)
    
    if not note:
        logger.warning(f"Note not found: {note_id}")
        return jsonify({"error": "Note not found"}), 404
    
    if note['owner_id'] != user_id and not session.get('is_admin', False):
        logger.warning(f"Unauthorized access attempt to note {note_id} by user {user_id}")
        return jsonify({"error": "Unauthorized"}), 403
    
    logger.info(f"Retrieved note {note_id} for user {user_id}")
    return jsonify({"note": note}), 200

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    if 'user_id' not in session:
        logger.warning("Unauthorized attempt to update note")
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    note = query_db("SELECT * FROM notes WHERE id = ?", (note_id,), one=True)
    
    if not note:
        logger.warning(f"Note not found for update: {note_id}")
        return jsonify({"error": "Note not found"}), 404
    
    if note['owner_id'] != user_id:
        logger.warning(f"Unauthorized update attempt for note {note_id} by user {user_id}")
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    
    if not data:
        logger.warning("Note update failed: No data provided")
        return jsonify({"error": "No data provided"}), 400
    
    # Update note fields
    if 'title' in data and 'content' in data:
        query_db(
            "UPDATE notes SET title = ?, content = ? WHERE id = ?",
            (data['title'], data['content'], note_id)
        )
    elif 'title' in data:
        query_db(
            "UPDATE notes SET title = ? WHERE id = ?",
            (data['title'], note_id)
        )
    elif 'content' in data:
        query_db(
            "UPDATE notes SET content = ? WHERE id = ?",
            (data['content'], note_id)
        )
    else:
        logger.warning("Note update failed: No valid fields to update")
        return jsonify({"error": "No valid fields to update"}), 400
    
    updated_note = query_db("SELECT * FROM notes WHERE id = ?", (note_id,), one=True)
    
    logger.info(f"Note updated: {note_id} by user {user_id}")
    return jsonify({"message": "Note updated successfully", "note": updated_note}), 200

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    if 'user_id' not in session:
        logger.warning("Unauthorized attempt to delete note")
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    note = query_db("SELECT * FROM notes WHERE id = ?", (note_id,), one=True)
    
    if not note:
        logger.warning(f"Note not found for deletion: {note_id}")
        return jsonify({"error": "Note not found"}), 404
    
    if note['owner_id'] != user_id and not session.get('is_admin', False):
        logger.warning(f"Unauthorized deletion attempt for note {note_id} by user {user_id}")
        return jsonify({"error": "Unauthorized"}), 403
    
    query_db("DELETE FROM notes WHERE id = ?", (note_id,))
    
    logger.info(f"Note deleted: {note_id} by user {user_id}")
    return jsonify({"message": "Note deleted successfully"}), 200

# Admin routes
@app.route('/api/admin/users', methods=['GET'])
def get_users():
    if 'user_id' not in session or not session.get('is_admin', False):
        logger.warning("Unauthorized access attempt to admin users list")
        return jsonify({"error": "Unauthorized"}), 403
    
    users = query_db("SELECT * FROM users")
    # Remove passwords from response
    for user in users:
        user.pop('password', None)
    
    logger.info(f"Admin retrieved user list, count: {len(users)}")
    return jsonify({"users": users}), 200

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if 'user_id' not in session or not session.get('is_admin', False):
        logger.warning("Unauthorized attempt to delete user")
        return jsonify({"error": "Unauthorized"}), 403
    
    # Prevent admin from deleting themselves
    if user_id == session['user_id']:
        logger.warning("Admin attempted to delete their own account")
        return jsonify({"error": "Cannot delete your own admin account"}), 400
    
    user = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    
    if not user:
        logger.warning(f"User not found for deletion: {user_id}")
        return jsonify({"error": "User not found"}), 404
    
    query_db("DELETE FROM users WHERE id = ?", (user_id,))
    
    logger.info(f"Admin deleted user: {user_id}")
    return jsonify({"message": "User deleted successfully"}), 200

# Status route
@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "user_count": len(mock_users),
        "note_count": len(mock_notes)
    }), 200

# Root route
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "message": "Welcome to Notes API",
        "version": "1.0.0",
        "endpoints": [
            "/api/register",
            "/api/login",
            "/api/logout",
            "/api/notes",
            "/api/notes/<id>",
            "/api/admin/users",
            "/api/admin/users/<id>",
            "/api/status"
        ]
    }), 200

if __name__ == '__main__':
    logger.info("Starting Notes API server")
    app.run(host='0.0.0.0', port=12001, debug=True)

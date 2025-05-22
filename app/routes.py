from flask import request, jsonify, session
import logging
import secrets
from datetime import datetime
from app.crud import query_db
from app.db import mock_users, mock_notes

# Configure logging
logger = logging.getLogger(__name__)

def register_routes(app):
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
        
        user_id = session['user_id']
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
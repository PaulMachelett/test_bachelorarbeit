import logging
from app.db import mock_users, mock_notes

# Configure logging
logger = logging.getLogger(__name__)

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
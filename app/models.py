# This file would normally contain SQLAlchemy models or other ORM definitions
# For this mock application, we'll define the structure of our data models

class User:
    """
    User model structure
    """
    def __init__(self, id, name, email, password, admin=False):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.admin = admin

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "admin": self.admin
        }


class Note:
    """
    Note model structure
    """
    def __init__(self, id, title, content, owner_id):
        self.id = id
        self.title = title
        self.content = content
        self.owner_id = owner_id

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "owner_id": self.owner_id
        }
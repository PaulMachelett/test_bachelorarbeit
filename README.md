# Notes API

A simple Flask-based REST API for managing user notes.

## Features

- User registration and authentication
- Create, read, update, and delete notes
- Admin functionality to manage users
- Mock database implementation for testing

## API Endpoints

### Authentication

- `POST /api/register` - Register a new user
- `POST /api/login` - Login and receive a session token
- `POST /api/logout` - Logout and invalidate session

### Notes

- `GET /api/notes` - Get all notes for the logged-in user
- `POST /api/notes` - Create a new note
- `GET /api/notes/<id>` - Get a specific note
- `PUT /api/notes/<id>` - Update a specific note
- `DELETE /api/notes/<id>` - Delete a specific note

### Admin

- `GET /api/admin/users` - Get all users (admin only)
- `DELETE /api/admin/users/<id>` - Delete a user (admin only)

### System

- `GET /api/status` - Get API status
- `GET /` - API information

## Database Schema

### Users Table

- `id` (INTEGER, Primary Key, unique)
- `name` (TEXT, unique)
- `email` (TEXT, unique)
- `admin` (BOOLEAN)

### Notes Table

- `id` (INTEGER, Primary Key)
- `title` (TEXT)
- `content` (TEXT)
- `owner_id` (INTEGER, Foreign Key, references `users.id`)

## Running the Application

```bash
python app.py
```

The server will start on port 12000.
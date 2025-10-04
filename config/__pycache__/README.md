Document Management & User Management API

A FastAPI application for managing users and documents, with JWT authentication, role-based access control, and MongoDB as the database.

Features
User Management

User registration and login with JWT-based authentication.

Role-based access control (user and admin).

Retrieve current user profile.

Admin-only endpoints to list, update, and delete users.

Document Management

Upload documents with metadata extraction (file type, size, word count).

List documents (users: their own, admins: all).

Update document metadata.

Delete documents (including the physical file).

Download documents.


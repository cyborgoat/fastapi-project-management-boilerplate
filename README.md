# FastAPI Project Management Boilerplate

A modern, production-ready boilerplate for building project management applications using FastAPI with comprehensive user authentication, project management, and task tracking capabilities.

## Features

### ✅ Implemented

- **User Authentication & Authorization**
  - JWT token-based authentication
  - Dual login support (username or email)
  - Password hashing with bcrypt
  - OAuth2 with Password (and hashed) Bearer tokens
- **User Management**
  - User registration with username and email
  - User profile management
  - Active/inactive user status
- **Project Management**
  - CRUD operations for projects
  - Project ownership and access control
- **Task Management**
  - Task creation and assignment
  - Task status tracking
  - Task-project relationships
  - RESTful endpoint for project tasks (`/projects/{project_id}/tasks`)
- **Database & Migrations**
  - PostgreSQL database with Docker setup
  - Alembic migrations for schema management
  - SQLAlchemy ORM with relationship modeling
  - SQLite in-memory configuration for isolated test suite
- **API Documentation**
  - Automatic OpenAPI/Swagger documentation
  - Interactive API testing interface

### 🚧 Ready for Extension

- Comments system
- File uploads
- Advanced collaboration tools
- Role-based permissions
- Team management

## Tech Stack

- **Framework:** FastAPI 0.115.4
- **Package Management:** UV
- **Database:** PostgreSQL (Docker)
- **ORM:** SQLAlchemy 2.0+
- **Authentication:** OAuth2 + JWT
- **Password Hashing:** bcrypt
- **Migrations:** Alembic
- **Testing:** pytest (configured, 100% coverage, uses SQLite for isolation)
- **Data Validation:** Pydantic v2
- **Development:** Uvicorn with hot reload

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- UV package manager

### Installation

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd fastapi-project-management-boilerplate
   ```

2. **Set up Python environment**

   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start the database**

   ```bash
   docker-compose up -d
   ```

5. **Run database migrations**

   ```bash
   alembic upgrade head
   ```

6. **Start the development server**

   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
   ```

The API will be available at:

- **API:** <http://127.0.0.1:8001>
- **Interactive Docs:** <http://127.0.0.1:8001/docs>
- **Alternative Docs:** <http://127.0.0.1:8001/redoc>

## API Usage Examples

### User Registration

```bash
curl -X POST "http://127.0.0.1:8001/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com", 
    "password": "securepassword123"
  }'
```

### Login with Username

```bash
curl -X POST "http://127.0.0.1:8001/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=johndoe&password=securepassword123"
```

### Login with Email

```bash
curl -X POST "http://127.0.0.1:8001/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=securepassword123"
```

### Access Protected Endpoints

```bash
# Use the access_token from login response
curl -X GET "http://127.0.0.1:8001/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Project Structure

```text
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py           # API router
│   │       └── endpoints/       # API endpoints
│   │           ├── login.py     # Authentication endpoints
│   │           ├── users.py     # User management
│   │           ├── projects.py  # Project management
│   │           └── tasks.py     # Task management
│   ├── core/
│   │   ├── config.py           # App configuration
│   │   └── security.py         # Security utilities
│   ├── crud/                   # Database operations
│   │   ├── crud_user.py
│   │   ├── crud_project.py
│   │   └── crud_task.py
│   ├── db/
│   │   ├── base.py            # SQLAlchemy base
│   │   └── session.py         # Database session
│   ├── models/                # SQLAlchemy models
│   │   ├── user.py
│   │   ├── project.py
│   │   └── task.py
│   ├── schemas/              # Pydantic schemas
│   │   ├── user.py
│   │   ├── project.py
│   │   └── task.py
│   └── main.py              # FastAPI app instance
├── migrations/              # Alembic migrations
├── docker-compose.yml       # Database setup
├── alembic.ini             # Migration config
└── pyproject.toml          # Dependencies
```

## Development

### Database Operations

**Create a new migration:**

```bash
alembic revision --autogenerate -m "Description of changes"
```

**Apply migrations:**

```bash
alembic upgrade head
```

**Rollback migrations:**

```bash
alembic downgrade -1
```

### Testing
```bash
pytest app/tests/ -v
```
All 111 tests pass with 100% coverage.

### Code Quality

```bash
# Format code
uv run ruff format

# Lint code  
uv run ruff check
```

## Configuration

Key environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/projectmanagement

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Development
DEBUG=True
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

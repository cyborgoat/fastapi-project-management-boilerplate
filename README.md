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
  - **Role-based Access Control**
    - Superuser (full system access)
    - Admin (user management privileges)
    - Normal User (standard access)
  - **Default Superuser** automatically created from environment configuration
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
   uvicorn app.main:app --reload --port 8000
   ```

The API will be available at:

- **API:** <http://127.0.0.1:8000>
- **Interactive Docs:** <http://127.0.0.1:8000/docs>
- **Alternative Docs:** <http://127.0.0.1:8000/redoc>

## Database Management

### Fresh Start / Clean Database

If you need to start with a completely clean database (removes all data):

1. **Stop the application and database**
   ```bash
   # Stop the FastAPI application (Ctrl+C if running)
   # Stop and remove database containers
   docker-compose down
   ```

2. **Remove persistent database data**
   ```bash
   # Remove the Docker volume containing database data
   docker volume rm fastapi-project-management-boilerplate_postgres_data
   # Or remove all unused volumes
   docker volume prune
   ```

3. **Restart database and run migrations**
   ```bash
   # Start the database container
   docker-compose up -d
   
   # Run all migrations to create tables
   alembic upgrade head
   ```

4. **Start the application**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

The application will automatically create a default superuser with credentials from your `.env` file:
- **Username:** `admin` (or value from `FIRST_SUPERUSER_USERNAME`)
- **Email:** `admin@example.com` (or value from `FIRST_SUPERUSER_EMAIL`)
- **Password:** `admin123` (or value from `FIRST_SUPERUSER_PASSWORD`)

### Migration Troubleshooting

If you encounter database-related errors:

1. **Check if database container is running:**
   ```bash
   docker-compose ps
   ```

2. **Check current migration status:**
   ```bash
   alembic current
   ```

3. **View migration history:**
   ```bash
   alembic history
   ```

4. **Force migration to latest:**
   ```bash
   alembic upgrade head
   ```

## API Usage Examples

### User Registration

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com", 
    "password": "securepassword123"
  }'
```

### Login with Username

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=johndoe&password=securepassword123"
```

### Login with Email

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=securepassword123"
```

### Access Protected Endpoints

```bash
# Use the access_token from login response
curl -X GET "http://127.0.0.1:8000/api/v1/users/me" \
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

```

### Testing

```bash
pytest app/tests/ -v
```

All 125 tests pass with 100% coverage.

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
POSTGRES_USER=dbuser
POSTGRES_PASSWORD=dbpassword
POSTGRES_DB=project-management-db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# API
API_V1_STR=/api/v1

# Environment
ENVIRONMENT=development

# Default Superuser Configuration
FIRST_SUPERUSER_USERNAME=admin
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=admin123
FIRST_SUPERUSER_FULL_NAME=System Administrator
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

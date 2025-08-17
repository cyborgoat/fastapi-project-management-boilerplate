"""
Database initialization utilities.
"""
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.models import user, project, task  # Import all models to register them


def init_db(db: Session) -> None:
    """Initialize database with default superuser."""
    # Check if superuser already exists
    existing_user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
    if not existing_user:
        # Create default superuser
        new_user = crud.user.create_superuser(
            db,
            username=settings.FIRST_SUPERUSER_USERNAME,
            email=settings.FIRST_SUPERUSER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name=settings.FIRST_SUPERUSER_FULL_NAME,
        )
        print(f"Created default superuser: {new_user.username} ({new_user.email})")
    else:
        print(f"Default superuser already exists: {existing_user.username} ({existing_user.email})")

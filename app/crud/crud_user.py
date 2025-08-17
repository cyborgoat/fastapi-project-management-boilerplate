from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserStatusUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get a user by email."""
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """Get a user by username."""
        return db.query(User).filter(User.username == username).first()

    def get_by_email_or_username(self, db: Session, *, identifier: str) -> Optional[User]:
        """Get a user by email or username."""
        return db.query(User).filter(
            (User.email == identifier) | (User.username == identifier)
        ).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=True,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_superuser(
        self, db: Session, *, username: str, email: str, password: str, full_name: Optional[str] = None
    ) -> User:
        """Create a superuser."""
        db_obj = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_superuser=True,
            is_admin=True,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_user_status(
        self, db: Session, *, db_obj: User, obj_in: UserStatusUpdate
    ) -> User:
        """Update user status (admin/superuser privileges)."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(
        self, db: Session, *, identifier: str, password: str
    ) -> Optional[User]:
        """Authenticate a user by email or username."""
        user = self.get_by_email_or_username(db, identifier=identifier)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """Check if the user is active."""
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        """Check if the user is a superuser."""
        return user.is_superuser

    def is_admin(self, user: User) -> bool:
        """Check if the user is an admin."""
        return user.is_admin

    def can_manage_users(self, user: User) -> bool:
        """Check if the user can manage other users (admin or superuser)."""
        return user.is_superuser or user.is_admin


user = CRUDUser(User)

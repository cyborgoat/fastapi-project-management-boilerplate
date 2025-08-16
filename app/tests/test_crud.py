from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.security import get_password_hash


class TestUserCRUD:
    """Test user CRUD operations."""

    def test_create_user(self, db_session: Session):
        """Test creating a user via CRUD."""
        user_data = schemas.UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        user = crud.user.create(db_session, obj_in=user_data)

        assert user.username == user_data.username
        assert user.email == user_data.email
        assert user.is_active is True
        assert hasattr(user, 'hashed_password')
        assert user.hashed_password != user_data.password  # Should be hashed

    def test_get_user_by_id(self, db_session: Session):
        """Test getting user by ID."""
        user_data = schemas.UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        created_user = crud.user.create(db_session, obj_in=user_data)
        retrieved_user = crud.user.get(db_session, id=created_user.id)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == user_data.username
        assert retrieved_user.email == user_data.email

    def test_get_user_by_email(self, db_session: Session):
        """Test getting user by email."""
        user_data = schemas.UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        created_user = crud.user.create(db_session, obj_in=user_data)
        retrieved_user = crud.user.get_by_email(db_session, email=user_data.email)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == user_data.email

    def test_get_user_by_username(self, db_session: Session):
        """Test getting user by username."""
        user_data = schemas.UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        created_user = crud.user.create(db_session, obj_in=user_data)
        retrieved_user = crud.user.get_by_username(db_session, username=user_data.username)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == user_data.username

    def test_get_user_by_email_or_username_with_email(self, db_session: Session):
        """Test getting user by email using the dual method."""
        user_data = schemas.UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        created_user = crud.user.create(db_session, obj_in=user_data)
        retrieved_user = crud.user.get_by_email_or_username(db_session, identifier=user_data.email)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == user_data.email

    def test_get_user_by_email_or_username_with_username(self, db_session: Session):
        """Test getting user by username using the dual method."""
        user_data = schemas.UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        created_user = crud.user.create(db_session, obj_in=user_data)
        retrieved_user = crud.user.get_by_email_or_username(db_session, identifier=user_data.username)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == user_data.username

    def test_authenticate_user_with_username(self, db_session: Session):
        """Test user authentication with username."""
        user_data = schemas.UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        created_user = crud.user.create(db_session, obj_in=user_data)
        authenticated_user = crud.user.authenticate(
            db_session,
            identifier=user_data.username,
            password=user_data.password
        )

        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id

    def test_authenticate_user_with_email(self, db_session: Session):
        """Test user authentication with email."""
        user_data = schemas.UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        created_user = crud.user.create(db_session, obj_in=user_data)
        authenticated_user = crud.user.authenticate(
            db_session,
            identifier=user_data.email,
            password=user_data.password
        )

        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id

    def test_authenticate_user_wrong_password(self, db_session: Session):
        """Test authentication fails with wrong password."""
        user_data = schemas.UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        crud.user.create(db_session, obj_in=user_data)
        authenticated_user = crud.user.authenticate(
            db_session,
            identifier=user_data.username,
            password="wrongpassword"
        )

        assert authenticated_user is None

    def test_authenticate_user_nonexistent(self, db_session: Session):
        """Test authentication fails for nonexistent user."""
        authenticated_user = crud.user.authenticate(
            db_session,
            identifier="nonexistent",
            password="password"
        )

        assert authenticated_user is None

    def test_update_user(self, db_session: Session):
        """Test updating user information."""
        user_data = schemas.UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        created_user = crud.user.create(db_session, obj_in=user_data)

        update_data = schemas.UserUpdate(
            username="updateduser",
            email="updated@example.com"
        )

        updated_user = crud.user.update(db_session, db_obj=created_user, obj_in=update_data)

        assert updated_user.username == update_data.username
        assert updated_user.email == update_data.email
        assert updated_user.id == created_user.id

    def test_delete_user(self, db_session: Session):
        """Test deleting user."""
        user_data = schemas.UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        created_user = crud.user.create(db_session, obj_in=user_data)
        user_id = created_user.id

        deleted_user = crud.user.remove(db_session, id=user_id)

        assert deleted_user is not None
        assert deleted_user.id == user_id

        # Verify user is actually deleted
        retrieved_user = crud.user.get(db_session, id=user_id)
        assert retrieved_user is None

    def test_get_multi_users(self, db_session: Session):
        """Test getting multiple users."""
        # Create multiple users
        for i in range(3):
            user_data = schemas.UserCreate(
                username=f"testuser{i}",
                email=f"test{i}@example.com",
                password="testpassword123"
            )
            crud.user.create(db_session, obj_in=user_data)

        users = crud.user.get_multi(db_session)

        assert len(users) >= 3  # At least the 3 we created

    def test_is_active_user(self, db_session: Session):
        """Test checking if user is active."""
        user_data = schemas.UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        created_user = crud.user.create(db_session, obj_in=user_data)

        assert crud.user.is_active(created_user) is True

    def test_is_superuser(self, db_session: Session):
        """Test checking if user is superuser."""
        user_data = schemas.UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        created_user = crud.user.create(db_session, obj_in=user_data)

        # Assuming users are not superusers by default
        assert crud.user.is_superuser(created_user) is False


class TestPasswordSecurity:
    """Test password hashing and verification."""

    def test_password_hashing(self):
        """Test that passwords are properly hashed."""
        password = "testpassword123"
        hashed_password = get_password_hash(password)

        assert hashed_password != password
        assert len(hashed_password) > 0

    def test_password_verification(self):
        """Test password verification."""
        from app.core.security import verify_password

        password = "testpassword123"
        hashed_password = get_password_hash(password)

        # Correct password should verify
        assert verify_password(password, hashed_password) is True

        # Wrong password should not verify
        assert verify_password("wrongpassword", hashed_password) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password generates different hashes (due to salt)."""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different due to salt
        assert hash1 != hash2

        # But both should verify the original password
        from app.core.security import verify_password
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

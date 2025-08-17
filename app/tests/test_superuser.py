import pytest
from fastapi.testclient import TestClient


class TestSuperuserFunctionality:
    """Test superuser and admin functionality."""

    @pytest.fixture
    def superuser_data(self):
        """Test data for creating a superuser."""
        return {
            "username": "superuser",
            "email": "superuser@example.com",
            "password": "superpass123",
            "full_name": "Super User"
        }

    @pytest.fixture
    def admin_data(self):
        """Test data for creating an admin."""
        return {
            "username": "admin_user",
            "email": "admin_user@example.com", 
            "password": "adminpass123",
            "full_name": "Admin User"
        }

    @pytest.fixture
    def superuser_headers(self, client: TestClient, db_session, test_settings_fixture):
        """Get authentication headers for a test superuser."""
        from app import crud
        
        # Create superuser in test database using test settings
        superuser = crud.user.create_superuser(
            db_session,
            username=test_settings_fixture.FIRST_SUPERUSER_USERNAME,
            email=test_settings_fixture.FIRST_SUPERUSER_EMAIL,
            password=test_settings_fixture.FIRST_SUPERUSER_PASSWORD,
            full_name=test_settings_fixture.FIRST_SUPERUSER_FULL_NAME,
        )
        
        # Login as superuser
        login_data = {
            "username": test_settings_fixture.FIRST_SUPERUSER_USERNAME,
            "password": test_settings_fixture.FIRST_SUPERUSER_PASSWORD
        }
        response = client.post(
            "/api/v1/login/access-token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
        return None

    def test_default_superuser_created(self, client: TestClient, db_session, test_settings_fixture):
        """Test that default superuser can be created and works correctly."""
        from app import crud
        
        # Create superuser in test database using test settings
        superuser = crud.user.create_superuser(
            db_session,
            username=test_settings_fixture.FIRST_SUPERUSER_USERNAME,
            email=test_settings_fixture.FIRST_SUPERUSER_EMAIL,
            password=test_settings_fixture.FIRST_SUPERUSER_PASSWORD,
            full_name=test_settings_fixture.FIRST_SUPERUSER_FULL_NAME,
        )
        
        # Try to login with superuser credentials
        login_data = {
            "username": test_settings_fixture.FIRST_SUPERUSER_USERNAME,
            "password": test_settings_fixture.FIRST_SUPERUSER_PASSWORD
        }
        response = client.post(
            "/api/v1/login/access-token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_default_superuser_has_correct_roles(self, client: TestClient, superuser_headers, test_settings_fixture):
        """Test that default superuser has correct roles."""
        if not superuser_headers:
            pytest.skip("Could not authenticate as superuser")
            
        response = client.get("/api/v1/users/me", headers=superuser_headers)
        assert response.status_code == 200
        
        user_data = response.json()
        assert user_data["username"] == test_settings_fixture.FIRST_SUPERUSER_USERNAME
        assert user_data["email"] == test_settings_fixture.FIRST_SUPERUSER_EMAIL
        assert user_data["full_name"] == test_settings_fixture.FIRST_SUPERUSER_FULL_NAME
        assert user_data["is_superuser"] is True
        assert user_data["is_admin"] is True
        assert user_data["is_active"] is True

    def test_create_user_with_full_name(self, client: TestClient, superuser_data):
        """Test creating user with full name."""
        response = client.post("/api/v1/users/", json=superuser_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["username"] == superuser_data["username"]
        assert data["email"] == superuser_data["email"]
        assert data["full_name"] == superuser_data["full_name"]
        assert data["is_active"] is True
        assert data["is_admin"] is False
        assert data["is_superuser"] is False

    def test_superuser_can_update_user_status(self, client: TestClient, superuser_headers, superuser_data):
        """Test that superuser can update user status."""
        if not superuser_headers:
            pytest.skip("Could not authenticate as superuser")

        # Create a regular user
        user_response = client.post("/api/v1/users/", json=superuser_data)
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        # Update user to admin
        status_update = {"is_admin": True}
        response = client.put(
            f"/api/v1/users/{user_id}/status",
            json=status_update,
            headers=superuser_headers
        )
        assert response.status_code == 200
        
        updated_user = response.json()
        assert updated_user["is_admin"] is True
        assert updated_user["is_superuser"] is False

    def test_superuser_can_create_superuser(self, client: TestClient, superuser_headers, admin_data):
        """Test that superuser can grant superuser privileges."""
        if not superuser_headers:
            pytest.skip("Could not authenticate as superuser")

        # Create a regular user
        user_response = client.post("/api/v1/users/", json=admin_data)
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        # Grant superuser privileges
        status_update = {"is_superuser": True}
        response = client.put(
            f"/api/v1/users/{user_id}/status",
            json=status_update,
            headers=superuser_headers
        )
        assert response.status_code == 200
        
        updated_user = response.json()
        assert updated_user["is_superuser"] is True

    def test_superuser_can_deactivate_user(self, client: TestClient, superuser_headers, superuser_data):
        """Test that superuser can deactivate users."""
        if not superuser_headers:
            pytest.skip("Could not authenticate as superuser")

        # Create a regular user
        user_response = client.post("/api/v1/users/", json=superuser_data)
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        # Deactivate user
        status_update = {"is_active": False}
        response = client.put(
            f"/api/v1/users/{user_id}/status",
            json=status_update,
            headers=superuser_headers
        )
        assert response.status_code == 200
        
        updated_user = response.json()
        assert updated_user["is_active"] is False

    def test_normal_user_cannot_update_user_status(self, client: TestClient, test_user_data):
        """Test that normal users cannot update user status."""
        # Create user
        user_response = client.post("/api/v1/users/", json=test_user_data)
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        # Login as the user
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        login_response = client.post(
            "/api/v1/login/access-token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to update status
        status_update = {"is_admin": True}
        response = client.put(
            f"/api/v1/users/{user_id}/status",
            json=status_update,
            headers=headers
        )
        assert response.status_code == 403

    def test_admin_can_update_normal_user_status(self, client: TestClient, superuser_headers, admin_data, superuser_data):
        """Test that admin can update normal user status but not create superusers."""
        if not superuser_headers:
            pytest.skip("Could not authenticate as superuser")

        # Create admin user
        admin_response = client.post("/api/v1/users/", json=admin_data)
        assert admin_response.status_code == 200
        admin_id = admin_response.json()["id"]

        # Grant admin privileges using superuser
        status_update = {"is_admin": True}
        response = client.put(
            f"/api/v1/users/{admin_id}/status",
            json=status_update,
            headers=superuser_headers
        )
        assert response.status_code == 200

        # Login as admin
        login_data = {
            "username": admin_data["username"],
            "password": admin_data["password"]
        }
        admin_login_response = client.post(
            "/api/v1/login/access-token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        admin_token = admin_login_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Create regular user
        user_response = client.post("/api/v1/users/", json=superuser_data)
        assert user_response.status_code == 200
        user_id = user_response.json()["id"]

        # Admin can deactivate user
        status_update = {"is_active": False}
        response = client.put(
            f"/api/v1/users/{user_id}/status",
            json=status_update,
            headers=admin_headers
        )
        assert response.status_code == 200

        # Admin cannot create superuser
        status_update = {"is_superuser": True}
        response = client.put(
            f"/api/v1/users/{user_id}/status",
            json=status_update,
            headers=admin_headers
        )
        assert response.status_code == 403

    def test_superuser_cannot_modify_own_superuser_status(self, client: TestClient, superuser_headers):
        """Test that superuser cannot remove their own superuser privileges."""
        if not superuser_headers:
            pytest.skip("Could not authenticate as superuser")

        # Get current user ID
        me_response = client.get("/api/v1/users/me", headers=superuser_headers)
        user_id = me_response.json()["id"]

        # Try to remove own superuser privileges
        status_update = {"is_superuser": False}
        response = client.put(
            f"/api/v1/users/{user_id}/status",
            json=status_update,
            headers=superuser_headers
        )
        assert response.status_code == 400

    def test_update_user_status_unauthenticated(self, client: TestClient):
        """Test updating user status without authentication fails."""
        status_update = {"is_admin": True}
        response = client.put("/api/v1/users/1/status", json=status_update)
        assert response.status_code == 401

    def test_update_nonexistent_user_status(self, client: TestClient, superuser_headers):
        """Test updating status of non-existent user returns 404."""
        if not superuser_headers:
            pytest.skip("Could not authenticate as superuser")

        status_update = {"is_admin": True}
        response = client.put(
            "/api/v1/users/99999/status",
            json=status_update,
            headers=superuser_headers
        )
        assert response.status_code == 404


class TestUserFieldValidation:
    """Test additional user field validation."""

    def test_user_update_validation(self, client: TestClient, authenticated_headers):
        """Test validation when updating user information."""
        # Get current user
        me_response = client.get("/api/v1/users/me", headers=authenticated_headers)
        user_id = me_response.json()["id"]

        # Test invalid username update
        invalid_update = {
            "username": "",  # Invalid empty username
            "email": "valid@example.com"
        }
        response = client.put(
            f"/api/v1/users/{user_id}",
            json=invalid_update,
            headers=authenticated_headers
        )
        assert response.status_code == 422

        # Test invalid email update  
        invalid_update = {
            "username": "validusername",
            "email": "invalid-email"  # Invalid email format
        }
        response = client.put(
            f"/api/v1/users/{user_id}",
            json=invalid_update,
            headers=authenticated_headers
        )
        assert response.status_code == 422

    def test_full_name_field(self, client: TestClient):
        """Test that full_name field works correctly."""
        user_data = {
            "username": "testuser_fullname",
            "email": "fullname@example.com",
            "password": "password123",
            "full_name": "Test Full Name"
        }
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["full_name"] == "Test Full Name"

    def test_optional_full_name_field(self, client: TestClient):
        """Test that full_name field is optional."""
        user_data = {
            "username": "testuser_nofullname",
            "email": "nofullname@example.com",
            "password": "password123"
        }
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["full_name"] is None

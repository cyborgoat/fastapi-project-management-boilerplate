import pytest
from fastapi.testclient import TestClient


class TestUserEndpoints:
    """Test user management endpoints."""

    def test_get_users_list_authenticated(self, client: TestClient, authenticated_headers):
        """Test getting users list with authentication."""
        response = client.get("/api/v1/users/", headers=authenticated_headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the authenticated user

    def test_get_users_list_unauthenticated(self, client: TestClient):
        """Test getting users list without authentication fails."""
        response = client.get("/api/v1/users/")
        assert response.status_code == 401

    def test_get_user_by_id_success(self, client: TestClient, authenticated_headers):
        """Test getting a specific user by ID."""
        # First get current user to get their ID
        me_response = client.get("/api/v1/users/me", headers=authenticated_headers)
        assert me_response.status_code == 200
        user_id = me_response.json()["id"]

        # Get user by ID
        response = client.get(f"/api/v1/users/{user_id}", headers=authenticated_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == user_id
        assert "username" in data
        assert "email" in data

    def test_get_user_by_id_not_found(self, client: TestClient, authenticated_headers):
        """Test getting a non-existent user returns 404."""
        response = client.get("/api/v1/users/99999", headers=authenticated_headers)
        assert response.status_code == 404

    def test_get_user_by_id_unauthenticated(self, client: TestClient):
        """Test getting user by ID without authentication fails."""
        response = client.get("/api/v1/users/1")
        assert response.status_code == 401

    def test_update_user_success(self, client: TestClient, authenticated_headers):
        """Test updating user information."""
        # Get current user
        me_response = client.get("/api/v1/users/me", headers=authenticated_headers)
        user_id = me_response.json()["id"]

        # Update user
        update_data = {
            "username": "updated_username",
            "email": "updated@example.com"
        }
        response = client.put(
            f"/api/v1/users/{user_id}",
            json=update_data,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == update_data["username"]
        assert data["email"] == update_data["email"]

    def test_update_user_duplicate_username(self, client: TestClient, test_user_data):
        """Test updating user with duplicate username fails."""
        # Create first user
        user1_response = client.post("/api/v1/users/", json=test_user_data)
        assert user1_response.status_code == 200

        # Create second user
        user2_data = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "password123"
        }
        user2_response = client.post("/api/v1/users/", json=user2_data)
        assert user2_response.status_code == 200
        user2_id = user2_response.json()["id"]

        # Login as user2
        login_data = {
            "username": user2_data["username"],
            "password": user2_data["password"]
        }
        login_response = client.post(
            "/api/v1/login/access-token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to update user2's username to user1's username
        update_data = {
            "username": test_user_data["username"],  # Duplicate username
            "email": "newemail@example.com"
        }
        response = client.put(
            f"/api/v1/users/{user2_id}",
            json=update_data,
            headers=headers
        )

        assert response.status_code == 400

    def test_update_user_unauthenticated(self, client: TestClient):
        """Test updating user without authentication fails."""
        update_data = {
            "username": "newusername",
            "email": "new@example.com"
        }
        response = client.put("/api/v1/users/1", json=update_data)
        assert response.status_code == 401

    def test_delete_user_success(self, client: TestClient, authenticated_headers):
        """Test deleting user."""
        # Get current user
        me_response = client.get("/api/v1/users/me", headers=authenticated_headers)
        user_id = me_response.json()["id"]

        # Delete user
        response = client.delete(f"/api/v1/users/{user_id}", headers=authenticated_headers)
        assert response.status_code == 200

    def test_delete_user_not_found(self, client: TestClient, authenticated_headers):
        """Test deleting non-existent user returns 404."""
        response = client.delete("/api/v1/users/99999", headers=authenticated_headers)
        assert response.status_code == 404

    def test_delete_user_unauthenticated(self, client: TestClient):
        """Test deleting user without authentication fails."""
        response = client.delete("/api/v1/users/1")
        assert response.status_code == 401


class TestUserValidation:
    """Test user data validation."""

    @pytest.mark.parametrize("invalid_email", [
        "invalid-email",
        "@example.com",
        "user@",
        "user.example.com",
        "",
    ])
    def test_invalid_email_formats(self, client: TestClient, invalid_email):
        """Test various invalid email formats are rejected."""
        invalid_data = {
            "username": "testuser",
            "email": invalid_email,
            "password": "password123"
        }
        response = client.post("/api/v1/users/", json=invalid_data)
        assert response.status_code == 422

    @pytest.mark.parametrize("invalid_username", [
        "",
        " ",
        "a" * 101,  # Too long (assuming max length of 100)
    ])
    def test_invalid_username_formats(self, client: TestClient, invalid_username):
        """Test various invalid username formats are rejected."""
        invalid_data = {
            "username": invalid_username,
            "email": "test@example.com",
            "password": "password123"
        }
        response = client.post("/api/v1/users/", json=invalid_data)
        assert response.status_code == 422

    def test_missing_required_fields(self, client: TestClient):
        """Test that missing required fields are rejected."""
        test_cases = [
            {"email": "test@example.com", "password": "password123"},  # Missing username
            {"username": "testuser", "password": "password123"},      # Missing email
            {"username": "testuser", "email": "test@example.com"},   # Missing password
            {},  # Missing all fields
        ]

        for invalid_data in test_cases:
            response = client.post("/api/v1/users/", json=invalid_data)
            assert response.status_code == 422, f"Failed for data: {invalid_data}"

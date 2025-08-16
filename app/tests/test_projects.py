import pytest
from fastapi.testclient import TestClient


class TestProjectEndpoints:
    """Test project management endpoints."""

    def test_create_project_success(self, client: TestClient, authenticated_headers, test_project_data):
        """Test successful project creation."""
        response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=authenticated_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == test_project_data["title"]
        assert data["description"] == test_project_data["description"]
        assert "id" in data
        assert "owner_id" in data

    def test_create_project_unauthenticated(self, client: TestClient, test_project_data):
        """Test creating project without authentication fails."""
        response = client.post("/api/v1/projects/", json=test_project_data)
        assert response.status_code == 401

    def test_create_project_missing_title(self, client: TestClient, authenticated_headers):
        """Test creating project without title fails."""
        invalid_data = {"description": "A project without title"}
        response = client.post(
            "/api/v1/projects/",
            json=invalid_data,
            headers=authenticated_headers
        )
        assert response.status_code == 422

    def test_get_projects_list(self, client: TestClient, authenticated_headers, test_project_data):
        """Test getting list of projects."""
        # Create a project first
        client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=authenticated_headers
        )

        # Get projects list
        response = client.get("/api/v1/projects/", headers=authenticated_headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_projects_list_unauthenticated(self, client: TestClient):
        """Test getting projects list without authentication fails."""
        response = client.get("/api/v1/projects/")
        assert response.status_code == 401

    def test_get_project_by_id_success(self, client: TestClient, authenticated_headers, test_project_data):
        """Test getting a specific project by ID."""
        # Create project first
        create_response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=authenticated_headers
        )
        project_id = create_response.json()["id"]

        # Get project by ID
        response = client.get(f"/api/v1/projects/{project_id}", headers=authenticated_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == project_id
        assert data["title"] == test_project_data["title"]

    def test_get_project_by_id_not_found(self, client: TestClient, authenticated_headers):
        """Test getting non-existent project returns 404."""
        response = client.get("/api/v1/projects/99999", headers=authenticated_headers)
        assert response.status_code == 404

    def test_get_project_by_id_unauthenticated(self, client: TestClient):
        """Test getting project by ID without authentication fails."""
        response = client.get("/api/v1/projects/1")
        assert response.status_code == 401

    def test_update_project_success(self, client: TestClient, authenticated_headers, test_project_data):
        """Test updating project information."""
        # Create project first
        create_response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=authenticated_headers
        )
        project_id = create_response.json()["id"]

        # Update project
        update_data = {
            "title": "Updated Project Title",
            "description": "Updated project description"
        }
        response = client.put(
            f"/api/v1/projects/{project_id}",
            json=update_data,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]

    def test_update_project_not_found(self, client: TestClient, authenticated_headers):
        """Test updating non-existent project returns 404."""
        update_data = {
            "title": "Updated Title",
            "description": "Updated description"
        }
        response = client.put(
            "/api/v1/projects/99999",
            json=update_data,
            headers=authenticated_headers
        )
        assert response.status_code == 404

    def test_update_project_unauthenticated(self, client: TestClient):
        """Test updating project without authentication fails."""
        update_data = {
            "title": "Updated Title",
            "description": "Updated description"
        }
        response = client.put("/api/v1/projects/1", json=update_data)
        assert response.status_code == 401

    def test_delete_project_success(self, client: TestClient, authenticated_headers, test_project_data):
        """Test deleting project."""
        # Create project first
        create_response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=authenticated_headers
        )
        project_id = create_response.json()["id"]

        # Delete project
        response = client.delete(f"/api/v1/projects/{project_id}", headers=authenticated_headers)
        assert response.status_code == 200

        # Verify project is deleted
        get_response = client.get(f"/api/v1/projects/{project_id}", headers=authenticated_headers)
        assert get_response.status_code == 404

    def test_delete_project_not_found(self, client: TestClient, authenticated_headers):
        """Test deleting non-existent project returns 404."""
        response = client.delete("/api/v1/projects/99999", headers=authenticated_headers)
        assert response.status_code == 404

    def test_delete_project_unauthenticated(self, client: TestClient):
        """Test deleting project without authentication fails."""
        response = client.delete("/api/v1/projects/1")
        assert response.status_code == 401


class TestProjectOwnership:
    """Test project ownership and access control."""

    def test_project_owner_access(self, client: TestClient, test_user_data, test_project_data):
        """Test that project owner can access their projects."""
        # Create user and login
        client.post("/api/v1/users/", json=test_user_data)
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

        # Create project
        create_response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=headers
        )
        assert create_response.status_code == 200

        project_data = create_response.json()
        project_id = project_data["id"]

        # Verify owner can access the project
        get_response = client.get(f"/api/v1/projects/{project_id}", headers=headers)
        assert get_response.status_code == 200

    def test_different_user_cannot_access_others_project(self, client: TestClient, test_project_data):
        """Test that users cannot access projects they don't own."""
        # Create first user and project
        user1_data = {
            "username": "user1",
            "email": "user1@example.com",
            "password": "password123"
        }
        client.post("/api/v1/users/", json=user1_data)

        login1_data = {
            "username": user1_data["username"],
            "password": user1_data["password"]
        }
        login1_response = client.post(
            "/api/v1/login/access-token",
            data=login1_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token1 = login1_response.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # Create project as user1
        create_response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=headers1
        )
        project_id = create_response.json()["id"]

        # Create second user
        user2_data = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "password123"
        }
        client.post("/api/v1/users/", json=user2_data)

        login2_data = {
            "username": user2_data["username"],
            "password": user2_data["password"]
        }
        login2_response = client.post(
            "/api/v1/login/access-token",
            data=login2_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token2 = login2_response.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # Try to access user1's project as user2
        # This should either return 404 (not found) or 403 (forbidden)
        # depending on the implementation
        get_response = client.get(f"/api/v1/projects/{project_id}", headers=headers2)
        assert get_response.status_code in [403, 404]


class TestProjectValidation:
    """Test project data validation."""

    @pytest.mark.parametrize("invalid_title", [
        "",
        " ",
        "a" * 201,  # Too long (assuming max length of 200)
    ])
    def test_invalid_project_titles(self, client: TestClient, authenticated_headers, invalid_title):
        """Test various invalid project titles are rejected."""
        invalid_data = {
            "title": invalid_title,
            "description": "Valid description"
        }
        response = client.post(
            "/api/v1/projects/",
            json=invalid_data,
            headers=authenticated_headers
        )
        assert response.status_code == 422

    def test_project_description_optional(self, client: TestClient, authenticated_headers):
        """Test that project description is optional."""
        valid_data = {
            "title": "Project Without Description"
        }
        response = client.post(
            "/api/v1/projects/",
            json=valid_data,
            headers=authenticated_headers
        )
        # This should succeed if description is optional
        assert response.status_code == 200

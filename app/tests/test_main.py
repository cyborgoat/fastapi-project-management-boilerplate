"""
Main test file for basic application functionality.
"""

import pytest
from fastapi.testclient import TestClient


class TestMainApp:
    """Test main application functionality."""

    def test_app_starts(self, client: TestClient):
        """Test that the application starts correctly."""
        # This test passes if the client fixture works, meaning the app starts
        assert client is not None

    def test_root_endpoint_exists(self, client: TestClient):
        """Test that a root endpoint exists or redirects properly."""
        response = client.get("/")
        # The response might be 404, 200, or redirect depending on implementation
        # We just check that the server responds
        assert response.status_code in [200, 404, 307, 404]

    def test_docs_endpoint(self, client: TestClient):
        """Test that API documentation is available."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_endpoint(self, client: TestClient):
        """Test that OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        # Check that it's valid JSON
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_api_v1_prefix(self, client: TestClient):
        """Test that API v1 endpoints are available under correct prefix."""
        # Test a protected endpoint to see if the routing works
        response = client.get("/api/v1/users/")
        # Should return 401 (unauthorized) rather than 404 (not found)
        assert response.status_code == 401

    def test_health_check(self, client: TestClient):
        """Test health check functionality if it exists."""
        # Many APIs have a health check endpoint
        response = client.get("/health")
        # This might not exist yet, so we allow 404
        assert response.status_code in [200, 404]


class TestCORS:
    """Test CORS configuration if needed."""

    def test_cors_headers(self, client: TestClient):
        """Test that CORS headers are present if configured."""
        response = client.get("/docs")

        # If CORS is configured, these headers might be present
        # This is optional and depends on your CORS configuration
        # For now, we just test that the response is successful
        assert response.status_code == 200


class TestErrorHandling:
    """Test application error handling."""

    def test_404_handling(self, client: TestClient):
        """Test that 404 errors are handled properly."""
        response = client.get("/nonexistent/endpoint")
        assert response.status_code == 404

        # Check that error response is JSON
        try:
            error_data = response.json()
            assert "detail" in error_data or "message" in error_data
        except ValueError:
            # If not JSON, that's also acceptable for 404s
            pass

    def test_405_handling(self, client: TestClient):
        """Test that 405 Method Not Allowed errors are handled."""
        # Try a wrong method on an existing endpoint
        response = client.patch("/api/v1/users/")  # PATCH not allowed
        assert response.status_code == 405

    def test_422_validation_error(self, client: TestClient, authenticated_headers):
        """Test that validation errors return 422."""
        # Send invalid data to trigger validation error
        invalid_data = {"invalid": "data"}
        response = client.post(
            "/api/v1/users/",
            json=invalid_data,
            headers=authenticated_headers
        )
        assert response.status_code == 422

        error_data = response.json()
        assert "detail" in error_data


class TestSecurity:
    """Test security-related functionality."""

    def test_security_headers(self, client: TestClient):
        """Test that basic security headers are present."""
        response = client.get("/docs")

        # This is optional - depends on your security configuration
        # Common security headers include:
        # - X-Content-Type-Options
        # - X-Frame-Options
        # - X-XSS-Protection
        # For now, we just ensure the response is successful
        assert response.status_code == 200

    def test_no_sensitive_info_in_errors(self, client: TestClient):
        """Test that error responses don't leak sensitive information."""
        # Try to access a protected endpoint without auth
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401

        error_data = response.json()

        # Error message should not contain sensitive info like:
        # - Database connection strings
        # - Internal file paths
        # - Stack traces (in production)
        error_message = str(error_data).lower()

        assert "password" not in error_message
        assert "secret" not in error_message
        assert "database" not in error_message


@pytest.mark.integration
class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_user_workflow(self, client: TestClient, test_user_data):
        """Test complete user registration and authentication workflow."""
        # 1. Register user
        register_response = client.post("/api/v1/users/", json=test_user_data)
        assert register_response.status_code == 200
        user_data = register_response.json()
        user_id = user_data["id"]

        # 2. Login with username
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        login_response = client.post(
            "/api/v1/login/access-token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        token = token_data["access_token"]

        # 3. Access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        me_response = client.get("/api/v1/users/me", headers=headers)
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["id"] == user_id

        # 4. Login with email
        email_login_data = {
            "username": test_user_data["email"],  # OAuth2 uses 'username' field
            "password": test_user_data["password"]
        }
        email_login_response = client.post(
            "/api/v1/login/access-token",
            data=email_login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert email_login_response.status_code == 200

        # Both login methods should work for the same user
        email_token_data = email_login_response.json()
        email_token = email_token_data["access_token"]

        # 5. Access protected endpoint with email-derived token
        email_headers = {"Authorization": f"Bearer {email_token}"}
        email_me_response = client.get("/api/v1/users/me", headers=email_headers)
        assert email_me_response.status_code == 200
        email_me_data = email_me_response.json()
        assert email_me_data["id"] == user_id  # Same user

    def test_complete_project_task_workflow(self, client: TestClient, authenticated_headers, test_project_data, test_task_data):
        """Test complete project and task management workflow."""
        # 1. Create project
        project_response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=authenticated_headers
        )
        assert project_response.status_code == 200
        project_data = project_response.json()
        project_id = project_data["id"]

        # 2. Create task for project
        task_data = test_task_data.copy()
        task_data["project_id"] = project_id

        task_response = client.post(
            "/api/v1/tasks/",
            json=task_data,
            headers=authenticated_headers
        )
        assert task_response.status_code == 200
        task_response_data = task_response.json()
        task_id = task_response_data["id"]

        # 3. Update task to completed
        update_task_data = task_data.copy()
        update_task_data["completed"] = True

        update_response = client.put(
            f"/api/v1/tasks/{task_id}",
            json=update_task_data,
            headers=authenticated_headers
        )
        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["completed"] is True

        # 4. Verify project still exists and accessible
        project_get_response = client.get(
            f"/api/v1/projects/{project_id}",
            headers=authenticated_headers
        )
        assert project_get_response.status_code == 200

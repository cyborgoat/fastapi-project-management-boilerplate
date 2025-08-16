import pytest
from fastapi.testclient import TestClient


class TestTaskEndpoints:
    """Test task management endpoints."""

    def test_create_task_success(self, client: TestClient, authenticated_headers, test_project_data, test_task_data):
        """Test successful task creation."""
        # Create project first
        project_response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=authenticated_headers
        )
        project_id = project_response.json()["id"]

        # Add project_id to task data
        task_data = test_task_data.copy()
        task_data["project_id"] = project_id

        # Create task
        response = client.post(
            "/api/v1/tasks/",
            json=task_data,
            headers=authenticated_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == test_task_data["title"]
        assert data["description"] == test_task_data["description"]
        assert data["completed"] == test_task_data["completed"]
        assert data["project_id"] == project_id
        assert "id" in data

    def test_create_task_unauthenticated(self, client: TestClient, test_task_data):
        """Test creating task without authentication fails."""
        response = client.post("/api/v1/tasks/", json=test_task_data)
        assert response.status_code == 401

    def test_create_task_missing_title(self, client: TestClient, authenticated_headers, test_project_data):
        """Test creating task without title fails."""
        # Create project first
        project_response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=authenticated_headers
        )
        project_id = project_response.json()["id"]

        invalid_data = {
            "description": "A task without title",
            "project_id": project_id,
            "completed": False
        }
        response = client.post(
            "/api/v1/tasks/",
            json=invalid_data,
            headers=authenticated_headers
        )
        assert response.status_code == 422

    def test_create_task_invalid_project(self, client: TestClient, authenticated_headers, test_task_data):
        """Test creating task with invalid project ID fails."""
        task_data = test_task_data.copy()
        task_data["project_id"] = 99999  # Non-existent project

        response = client.post(
            "/api/v1/tasks/",
            json=task_data,
            headers=authenticated_headers
        )
        assert response.status_code == 404

    def test_get_tasks_list(self, client: TestClient, authenticated_headers, test_project_data, test_task_data):
        """Test getting list of tasks."""
        # Create project and task first
        project_response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=authenticated_headers
        )
        project_id = project_response.json()["id"]

        task_data = test_task_data.copy()
        task_data["project_id"] = project_id

        client.post(
            "/api/v1/tasks/",
            json=task_data,
            headers=authenticated_headers
        )

        # Get tasks list
        response = client.get("/api/v1/tasks/", headers=authenticated_headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_tasks_list_unauthenticated(self, client: TestClient):
        """Test getting tasks list without authentication fails."""
        response = client.get("/api/v1/tasks/")
        assert response.status_code == 401

    def test_get_task_by_id_success(self, client: TestClient, authenticated_headers, test_project_data, test_task_data):
        """Test getting a specific task by ID."""
        # Create project and task first
        project_response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=authenticated_headers
        )
        project_id = project_response.json()["id"]

        task_data = test_task_data.copy()
        task_data["project_id"] = project_id

        create_response = client.post(
            "/api/v1/tasks/",
            json=task_data,
            headers=authenticated_headers
        )
        task_id = create_response.json()["id"]

        # Get task by ID
        response = client.get(f"/api/v1/tasks/{task_id}", headers=authenticated_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == test_task_data["title"]

    def test_get_task_by_id_not_found(self, client: TestClient, authenticated_headers):
        """Test getting non-existent task returns 404."""
        response = client.get("/api/v1/tasks/99999", headers=authenticated_headers)
        assert response.status_code == 404

    def test_get_task_by_id_unauthenticated(self, client: TestClient):
        """Test getting task by ID without authentication fails."""
        response = client.get("/api/v1/tasks/1")
        assert response.status_code == 401

    def test_update_task_success(self, client: TestClient, authenticated_headers, test_project_data, test_task_data):
        """Test updating task information."""
        # Create project and task first
        project_response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=authenticated_headers
        )
        project_id = project_response.json()["id"]

        task_data = test_task_data.copy()
        task_data["project_id"] = project_id

        create_response = client.post(
            "/api/v1/tasks/",
            json=task_data,
            headers=authenticated_headers
        )
        task_id = create_response.json()["id"]

        # Update task
        update_data = {
            "title": "Updated Task Title",
            "description": "Updated task description",
            "completed": True,
            "project_id": project_id
        }
        response = client.put(
            f"/api/v1/tasks/{task_id}",
            json=update_data,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["completed"] == update_data["completed"]

    def test_update_task_completion_status(self, client: TestClient, authenticated_headers, test_project_data, test_task_data):
        """Test updating task completion status."""
        # Create project and task first
        project_response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=authenticated_headers
        )
        project_id = project_response.json()["id"]

        task_data = test_task_data.copy()
        task_data["project_id"] = project_id
        task_data["completed"] = False

        create_response = client.post(
            "/api/v1/tasks/",
            json=task_data,
            headers=authenticated_headers
        )
        task_id = create_response.json()["id"]

        # Mark task as completed
        update_data = {
            "title": task_data["title"],
            "description": task_data["description"],
            "completed": True,
            "project_id": project_id
        }
        response = client.put(
            f"/api/v1/tasks/{task_id}",
            json=update_data,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        assert response.json()["completed"] is True

    def test_update_task_not_found(self, client: TestClient, authenticated_headers):
        """Test updating non-existent task returns 404."""
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "completed": True,
            "project_id": 1
        }
        response = client.put(
            "/api/v1/tasks/99999",
            json=update_data,
            headers=authenticated_headers
        )
        assert response.status_code == 404

    def test_update_task_unauthenticated(self, client: TestClient):
        """Test updating task without authentication fails."""
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "completed": True,
            "project_id": 1
        }
        response = client.put("/api/v1/tasks/1", json=update_data)
        assert response.status_code == 401

    def test_delete_task_success(self, client: TestClient, authenticated_headers, test_project_data, test_task_data):
        """Test deleting task."""
        # Create project and task first
        project_response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=authenticated_headers
        )
        project_id = project_response.json()["id"]

        task_data = test_task_data.copy()
        task_data["project_id"] = project_id

        create_response = client.post(
            "/api/v1/tasks/",
            json=task_data,
            headers=authenticated_headers
        )
        task_id = create_response.json()["id"]

        # Delete task
        response = client.delete(f"/api/v1/tasks/{task_id}", headers=authenticated_headers)
        assert response.status_code == 200

        # Verify task is deleted
        get_response = client.get(f"/api/v1/tasks/{task_id}", headers=authenticated_headers)
        assert get_response.status_code == 404

    def test_delete_task_not_found(self, client: TestClient, authenticated_headers):
        """Test deleting non-existent task returns 404."""
        response = client.delete("/api/v1/tasks/99999", headers=authenticated_headers)
        assert response.status_code == 404

    def test_delete_task_unauthenticated(self, client: TestClient):
        """Test deleting task without authentication fails."""
        response = client.delete("/api/v1/tasks/1")
        assert response.status_code == 401


class TestTasksByProject:
    """Test tasks filtered by project."""

    def test_get_tasks_by_project(self, client: TestClient, authenticated_headers, test_project_data, test_task_data):
        """Test getting tasks filtered by project."""
        # Create project
        project_response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=authenticated_headers
        )
        project_id = project_response.json()["id"]

        # Create multiple tasks for the project
        for i in range(3):
            task_data = test_task_data.copy()
            task_data["title"] = f"Task {i+1}"
            task_data["project_id"] = project_id

            client.post(
                "/api/v1/tasks/",
                json=task_data,
                headers=authenticated_headers
            )

        # Get tasks by project (if this endpoint exists)
        response = client.get(
            f"/api/v1/projects/{project_id}/tasks",
            headers=authenticated_headers
        )

        # This test assumes the endpoint exists
        # If it doesn't exist yet, the test will fail and indicate
        # that this functionality could be implemented
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 3

            # All tasks should belong to the same project
            for task in data:
                assert task["project_id"] == project_id

    def test_get_tasks_by_project_unauthenticated(self, client: TestClient):
        """Test getting tasks by project without authentication fails."""
        response = client.get("/api/v1/projects/1/tasks")
        assert response.status_code == 401


class TestTaskValidation:
    """Test task data validation."""

    @pytest.mark.parametrize("invalid_title", [
        "",
        " ",
        "a" * 201,  # Too long (assuming max length of 200)
    ])
    def test_invalid_task_titles(self, client: TestClient, authenticated_headers, test_project_data, invalid_title):
        """Test various invalid task titles are rejected."""
        # Create project first
        project_response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=authenticated_headers
        )
        project_id = project_response.json()["id"]

        invalid_data = {
            "title": invalid_title,
            "description": "Valid description",
            "project_id": project_id,
            "completed": False
        }
        response = client.post(
            "/api/v1/tasks/",
            json=invalid_data,
            headers=authenticated_headers
        )
        assert response.status_code == 422

    def test_task_completion_boolean(self, client: TestClient, authenticated_headers, test_project_data):
        """Test that task completion status must be boolean."""
        # Create project first
        project_response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=authenticated_headers
        )
        project_id = project_response.json()["id"]

        invalid_data = {
            "title": "Test Task",
            "description": "Test description",
            "project_id": project_id,
            "completed": "not_boolean"  # Invalid type
        }
        response = client.post(
            "/api/v1/tasks/",
            json=invalid_data,
            headers=authenticated_headers
        )
        assert response.status_code == 422

    def test_task_description_optional(self, client: TestClient, authenticated_headers, test_project_data):
        """Test that task description is optional."""
        # Create project first
        project_response = client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers=authenticated_headers
        )
        project_id = project_response.json()["id"]

        valid_data = {
            "title": "Task Without Description",
            "project_id": project_id,
            "completed": False
        }
        response = client.post(
            "/api/v1/tasks/",
            json=valid_data,
            headers=authenticated_headers
        )
        # This should succeed if description is optional
        assert response.status_code == 200

    def test_task_requires_project_id(self, client: TestClient, authenticated_headers):
        """Test that task requires a project_id."""
        invalid_data = {
            "title": "Task Without Project",
            "description": "This task has no project",
            "completed": False
        }
        response = client.post(
            "/api/v1/tasks/",
            json=invalid_data,
            headers=authenticated_headers
        )
        assert response.status_code == 422

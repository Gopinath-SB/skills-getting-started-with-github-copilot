"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_success(self):
        """Test that we can retrieve all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
    def test_get_activities_has_required_fields(self):
        """Test that activities have required fields"""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonExistent/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_student(self):
        """Test that duplicate signup is rejected"""
        email = "duplicate@mergington.edu"
        activity_name = "Chess%20Club"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregister from an activity"""
        activity_name = "Programming%20Class"
        email = "test_unregister@mergington.edu"
        
        # First signup
        client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Then unregister
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_not_signed_up(self):
        """Test unregister for student not signed up"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=notreal@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_activity_not_found(self):
        """Test unregister from non-existent activity"""
        response = client.post(
            "/activities/NonExistent/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root_redirect(self):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]

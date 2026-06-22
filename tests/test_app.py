"""
Test suite for the Mergington High School Activities API
Uses the AAA (Arrange-Act-Assert) pattern for test structure
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture to provide a test client for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_200(self, client):
        """
        Test that GET /activities returns all activities successfully
        
        Arrange: No setup needed - activities are pre-loaded
        Act: Make GET request to /activities
        Assert: Status code is 200 and response is valid JSON
        """
        # Arrange
        expected_status = 200
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == expected_status
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0

    def test_activities_have_required_fields(self, client):
        """
        Test that each activity has the required structure
        
        Arrange: Fetch activities from API
        Act: Verify structure of returned data
        Assert: Each activity has description, schedule, max_participants, and participants
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(activity_data.keys())
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_returns_200(self, client):
        """
        Test that a new participant can successfully sign up for an activity
        
        Arrange: Select an activity and a test email
        Act: Make POST request to signup endpoint
        Assert: Status code is 200 and success message is returned
        """
        # Arrange
        activity_name = "Chess Club"
        test_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert test_email in result["message"]

    def test_participant_added_to_activity(self, client):
        """
        Test that a signed-up participant appears in the activity's participant list
        
        Arrange: Sign up a new participant
        Act: Fetch activities and check participant list
        Assert: New participant is in the list
        """
        # Arrange
        activity_name = "Programming Class"
        test_email = "verify@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Act - Fetch activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert
        assert signup_response.status_code == 200
        assert test_email in activities[activity_name]["participants"]

    def test_duplicate_signup_returns_400(self, client):
        """
        Test that signing up twice for the same activity returns a 400 error
        
        Arrange: Already have participants in the database
        Act: Try to signup an existing participant again
        Assert: Status code is 400 and error detail is provided
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Pre-loaded participant
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Test that signing up for a non-existent activity returns 404
        
        Arrange: Use a fake activity name
        Act: Try to signup for non-existent activity
        Assert: Status code is 404 and error detail is provided
        """
        # Arrange
        fake_activity = "Nonexistent Activity"
        test_email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""

    def test_remove_participant_returns_200(self, client):
        """
        Test that removing an existing participant returns 200
        
        Arrange: Get a participant from an activity
        Act: Make DELETE request to remove participant
        Assert: Status code is 200 and success message is returned
        """
        # Arrange
        activity_name = "Gym Class"
        participant_email = "john@mergington.edu"  # Pre-loaded participant
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": participant_email}
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert participant_email in result["message"]

    def test_removed_participant_no_longer_in_list(self, client):
        """
        Test that a removed participant no longer appears in the activity
        
        Arrange: Remove a participant
        Act: Fetch activities and check participant list
        Assert: Removed participant is not in the list
        """
        # Arrange
        activity_name = "Soccer Team"
        participant_email = "nina@mergington.edu"  # Pre-loaded participant
        
        # Act - Remove participant
        delete_response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": participant_email}
        )
        
        # Act - Fetch activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert
        assert delete_response.status_code == 200
        assert participant_email not in activities[activity_name]["participants"]

    def test_remove_nonexistent_participant_returns_404(self, client):
        """
        Test that removing a non-existent participant returns 404
        
        Arrange: Use an email not in any participant list
        Act: Try to remove that email from an activity
        Assert: Status code is 404 and error detail is provided
        """
        # Arrange
        activity_name = "Basketball Club"
        fake_email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": fake_email}
        )
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"]

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """
        Test that trying to remove from a non-existent activity returns 404
        
        Arrange: Use a fake activity name
        Act: Try to remove participant from non-existent activity
        Assert: Status code is 404 and error detail is provided
        """
        # Arrange
        fake_activity = "Fake Activity"
        test_email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{fake_activity}/participants",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"]

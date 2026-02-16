"""
Test suite for the Mergington High School Activities API endpoints
"""
import pytest
from fastapi import status


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities"""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, dict)
        
        # Check that all expected activities are present
        expected_activities = [
            "Soccer Team", "Basketball Club", "Art Studio", "Drama Club",
            "Debate Team", "Science Club", "Chess Club", "Programming Class", "Gym Class"
        ]
        for activity in expected_activities:
            assert activity in data
    
    def test_activity_structure(self, client):
        """Test that each activity has the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        # Test one activity structure
        soccer = data["Soccer Team"]
        assert "description" in soccer
        assert "schedule" in soccer
        assert "max_participants" in soccer
        assert "participants" in soccer
        assert isinstance(soccer["participants"], list)
    
    def test_activity_initial_participants(self, client):
        """Test that activities have their initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        # Check Soccer Team has its initial participants
        assert "alex@mergington.edu" in data["Soccer Team"]["participants"]
        assert "sarah@mergington.edu" in data["Soccer Team"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_success(self, client):
        """Test successful signup for a new student"""
        response = client.post(
            "/activities/Soccer Team/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "Signed up newstudent@mergington.edu for Soccer Team" in response.json()["message"]
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "newstudent@mergington.edu" in activities["Soccer Team"]["participants"]
    
    def test_signup_duplicate_student_fails(self, client):
        """Test that signing up the same student twice fails"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == status.HTTP_200_OK
        
        # Second signup should fail
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already signed up" in response2.json()["detail"].lower()
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for a non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        response = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": "coder@mergington.edu"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "coder@mergington.edu" in activities["Programming Class"]["participants"]
    
    def test_signup_multiple_students_to_same_activity(self, client):
        """Test that multiple different students can sign up for the same activity"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                "/activities/Drama Club/signup",
                params={"email": email}
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all students were added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        for email in emails:
            assert email in activities["Drama Club"]["participants"]
    
    def test_signup_student_to_multiple_activities(self, client):
        """Test that a student can sign up for multiple different activities"""
        email = "multitasker@mergington.edu"
        activities_to_join = ["Art Studio", "Science Club", "Debate Team"]
        
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Verify student is in all activities
        activities_response = client.get("/activities")
        all_activities = activities_response.json()
        for activity in activities_to_join:
            assert email in all_activities[activity]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_existing_participant_success(self, client):
        """Test successful removal of an existing participant"""
        # First, add a student
        client.post(
            "/activities/Basketball Club/signup",
            params={"email": "removeme@mergington.edu"}
        )
        
        # Then remove them
        response = client.delete(
            "/activities/Basketball Club/participants/removeme@mergington.edu"
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "Removed removeme@mergington.edu from Basketball Club" in response.json()["message"]
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "removeme@mergington.edu" not in activities["Basketball Club"]["participants"]
    
    def test_remove_initial_participant(self, client):
        """Test removing a participant that was in the initial data"""
        response = client.delete(
            "/activities/Soccer Team/participants/alex@mergington.edu"
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "alex@mergington.edu" not in activities["Soccer Team"]["participants"]
    
    def test_remove_nonexistent_participant_fails(self, client):
        """Test that removing a non-existent participant fails"""
        response = client.delete(
            "/activities/Gym Class/participants/nonexistent@mergington.edu"
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Student not found" in response.json()["detail"]
    
    def test_remove_from_nonexistent_activity_fails(self, client):
        """Test that removing from a non-existent activity fails"""
        response = client.delete(
            "/activities/Fake Activity/participants/student@mergington.edu"
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Activity not found" in response.json()["detail"]
    
    def test_remove_with_url_encoded_names(self, client):
        """Test removal with URL-encoded activity and email"""
        # Add a student first
        client.post(
            "/activities/Programming Class/signup",
            params={"email": "test+user@mergington.edu"}
        )
        
        # Remove with URL encoding
        response = client.delete(
            "/activities/Programming%20Class/participants/test%2Buser@mergington.edu"
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_remove_and_add_again(self, client):
        """Test that a participant can be removed and added back"""
        email = "comeback@mergington.edu"
        activity = "Debate Team"
        
        # Add student
        response1 = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response1.status_code == status.HTTP_200_OK
        
        # Remove student
        response2 = client.delete(f"/activities/{activity}/participants/{email}")
        assert response2.status_code == status.HTTP_200_OK
        
        # Add student again
        response3 = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response3.status_code == status.HTTP_200_OK
        
        # Verify student is in the activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity]["participants"]


class TestIntegrationScenarios:
    """Integration tests for complex scenarios"""
    
    def test_full_lifecycle(self, client):
        """Test a full lifecycle: get activities, signup, verify, remove, verify"""
        email = "lifecycle@mergington.edu"
        activity = "Art Studio"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert signup_response.status_code == status.HTTP_200_OK
        
        # Verify addition
        after_signup = client.get("/activities")
        assert len(after_signup.json()[activity]["participants"]) == initial_count + 1
        assert email in after_signup.json()[activity]["participants"]
        
        # Remove
        remove_response = client.delete(f"/activities/{activity}/participants/{email}")
        assert remove_response.status_code == status.HTTP_200_OK
        
        # Verify removal
        after_removal = client.get("/activities")
        assert len(after_removal.json()[activity]["participants"]) == initial_count
        assert email not in after_removal.json()[activity]["participants"]
    
    def test_multiple_operations_on_different_activities(self, client):
        """Test multiple operations across different activities"""
        # Add students to multiple activities
        client.post("/activities/Soccer Team/signup", params={"email": "athlete1@mergington.edu"})
        client.post("/activities/Chess Club/signup", params={"email": "thinker1@mergington.edu"})
        client.post("/activities/Drama Club/signup", params={"email": "actor1@mergington.edu"})
        
        # Remove a student from one activity
        client.delete("/activities/Soccer Team/participants/alex@mergington.edu")
        
        # Get activities and verify all changes
        response = client.get("/activities")
        activities = response.json()
        
        assert "athlete1@mergington.edu" in activities["Soccer Team"]["participants"]
        assert "alex@mergington.edu" not in activities["Soccer Team"]["participants"]
        assert "thinker1@mergington.edu" in activities["Chess Club"]["participants"]
        assert "actor1@mergington.edu" in activities["Drama Club"]["participants"]
    
    def test_participant_count_accuracy(self, client):
        """Test that participant counts remain accurate across operations"""
        activity = "Science Club"
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity]["participants"]
        initial_count = len(initial_participants)
        
        # Add 3 students
        for i in range(3):
            client.post(f"/activities/{activity}/signup", params={"email": f"scientist{i}@mergington.edu"})
        
        # Check count increased by 3
        after_add = client.get("/activities")
        assert len(after_add.json()[activity]["participants"]) == initial_count + 3
        
        # Remove 2 students
        client.delete(f"/activities/{activity}/participants/scientist0@mergington.edu")
        client.delete(f"/activities/{activity}/participants/scientist1@mergington.edu")
        
        # Check count is initial + 1
        final = client.get("/activities")
        assert len(final.json()[activity]["participants"]) == initial_count + 1

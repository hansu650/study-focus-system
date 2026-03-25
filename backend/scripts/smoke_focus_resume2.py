import requests
import json

# Base URL of the backend API
BASE_URL = "http://localhost:8000/api/v1"
VALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Replace with real valid token

def test_focus_resume_create():
    """
    Test focus resume create API endpoint
    Verify that creating resume returns 201 Created and resume ID
    """
    resume_url = f"{BASE_URL}/focus/resume"
    headers = {
        "Authorization": f"Bearer {VALID_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": "John Doe",
        "position": "Software Engineer",
        "experience": [
            {
                "company": "Tech Corp",
                "duration": "2020-2023",
                "responsibilities": ["Develop REST APIs", "Write unit tests"]
            }
        ],
        "skills": ["Python", "Django", "REST API", "Testing"]
    }
    
    response = requests.post(resume_url, json=payload, headers=headers)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    
    resume_data = response.json()
    assert "resume_id" in resume_data, "Resume ID missing in response"
    print(f"test_focus_resume_create passed (resume ID: {resume_data['resume_id']})")
    return resume_data["resume_id"]

def test_focus_resume_get_by_id(resume_id):
    """
    Test focus resume get by ID API endpoint
    Verify that getting resume by ID returns 200 OK and correct data
    """
    resume_url = f"{BASE_URL}/focus/resume/{resume_id}"
    headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
    
    response = requests.get(resume_url, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    resume_data = response.json()
    assert resume_data["resume_id"] == resume_id, "Resume ID mismatch"
    assert resume_data["name"] == "John Doe", "Resume name mismatch"
    print("test_focus_resume_get_by_id passed")

def test_focus_resume_update(resume_id):
    """
    Test focus resume update API endpoint
    Verify that updating resume returns 200 OK and updated data
    """
    resume_url = f"{BASE_URL}/focus/resume/{resume_id}"
    headers = {
        "Authorization": f"Bearer {VALID_TOKEN}",
        "Content-Type": "application/json"
    }
    update_payload = {
        "position": "Senior Software Engineer",
        "skills": ["Python", "Django", "REST API", "Testing", "CI/CD"]
    }
    
    response = requests.patch(resume_url, json=update_payload, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    updated_data = response.json()
    assert updated_data["position"] == "Senior Software Engineer", "Position not updated"
    assert "CI/CD" in updated_data["skills"], "Skills not updated"
    print("test_focus_resume_update passed")

if __name__ == "__main__":
    resume_id = test_focus_resume_create()
    test_focus_resume_get_by_id(resume_id)
    test_focus_resume_update(resume_id)

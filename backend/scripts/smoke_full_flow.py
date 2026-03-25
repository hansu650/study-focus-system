import requests
import time

# Base URL of the backend API
BASE_URL = "http://localhost:8000/api/v1"

def test_full_user_ai_resume_flow():
    """
    Test full end-to-end flow: User Login → AI Chat → Create Resume
    Verify all steps work together without errors
    """
    # Step 1: User Login
    login_url = f"{BASE_URL}/user/login"
    login_payload = {"username": "test_user", "password": "test_password123"}
    login_response = requests.post(login_url, json=login_payload)
    assert login_response.status_code == 200, "Login failed"
    token = login_response.json()["access_token"]
    print("Step 1: User login passed")
    
    # Step 2: AI Chat (get resume advice)
    chat_url = f"{BASE_URL}/ai/chat"
    chat_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    chat_payload = {
        "conversation_id": "conv_full_flow",
        "message": "Give advice for a Senior Python Engineer resume"
    }
    chat_response = requests.post(chat_url, json=chat_payload, headers=chat_headers)
    assert chat_response.status_code == 200, "AI chat failed"
    ai_advice = chat_response.json()["reply"]
    assert len(ai_advice) > 0, "AI advice is empty"
    print("Step 2: AI chat for resume advice passed")
    
    # Step 3: Create Focus Resume (using AI advice)
    resume_url = f"{BASE_URL}/focus/resume"
    resume_payload = {
        "name": "Jane Smith",
        "position": "Senior Python Engineer",
        "experience": [
            {
                "company": "Data Tech Inc",
                "duration": "2019-2024",
                "responsibilities": ["Lead backend development", "Optimize API performance"]
            }
        ],
        "skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"],
        "ai_advice": ai_advice  # Include AI advice in resume
    }
    resume_response = requests.post(resume_url, json=resume_payload, headers=chat_headers)
    assert resume_response.status_code == 201, "Resume creation failed"
    resume_id = resume_response.json()["resume_id"]
    assert resume_id is not None, "Resume ID not generated"
    print("Step 3: Resume creation passed")
    
    # Step 4: Verify resume exists
    resume_get_url = f"{BASE_URL}/focus/resume/{resume_id}"
    resume_get_response = requests.get(resume_get_url, headers=chat_headers)
    assert resume_get_response.status_code == 200, "Resume retrieval failed"
    assert resume_get_response.json()["position"] == "Senior Python Engineer", "Resume data mismatch"
    print("Step 4: Resume verification passed")
    
    print("\n✅ Full end-to-end flow test passed!")

if __name__ == "__main__":
    test_full_user_ai_resume_flow()

import requests
import json

# Base URL of the backend API
BASE_URL = "http://localhost:8000/api/v1"


def test_user_login():
    """
    Test user login API endpoint
    Verify that valid credentials return 200 OK and token, invalid credentials return 401
    """
    # Test case 1: Valid login credentials
    login_url = f"{BASE_URL}/user/login"
    valid_payload = {
        "username": "test_user",
        "password": "test_password123"
    }
    response = requests.post(login_url, json=valid_payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "access_token" in response.json(), "Access token not found in response"

    # Test case 2: Invalid password
    invalid_payload = {
        "username": "test_user",
        "password": "wrong_password"
    }
    response = requests.post(login_url, json=invalid_payload)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    print("test_user_login passed")


def test_user_logout():
    """
    Test user logout API endpoint
    Verify that logout with valid token returns 200 OK
    """
    # First get valid token
    login_response = requests.post(f"{BASE_URL}/user/login",
                                   json={"username": "test_user", "password": "test_password123"})
    token = login_response.json()["access_token"]

    logout_url = f"{BASE_URL}/user/logout"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(logout_url, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("test_user_logout passed")


if __name__ == "__main__":
    test_user_login()
    test_user_logout()

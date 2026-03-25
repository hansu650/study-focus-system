import requests
import time

# Base URL of the backend API
BASE_URL = "http://localhost:8000/api/v1"
VALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Replace with real valid token

def test_ai_chat_send_message():
    """
    Test AI chat send message API endpoint
    Verify that sending message returns 200 OK and valid response content
    """
    chat_url = f"{BASE_URL}/ai/chat"
    headers = {
        "Authorization": f"Bearer {VALID_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "conversation_id": "conv_123456",
        "message": "Explain REST API in simple terms"
    }
    
    # Send chat request
    response = requests.post(chat_url, json=payload, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Validate response structure
    response_data = response.json()
    assert "reply" in response_data, "AI reply not found in response"
    assert "conversation_id" in response_data, "Conversation ID missing in response"
    assert len(response_data["reply"]) > 0, "AI reply is empty"
    print("test_ai_chat_send_message passed")

def test_ai_chat_conversation_history():
    """
    Test AI chat conversation history API endpoint
    Verify that getting history returns 200 OK and non-empty list (if history exists)
    """
    history_url = f"{BASE_URL}/ai/chat/history"
    headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
    params = {"conversation_id": "conv_123456"}
    
    response = requests.get(history_url, headers=headers, params=params)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    history_data = response.json()
    assert isinstance(history_data, list), "Conversation history should be a list"
    print("test_ai_chat_conversation_history passed")

if __name__ == "__main__":
    test_ai_chat_send_message()
    test_ai_chat_conversation_history()

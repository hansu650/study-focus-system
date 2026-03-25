import unittest
import requests

# Backend service base URL
BASE_URL = "http://127.0.0.1:8000"

class TestAIService(unittest.TestCase):
    """Automated tests for AI service APIs"""

    def test_health_check(self):
        """Test service health check endpoint"""
        resp = requests.get(f"{BASE_URL}/health")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("status", resp.json())

    def test_ai_chat_normal(self):
        """Test AI chat API with valid parameters"""
        payload = {
            "user_id": "test_user_001",
            "message": "Hello, please introduce yourself briefly"
        }
        resp = requests.post(f"{BASE_URL}/api/ai/chat", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("reply", resp.json())

    def test_ai_chat_missing_params(self):
        """Test AI chat API with missing required parameters"""
        payload = {"user_id": "test_user_002"}
        resp = requests.post(f"{BASE_URL}/api/ai/chat", json=payload)
        self.assertEqual(resp.status_code, 400)

if __name__ == '__main__':
    unittest.main()

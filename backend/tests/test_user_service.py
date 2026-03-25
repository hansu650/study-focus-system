import unittest
import json
from unittest.mock import Mock, patch
from backend.services.user_service import UserService  # Replace with actual module path
from backend.models.user import User  # Replace with actual model path
from backend.exceptions import AuthenticationError

class TestUserService(unittest.TestCase):
    """Unit tests for User Service layer"""
    
    def setUp(self):
        """Initialize test dependencies before each test case"""
        self.user_service = UserService()
        self.mock_user = User(
            id=1,
            username="test_user",
            email="test@example.com"
        )
        # Set password hash (mock real hash logic)
        self.mock_user.password_hash = "hashed_test_password123"

    def test_verify_password_success(self):
        """Test password verification with correct credentials"""
        # Arrange
        username = "test_user"
        password = "test_password123"
        
        # Mock database query
        with patch.object(self.user_service.db, 'get_user_by_username') as mock_get:
            mock_get.return_value = self.mock_user
            
            # Act
            result = self.user_service.verify_credentials(username, password)
            
            # Assert
            self.assertTrue(result)
            mock_get.assert_called_once_with(username)

    def test_verify_password_failure(self):
        """Test password verification with incorrect credentials"""
        # Arrange
        username = "test_user"
        wrong_password = "wrong_password"
        
        # Mock database query
        with patch.object(self.user_service.db, 'get_user_by_username') as mock_get:
            mock_get.return_value = self.mock_user
            
            # Act & Assert
            with self.assertRaises(AuthenticationError):
                self.user_service.verify_credentials(username, wrong_password)
            mock_get.assert_called_once_with(username)

    def test_create_user_valid_data(self):
        """Test user creation with valid input data"""
        # Arrange
        user_data = {
            "username": "new_user",
            "email": "new@example.com",
            "password": "new_password123"
        }
        
        # Mock database save
        with patch.object(self.user_service.db, 'save_user') as mock_save:
            mock_save.return_value = User(id=2, **user_data)
            
            # Act
            new_user = self.user_service.create_user(user_data)
            
            # Assert
            self.assertEqual(new_user.username, user_data["username"])
            self.assertEqual(new_user.email, user_data["email"])
            mock_save.assert_called_once()

    def tearDown(self):
        """Clean up after each test case"""
        self.user_service = None

if __name__ == '__main__':
    unittest.main()

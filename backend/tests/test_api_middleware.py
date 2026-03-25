import unittest
from unittest.mock import Mock, patch
from fastapi import Request, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
from backend.api.middleware import AuthMiddleware  # Replace with actual path
from backend.utils.token import TokenValidator  # Replace with actual path

class TestApiMiddleware(unittest.TestCase):
    """Unit tests for API middleware (authentication/validation)"""
    
    def setUp(self):
        """Initialize test dependencies"""
        self.auth_middleware = AuthMiddleware(app=Mock())
        self.mock_request = Mock(spec=Request)
        self.valid_token = "valid_jwt_token_123"
        self.invalid_token = "invalid_jwt_token_456"

    def test_auth_middleware_valid_token(self):
        """Test middleware passes with valid authentication token"""
        # Arrange
        self.mock_request.headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        # Mock token validation
        with patch.object(TokenValidator, 'validate') as mock_validate:
            mock_validate.return_value = {"user_id": 1, "username": "test_user"}
            
            # Act (middleware call - simulate ASGI call)
            async def mock_call_next(request):
                return Mock(status_code=200)
            
            # Run async test (simplified for unittest)
            result = self.auth_middleware.dispatch(self.mock_request, mock_call_next)
            
            # Assert
            mock_validate.assert_called_once_with(self.valid_token)
            self.assertTrue(result)

    def test_auth_middleware_missing_token(self):
        """Test middleware raises 401 when token is missing"""
        # Arrange
        self.mock_request.headers = {}  # No Authorization header
        
        # Act & Assert
        with self.assertRaises(HTTPException) as ctx:
            # Simulate middleware dispatch
            self.auth_middleware.validate_token(self.mock_request)
        
        self.assertEqual(ctx.exception.status_code, HTTP_401_UNAUTHORIZED)
        self.assertEqual(ctx.exception.detail, "Authorization token missing")

    def test_auth_middleware_invalid_token(self):
        """Test middleware raises 401 with invalid token"""
        # Arrange
        self.mock_request.headers = {"Authorization": f"Bearer {self.invalid_token}"}
        
        # Mock token validation failure
        with patch.object(TokenValidator, 'validate') as mock_validate:
            mock_validate.side_effect = HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
            
            # Act & Assert
            with self.assertRaises(HTTPException) as ctx:
                self.auth_middleware.validate_token(self.mock_request)
            
            self.assertEqual(ctx.exception.status_code, HTTP_401_UNAUTHORIZED)
            mock_validate.assert_called_once_with(self.invalid_token)

if __name__ == '__main__':
    unittest.main()

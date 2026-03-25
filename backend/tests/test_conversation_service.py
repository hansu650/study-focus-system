import unittest
from unittest.mock import Mock, patch
from backend.services.conversation_service import ConversationService  # Replace with actual path
from backend.models.conversation import Conversation, Message  # Replace with actual path

class TestConversationService(unittest.TestCase):
    """Unit tests for Conversation Service layer"""
    
    def setUp(self):
        """Initialize test dependencies"""
        self.conv_service = ConversationService()
        self.mock_conversation = Conversation(
            id="conv_123456",
            user_id=1,
            messages=[
                Message(id=1, role="user", content="Hello AI"),
                Message(id=2, role="assistant", content="Hi there!")
            ]
        )

    def test_get_conversation_by_id(self):
        """Test retrieving conversation by valid ID"""
        # Arrange
        conv_id = "conv_123456"
        user_id = 1
        
        # Mock database query
        with patch.object(self.conv_service.db, 'get_conversation') as mock_get:
            mock_get.return_value = self.mock_conversation
            
            # Act
            result = self.conv_service.get_conversation(conv_id, user_id)
            
            # Assert
            self.assertEqual(result.id, conv_id)
            self.assertEqual(result.user_id, user_id)
            self.assertEqual(len(result.messages), 2)
            mock_get.assert_called_once_with(conv_id, user_id)

    def test_add_message_to_conversation(self):
        """Test adding new message to existing conversation"""
        # Arrange
        conv_id = "conv_123456"
        user_id = 1
        new_message = {
            "role": "user",
            "content": "Explain unit testing"
        }
        
        # Mock dependencies
        with patch.object(self.conv_service.db, 'get_conversation') as mock_get:
            mock_get.return_value = self.mock_conversation
            with patch.object(self.conv_service.db, 'save_message') as mock_save:
                mock_save.return_value = Message(id=3, **new_message)
                
                # Act
                updated_conv = self.conv_service.add_message(conv_id, user_id, new_message)
                
                # Assert
                self.assertEqual(len(updated_conv.messages), 3)
                self.assertEqual(updated_conv.messages[-1].content, new_message["content"])
                mock_get.assert_called_once_with(conv_id, user_id)
                mock_save.assert_called_once()

    def test_get_conversation_not_found(self):
        """Test error handling for non-existent conversation ID"""
        # Arrange
        conv_id = "invalid_conv_id"
        user_id = 1
        
        # Mock database query returning None
        with patch.object(self.conv_service.db, 'get_conversation') as mock_get:
            mock_get.return_value = None
            
            # Act & Assert
            result = self.conv_service.get_conversation(conv_id, user_id)
            self.assertIsNone(result)
            mock_get.assert_called_once_with(conv_id, user_id)

if __name__ == '__main__':
    unittest.main()

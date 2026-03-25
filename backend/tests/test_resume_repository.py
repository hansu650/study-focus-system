import unittest
from unittest.mock import Mock, MagicMock
from backend.repositories.resume_repository import ResumeRepository  # Replace with actual path
from backend.models.resume import Resume  # Replace with actual path

class TestResumeRepository(unittest.TestCase):
    """Unit tests for Resume Repository layer (data access layer)"""
    
    def setUp(self):
        """Initialize test dependencies"""
        self.db_session = Mock()
        self.resume_repo = ResumeRepository(self.db_session)
        self.test_resume = Resume(
            id="res_789012",
            user_id=1,
            name="John Doe",
            position="Software Engineer",
            skills=["Python", "Django", "Testing"]
        )

    def test_get_resume_by_id_success(self):
        """Test retrieving resume by ID from database"""
        # Arrange
        resume_id = "res_789012"
        user_id = 1
        
        # Mock ORM query
        self.db_session.query.return_value.filter.return_value.first.return_value = self.test_resume
        
        # Act
        resume = self.resume_repo.get_by_id(resume_id, user_id)
        
        # Assert
        self.assertEqual(resume.id, resume_id)
        self.assertEqual(resume.user_id, user_id)
        self.assertEqual(resume.position, "Software Engineer")
        self.db_session.query.assert_called()

    def test_create_resume(self):
        """Test persisting new resume to database"""
        # Arrange
        resume_data = {
            "user_id": 1,
            "name": "Jane Smith",
            "position": "Senior DevOps Engineer",
            "skills": ["Docker", "K8s", "AWS"]
        }
        
        # Act
        self.resume_repo.create(resume_data)
        
        # Assert
        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()

    def test_update_resume_skills(self):
        """Test updating resume skills field"""
        # Arrange
        resume_id = "res_789012"
        user_id = 1
        update_data = {"skills": ["Python", "Django", "Testing", "CI/CD"]}
        
        # Mock existing resume
        self.db_session.query.return_value.filter.return_value.first.return_value = self.test_resume
        
        # Act
        updated_resume = self.resume_repo.update(resume_id, user_id, update_data)
        
        # Assert
        self.assertEqual(updated_resume.skills, update_data["skills"])
        self.db_session.commit.assert_called_once()

    def test_delete_resume(self):
        """Test soft/hard delete resume from database"""
        # Arrange
        resume_id = "res_789012"
        user_id = 1
        
        # Mock existing resume
        self.db_session.query.return_value.filter.return_value.first.return_value = self.test_resume
        
        # Act
        self.resume_repo.delete(resume_id, user_id)
        
        # Assert
        self.db_session.delete.assert_called_once_with(self.test_resume)
        self.db_session.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()

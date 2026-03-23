import pytest
import os
import sys
from datetime import datetime

# Add app directory to system path (adjust based on actual project structure)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

# Test 1: Focus duration calculation logic
def test_calculate_focus_duration():
    """Test the logic of calculating focus duration (minutes)"""
    from utils.focus_calculator import calculate_focus_duration

    # Normal case: start time < end time
    start_time = datetime(2024, 1, 1, 9, 0, 0)
    end_time = datetime(2024, 1, 1, 10, 30, 0)
    assert calculate_focus_duration(start_time, end_time) == 90  # 90 minutes expected

    # Boundary case: start time = end time
    assert calculate_focus_duration(start_time, start_time) == 0

    # Exception case: end time < start time (should raise ValueError)
    with pytest.raises(ValueError):
        calculate_focus_duration(end_time, start_time)

# Test 2: Database connection fixture (reusable for DB-related tests)
@pytest.fixture
def db_connection():
    """Fixture for creating a temporary database connection"""
    import psycopg2
    from dotenv import load_dotenv

    # Load environment variables from example file (test environment)
    load_dotenv(os.path.join(os.path.dirname(__file__), "../.env.example"))
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME")
    )
    yield conn  # Provide connection to test functions
    conn.close()  # Clean up after test

def test_db_connection(db_connection):
    """Test if database connection can be established successfully"""
    cursor = db_connection.cursor()
    cursor.execute("SELECT 1")  # Simple test query
    result = cursor.fetchone()
    assert result == (1,)  # Verify query returns expected result

# Test 3: Daily question attempt insertion logic
def test_add_daily_question_attempt(db_connection):
    """Test inserting daily question attempt records into database"""
    from db.operations import add_question_attempt
    # Test data (valid entry)
    user_id = 1
    question_id = 101
    is_correct = True
    attempt_time = datetime.now()
    # Execute insertion
    attempt_id = add_question_attempt(
        db_connection, user_id, question_id, is_correct, attempt_time
    )

    # Verify insertion success
    cursor = db_connection.cursor()
    cursor.execute("SELECT id FROM daily_question_attempt WHERE id = %s", (attempt_id,))
    assert cursor.fetchone() is not None  # Record should exist

    # Rollback test data to avoid polluting test database
    db_connection.rollback()

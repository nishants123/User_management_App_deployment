"""Pytest configuration and shared fixtures."""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app


@pytest.fixture
def app():
    """Create application for testing."""
    flask_app.config['TESTING'] = True
    flask_app.config['ENV'] = 'test'
    
    yield flask_app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def mock_db_connection():
    """Mock database connection."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {
        'id': 1,
        'name': 'Test User',
        'email': 'test@example.com',
        'phone': '1234567890',
        'created_at': '2026-05-10 12:00:00'
    }


@pytest.fixture
def sample_users(sample_user):
    """Sample list of users."""
    return [
        sample_user,
        {
            'id': 2,
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'phone': '9876543210',
            'created_at': '2026-05-11 10:30:00'
        }
    ]

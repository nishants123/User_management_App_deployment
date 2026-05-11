"""Integration tests for the User Management application with database."""

import pytest
from unittest.mock import patch, MagicMock
import json


@pytest.mark.integration
class TestUserCRUDOperations:
    """Integration tests for complete CRUD operations."""
    
    @patch('app.get_db_connection')
    def test_full_user_lifecycle(self, mock_get_conn, client):
        """Test complete user creation, update, and deletion flow."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Create user
        mock_cursor.lastrowid = 1
        create_response = client.post('/users',
                                     data=json.dumps({
                                         'name': 'Integration Test User',
                                         'email': 'integration@test.com',
                                         'phone': '1234567890'
                                     }),
                                     content_type='application/json')
        
        assert create_response.status_code == 201
        
        # Get user
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'name': 'Integration Test User',
            'email': 'integration@test.com',
            'phone': '1234567890',
            'created_at': '2026-05-11 10:00:00'
        }
        
        get_response = client.get('/users/1')
        assert get_response.status_code == 200
        
        # Update user
        mock_cursor.rowcount = 1
        update_response = client.put('/users/1',
                                    data=json.dumps({
                                        'name': 'Updated User',
                                        'email': 'updated@test.com',
                                        'phone': '9876543210'
                                    }),
                                    content_type='application/json')
        
        assert update_response.status_code == 200
        
        # Delete user
        delete_response = client.delete('/users/1')
        assert delete_response.status_code == 200

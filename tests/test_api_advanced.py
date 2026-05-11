"""Advanced API tests for edge cases and error scenarios."""

import pytest
from unittest.mock import patch, MagicMock
import json
from mysql.connector import Error as MySQLError


class TestAPIEdgeCases:
    """Test API edge cases and boundary conditions."""
    
    @patch('app.get_db_connection')
    def test_create_user_with_empty_phone(self, mock_get_conn, client):
        """Test creating user with empty phone number."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': ''
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        assert response.status_code == 201
    
    @patch('app.get_db_connection')
    def test_create_user_with_whitespace_name(self, mock_get_conn, client):
        """Test creating user with only whitespace in name."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': '   ',
            'email': 'test@example.com'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('app.get_db_connection')
    def test_create_user_without_email(self, mock_get_conn, client):
        """Test creating user without email."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': 'Test User'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        assert response.status_code == 400
    
    @patch('app.get_db_connection')
    def test_create_user_with_special_characters(self, mock_get_conn, client):
        """Test creating user with special characters in name."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': "Test User's Name-123 @#$",
            'email': 'test@example.com'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        assert response.status_code == 201
    
    @patch('app.get_db_connection')
    def test_create_user_with_very_long_name(self, mock_get_conn, client):
        """Test creating user with very long name."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': 'A' * 100,
            'email': 'test@example.com'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        assert response.status_code == 201
    
    @patch('app.get_db_connection')
    def test_create_user_with_unicode_characters(self, mock_get_conn, client):
        """Test creating user with unicode characters."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': '张三 中文名字 अजय',
            'email': 'test@example.com'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        assert response.status_code == 201
    
    @patch('app.get_db_connection')
    def test_update_user_with_partial_data(self, mock_get_conn, client):
        """Test updating user with only some fields."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        update_data = {
            'name': 'Updated Name'
        }
        
        response = client.put('/users/1',
                              data=json.dumps(update_data),
                              content_type='application/json')
        
        assert response.status_code == 200
    
    @patch('app.get_db_connection')
    def test_get_users_with_special_characters_in_response(self, mock_get_conn, client):
        """Test fetching users with special characters in data."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'name': 'Test<User>',
                'email': 'test@example.com',
                'phone': '1234567890',
                'created_at': '2026-05-10 12:00:00'
            }
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.get('/users')
        assert response.status_code == 200


class TestAPIErrorHandling:
    """Test comprehensive error handling in API."""
    
    @patch('app.get_db_connection')
    def test_create_user_db_commit_error(self, mock_get_conn, client):
        """Test handling database commit errors."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.commit.side_effect = MySQLError("Commit failed")
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': 'Test User',
            'email': 'test@example.com'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        assert response.status_code == 500
    
    @patch('app.get_db_connection')
    def test_update_user_db_error(self, mock_get_conn, client):
        """Test update with database error."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = MySQLError("Update failed")
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        update_data = {
            'name': 'Updated',
            'email': 'updated@example.com'
        }
        
        response = client.put('/users/1',
                              data=json.dumps(update_data),
                              content_type='application/json')
        
        assert response.status_code == 500
    
    @patch('app.get_db_connection')
    def test_delete_user_db_error(self, mock_get_conn, client):
        """Test delete with database error."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = MySQLError("Delete failed")
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.delete('/users/1')
        
        assert response.status_code == 500
    
    def test_post_with_invalid_json(self, client):
        """Test POST with invalid JSON payload."""
        response = client.post('/users',
                               data='invalid json',
                               content_type='application/json')
        
        # Flask should return 400 for invalid JSON
        assert response.status_code in [400, 415]
    
    def test_post_with_missing_content_type(self, client):
        """Test POST without content type header."""
        response = client.post('/users',
                               data=json.dumps({
                                   'name': 'Test',
                                   'email': 'test@example.com'
                               }))
        
        # Should handle gracefully
        assert response.status_code in [400, 415, 500]
    
    @patch('app.get_db_connection')
    def test_get_users_with_cursor_close_error(self, mock_get_conn, client):
        """Test when cursor close fails."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.close.side_effect = Exception("Close failed")
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.get('/users')
        # Should still return success even if close fails
        assert response.status_code == 200


class TestAPIValidation:
    """Test comprehensive input validation."""
    
    @patch('app.get_db_connection')
    def test_email_with_multiple_at_signs(self, mock_get_conn, client):
        """Test email validation with multiple @ signs."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': 'Test',
            'email': 'test@@example.com'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        assert response.status_code == 400
    
    @patch('app.get_db_connection')
    def test_email_with_leading_space(self, mock_get_conn, client):
        """Test email with leading space."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': 'Test',
            'email': ' test@example.com'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        assert response.status_code == 400
    
    @patch('app.get_db_connection')
    def test_email_with_trailing_space(self, mock_get_conn, client):
        """Test email with trailing space."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': 'Test',
            'email': 'test@example.com '
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        # Should fail or trim - depends on implementation
        # Currently trims, so should succeed
        assert response.status_code in [400, 201]
    
    @patch('app.get_db_connection')
    def test_create_user_with_null_value(self, mock_get_conn, client):
        """Test creating user with null values."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': None,
            'email': 'test@example.com'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        assert response.status_code == 400
    
    @patch('app.get_db_connection')
    def test_create_user_with_empty_string_email(self, mock_get_conn, client):
        """Test creating user with empty string email."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': 'Test',
            'email': ''
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        assert response.status_code == 400


class TestAPIResponseFormats:
    """Test API response formats and consistency."""
    
    @patch('app.get_db_connection')
    def test_success_response_structure(self, mock_get_conn, client):
        """Test success response has correct structure."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'name': 'Test',
                'email': 'test@example.com',
                'phone': None,
                'created_at': '2026-05-10 12:00:00'
            }
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.get('/users')
        data = json.loads(response.data)
        
        assert 'users' in data
        assert isinstance(data['users'], list)
        assert len(data['users']) > 0
    
    @patch('app.get_db_connection')
    def test_error_response_structure(self, mock_get_conn, client):
        """Test error response has correct structure."""
        mock_get_conn.return_value = None
        
        response = client.get('/users')
        data = json.loads(response.data)
        
        assert 'error' in data
        assert isinstance(data['error'], str)
    
    def test_health_response_format(self, client):
        """Test health endpoint response format."""
        response = client.get('/health')
        data = json.loads(response.data)
        
        assert 'status' in data
        assert data['status'] == 'ok'
        assert response.content_type == 'application/json'

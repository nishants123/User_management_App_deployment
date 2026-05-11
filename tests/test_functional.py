"""Template and rendering tests."""

import pytest
from unittest.mock import patch, MagicMock
import re


class TestTemplateRendering:
    """Test HTML template rendering."""
    
    def test_index_page_returns_html(self, client):
        """Test index page returns HTML content."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data
    
    def test_index_page_contains_head_section(self, client):
        """Test index page has proper head section."""
        response = client.get('/')
        
        assert b'<head>' in response.data or b'<meta' in response.data
        assert b'<title>' in response.data
    
    def test_index_page_contains_body_section(self, client):
        """Test index page has body section."""
        response = client.get('/')
        
        assert b'<body>' in response.data or b'</body>' in response.data
    
    def test_index_page_loads_javascript(self, client):
        """Test index page loads JavaScript files."""
        response = client.get('/')
        
        # Should reference script.js
        assert b'script.js' in response.data or b'.js' in response.data
    
    def test_index_page_loads_css(self, client):
        """Test index page loads CSS files."""
        response = client.get('/')
        
        # Should reference style.css
        assert b'style.css' in response.data or b'.css' in response.data
    
    def test_index_page_content_type(self, client):
        """Test index page has correct content type."""
        response = client.get('/')
        
        assert 'text/html' in response.content_type
    
    def test_index_page_not_empty(self, client):
        """Test index page returns content."""
        response = client.get('/')
        
        assert len(response.data) > 0
        assert len(response.data) > 100  # Should have substantial content


class TestEndToEndScenarios:
    """Test complete end-to-end workflows."""
    
    @patch('app.get_db_connection')
    def test_complete_user_management_flow(self, mock_get_conn, client):
        """Test complete user management workflow."""
        import json
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # 1. Get initial users (empty)
        mock_cursor.fetchall.return_value = []
        response1 = client.get('/users')
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        assert len(data1['users']) == 0
        
        # 2. Create a user
        mock_cursor.lastrowid = 1
        mock_cursor.rowcount = 1
        response2 = client.post('/users',
                               data=json.dumps({
                                   'name': 'John Doe',
                                   'email': 'john@example.com',
                                   'phone': '1234567890'
                               }),
                               content_type='application/json')
        assert response2.status_code == 201
        
        # 3. Get the created user
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'created_at': '2026-05-11 12:00:00'
        }
        response3 = client.get('/users/1')
        assert response3.status_code == 200
        
        # 4. Update the user
        response4 = client.put('/users/1',
                              data=json.dumps({
                                  'name': 'Jane Doe',
                                  'email': 'jane@example.com',
                                  'phone': '9876543210'
                              }),
                              content_type='application/json')
        assert response4.status_code == 200
        
        # 5. Delete the user
        mock_cursor.rowcount = 1
        response5 = client.delete('/users/1')
        assert response5.status_code == 200
    
    @patch('app.get_db_connection')
    def test_health_check_in_workflow(self, mock_get_conn, client):
        """Test health check during workflow."""
        import json
        
        # Check health
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
    
    @patch('app.get_db_connection')
    def test_multiple_users_workflow(self, mock_get_conn, client):
        """Test workflow with multiple users."""
        import json
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Create first user
        mock_cursor.lastrowid = 1
        response1 = client.post('/users',
                               data=json.dumps({
                                   'name': 'User 1',
                                   'email': 'user1@example.com'
                               }),
                               content_type='application/json')
        assert response1.status_code == 201
        
        # Create second user
        mock_cursor.lastrowid = 2
        response2 = client.post('/users',
                               data=json.dumps({
                                   'name': 'User 2',
                                   'email': 'user2@example.com'
                               }),
                               content_type='application/json')
        assert response2.status_code == 201
        
        # Get all users
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'name': 'User 1',
                'email': 'user1@example.com',
                'phone': None,
                'created_at': '2026-05-11 12:00:00'
            },
            {
                'id': 2,
                'name': 'User 2',
                'email': 'user2@example.com',
                'phone': None,
                'created_at': '2026-05-11 12:05:00'
            }
        ]
        response3 = client.get('/users')
        assert response3.status_code == 200
        data = json.loads(response3.data)
        assert len(data['users']) == 2


class TestErrorRecovery:
    """Test error recovery scenarios."""
    
    @patch('app.get_db_connection')
    def test_recovery_after_connection_error(self, mock_get_conn, client):
        """Test system recovery after connection error."""
        import json
        
        # First call fails
        mock_get_conn.return_value = None
        response1 = client.get('/users')
        assert response1.status_code == 500
        
        # Connection restored
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response2 = client.get('/users')
        assert response2.status_code == 200
    
    @patch('app.get_db_connection')
    def test_recovery_after_validation_error(self, mock_get_conn, client):
        """Test recovery after validation error."""
        import json
        
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        # First call - validation error
        response1 = client.post('/users',
                               data=json.dumps({'name': 'Test'}),
                               content_type='application/json')
        assert response1.status_code == 400
        
        # Valid request should work
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        
        with patch('app.write_backup_file'):
            response2 = client.post('/users',
                                   data=json.dumps({
                                       'name': 'Test',
                                       'email': 'test@example.com'
                                   }),
                                   content_type='application/json')
        
        assert response2.status_code == 201


class TestDataConsistency:
    """Test data consistency across operations."""
    
    @patch('app.get_db_connection')
    def test_list_response_format_consistency(self, mock_get_conn, client):
        """Test GET /users always returns consistent format."""
        import json
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Empty list
        mock_cursor.fetchall.return_value = []
        response1 = client.get('/users')
        data1 = json.loads(response1.data)
        assert 'users' in data1
        assert isinstance(data1['users'], list)
        
        # With users
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'name': 'Test', 'email': 'test@example.com',
             'phone': None, 'created_at': '2026-05-11 12:00:00'}
        ]
        response2 = client.get('/users')
        data2 = json.loads(response2.data)
        assert 'users' in data2
        assert isinstance(data2['users'], list)
    
    @patch('app.get_db_connection')
    def test_single_user_response_format(self, mock_get_conn, client):
        """Test GET /users/<id> response format."""
        import json
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'name': 'Test',
            'email': 'test@example.com',
            'phone': None,
            'created_at': '2026-05-11 12:00:00'
        }
        
        response = client.get('/users/1')
        data = json.loads(response.data)
        assert 'user' in data
        assert isinstance(data['user'], dict)


class TestRequestContentTypes:
    """Test different content types in requests."""
    
    @patch('app.get_db_connection')
    def test_json_content_type(self, mock_get_conn, client):
        """Test POST with JSON content type."""
        import json
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        with patch('app.write_backup_file'):
            response = client.post('/users',
                                   data=json.dumps({
                                       'name': 'Test',
                                       'email': 'test@example.com'
                                   }),
                                   content_type='application/json')
        
        assert response.status_code == 201
    
    def test_get_has_no_body(self, client):
        """Test GET requests don't require body."""
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_delete_has_no_body(self, client):
        """Test DELETE requests don't require body."""
        with patch('app.get_db_connection') as mock_get_conn:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.rowcount = 1
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn
            
            with patch('app.write_backup_file'):
                response = client.delete('/users/1')
            
            assert response.status_code == 200

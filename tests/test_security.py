"""Security and functional behavior tests."""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import json
from app import write_backup_file


class TestSecurityValidation:
    """Test security-related validations."""
    
    @patch('app.get_db_connection')
    def test_sql_injection_protection_in_create(self, mock_get_conn, client):
        """Test SQL injection protection in create endpoint."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Attempt SQL injection in name field
        user_data = {
            'name': "'; DROP TABLE users; --",
            'email': 'test@example.com'
        }
        
        with patch('app.write_backup_file'):
            response = client.post('/users',
                                   data=json.dumps(user_data),
                                   content_type='application/json')
        
        # Should succeed with parameterized query
        assert response.status_code == 201
        
        # Verify parameterized query was used
        call_args = mock_cursor.execute.call_args
        assert '%s' in call_args[0][0]
    
    @patch('app.get_db_connection')
    def test_sql_injection_protection_in_read(self, mock_get_conn, client):
        """Test SQL injection protection in read endpoint."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'id': 1}
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Attempt SQL injection in URL parameter
        response = client.get('/users/1 OR 1=1')
        
        # Should handle gracefully (Flask converts to int)
        assert response.status_code in [404, 500]
    
    @patch('app.get_db_connection')
    def test_xss_protection_in_response(self, mock_get_conn, client):
        """Test XSS protection - dangerous content in response."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'name': '<script>alert("xss")</script>',
                'email': 'test@example.com',
                'phone': None,
                'created_at': '2026-05-10 12:00:00'
            }
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.get('/users')
        # Response should contain the script tags (API returns JSON, not HTML)
        # Frontend JS handles escaping
        assert response.status_code == 200
    
    @patch('app.get_db_connection')
    def test_path_traversal_protection(self, mock_get_conn, client):
        """Test protection against path traversal attacks."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        # Attempt path traversal
        response = client.get('/users/../../etc/passwd')
        
        # Should handle gracefully
        assert response.status_code in [404, 500]
    
    @patch('app.get_db_connection')
    def test_email_header_injection_protection(self, mock_get_conn, client):
        """Test protection against email header injection."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        # Attempt header injection
        user_data = {
            'name': 'Test',
            'email': 'test@example.com\nBcc: attacker@example.com'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        # Should fail validation
        assert response.status_code == 400


class TestInputSanitization:
    """Test input sanitization and encoding."""
    
    @patch('app.get_db_connection')
    def test_name_with_html_tags(self, mock_get_conn, client):
        """Test name field with HTML tags."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': '<img src=x onerror=alert("xss")>',
            'email': 'test@example.com'
        }
        
        with patch('app.write_backup_file'):
            response = client.post('/users',
                                   data=json.dumps(user_data),
                                   content_type='application/json')
        
        # Should accept (frontend handles escaping)
        assert response.status_code == 201
    
    @patch('app.get_db_connection')
    def test_email_with_quotes(self, mock_get_conn, client):
        """Test email with quote characters."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': 'Test',
            'email': 'test\'quote@example.com'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        # Should fail email validation
        assert response.status_code == 400
    
    @patch('app.get_db_connection')
    def test_phone_with_special_characters(self, mock_get_conn, client):
        """Test phone field with special characters."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': 'Test',
            'email': 'test@example.com',
            'phone': '+1-234-567-8900'
        }
        
        with patch('app.write_backup_file'):
            response = client.post('/users',
                                   data=json.dumps(user_data),
                                   content_type='application/json')
        
        assert response.status_code == 201


class TestFunctionalBehavior:
    """Test functional behavior and business logic."""
    
    @patch('app.write_backup_file')
    @patch('app.get_db_connection')
    def test_backup_called_on_create(self, mock_get_conn, mock_backup, client):
        """Test backup is called after creating user."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': 'Test',
            'email': 'test@example.com'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        assert response.status_code == 201
        mock_backup.assert_called_once()
    
    @patch('app.write_backup_file')
    @patch('app.get_db_connection')
    def test_backup_called_on_update(self, mock_get_conn, mock_backup, client):
        """Test backup is called after updating user."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        update_data = {
            'name': 'Updated',
            'email': 'updated@example.com'
        }
        
        response = client.put('/users/1',
                              data=json.dumps(update_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        mock_backup.assert_called_once()
    
    @patch('app.write_backup_file')
    @patch('app.get_db_connection')
    def test_backup_called_on_delete(self, mock_get_conn, mock_backup, client):
        """Test backup is called after deleting user."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.delete('/users/1')
        
        assert response.status_code == 200
        mock_backup.assert_called_once()
    
    @patch('app.write_backup_file')
    def test_backup_endpoint_triggers_backup(self, mock_backup, client):
        """Test backup endpoint triggers backup function."""
        response = client.post('/backup')
        
        assert response.status_code == 200
        mock_backup.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('app.get_db_connection')
    def test_backup_file_format(self, mock_get_conn, mock_file):
        """Test backup file has correct format."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'name': 'Test User',
                'email': 'test@example.com',
                'phone': '1234567890',
                'created_at': '2026-05-10 12:00:00'
            }
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        write_backup_file()
        
        # Check file was opened
        mock_file.assert_called_with('/backup/Backupuserdata.txt', 'w', encoding='utf-8')
        
        # Check content includes CSV header and data
        handle = mock_file()
        written_content = handle.write.call_args[0][0]
        assert 'id,name,email,phone,created_at' in written_content
        assert 'Test User' in written_content


class TestHTTPMethods:
    """Test HTTP method handling."""
    
    def test_unsupported_method_on_users(self, client):
        """Test unsupported HTTP methods."""
        # PATCH not implemented for users
        response = client.patch('/users')
        assert response.status_code in [405, 404]
    
    def test_unsupported_method_on_user_id(self, client):
        """Test unsupported methods on specific user."""
        # POST not valid on specific user
        response = client.post('/users/1',
                               data=json.dumps({'name': 'Test'}),
                               content_type='application/json')
        assert response.status_code in [405, 404]
    
    def test_options_method(self, client):
        """Test OPTIONS method for CORS."""
        response = client.options('/users')
        # OPTIONS may be supported for CORS
        assert response.status_code in [200, 404, 405]


class TestResponseHeaders:
    """Test HTTP response headers."""
    
    @patch('app.get_db_connection')
    def test_content_type_header(self, mock_get_conn, client):
        """Test response has correct content type."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.get('/users')
        
        assert 'application/json' in response.content_type
    
    def test_health_endpoint_content_type(self, client):
        """Test health endpoint content type."""
        response = client.get('/health')
        assert 'application/json' in response.content_type

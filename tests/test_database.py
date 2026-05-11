"""Database and performance related tests."""

import pytest
from unittest.mock import patch, MagicMock, call
import json
from mysql.connector import Error as MySQLError


class TestDatabaseOperations:
    """Test database operation behaviors."""
    
    @patch('app.get_db_connection')
    def test_connection_cursor_lifecycle(self, mock_get_conn, client):
        """Test proper cursor and connection lifecycle management."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_get_conn.return_value = mock_conn
        
        response = client.get('/users')
        
        # Verify proper cleanup
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
        assert response.status_code == 200
    
    @patch('app.get_db_connection')
    def test_transaction_rollback_on_error(self, mock_get_conn, client):
        """Test transaction rollback when error occurs."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = MySQLError("Insert error")
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': 'Test',
            'email': 'test@example.com'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        # Verify rollback was called
        mock_conn.rollback.assert_called_once()
        assert response.status_code == 500
    
    @patch('app.get_db_connection')
    def test_transaction_commit_on_success(self, mock_get_conn, client):
        """Test transaction commit on successful operation."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': 'Test',
            'email': 'test@example.com'
        }
        
        with patch('app.write_backup_file'):
            response = client.post('/users',
                                   data=json.dumps(user_data),
                                   content_type='application/json')
        
        # Verify commit was called
        mock_conn.commit.assert_called_once()
        assert response.status_code == 201
    
    @patch('app.get_db_connection')
    def test_parameterized_queries_used(self, mock_get_conn, client):
        """Test that parameterized queries are used (SQL injection protection)."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'id': 1, 'name': 'Test'}
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.get('/users/1')
        
        # Verify execute was called with parameters
        mock_cursor.execute.assert_called()
        call_args = mock_cursor.execute.call_args
        # Should have 2 arguments: SQL and parameters tuple
        assert len(call_args[0]) == 2
        assert '%s' in call_args[0][0]  # Parameterized query
    
    @patch('app.get_db_connection')
    def test_bulk_operations(self, mock_get_conn, client):
        """Test operations with multiple users."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        users = [{'id': i, 'name': f'User {i}', 'email': f'user{i}@example.com',
                  'phone': None, 'created_at': '2026-05-10 12:00:00'} for i in range(100)]
        
        mock_cursor.fetchall.return_value = users
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.get('/users')
        data = json.loads(response.data)
        
        assert len(data['users']) == 100
        assert response.status_code == 200
    
    @patch('app.get_db_connection')
    def test_query_execution_with_none_values(self, mock_get_conn, client):
        """Test query execution when fields have None values."""
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
        
        assert data['users'][0]['phone'] is None
        assert response.status_code == 200


class TestConcurrency:
    """Test concurrent operation scenarios."""
    
    @patch('app.get_db_connection')
    def test_multiple_read_operations(self, mock_get_conn, client):
        """Test multiple concurrent reads."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Simulate multiple concurrent reads
        for _ in range(5):
            response = client.get('/users')
            assert response.status_code == 200
        
        # Verify connection was created multiple times
        assert mock_get_conn.call_count == 5
    
    @patch('app.get_db_connection')
    def test_create_then_read_same_user(self, mock_get_conn, client):
        """Test create operation followed by read."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        # First call for create
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        with patch('app.write_backup_file'):
            create_response = client.post('/users',
                                         data=json.dumps({
                                             'name': 'Test',
                                             'email': 'test@example.com'
                                         }),
                                         content_type='application/json')
        
        assert create_response.status_code == 201
        
        # Reset mocks for read
        mock_cursor.reset_mock()
        mock_conn.reset_mock()
        
        # Now read
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'name': 'Test',
            'email': 'test@example.com',
            'phone': None,
            'created_at': '2026-05-10 12:00:00'
        }
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        read_response = client.get('/users/1')
        assert read_response.status_code == 200


class TestDataIntegrity:
    """Test data integrity and consistency."""
    
    @patch('app.get_db_connection')
    def test_user_id_consistency(self, mock_get_conn, client):
        """Test that user IDs are consistent."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'name': 'User 1', 'email': 'user1@example.com',
             'phone': None, 'created_at': '2026-05-10 12:00:00'},
            {'id': 2, 'name': 'User 2', 'email': 'user2@example.com',
             'phone': None, 'created_at': '2026-05-10 12:00:00'}
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.get('/users')
        data = json.loads(response.data)
        
        assert data['users'][0]['id'] == 1
        assert data['users'][1]['id'] == 2
    
    @patch('app.get_db_connection')
    def test_email_uniqueness_constraint(self, mock_get_conn, client):
        """Test email uniqueness constraint enforcement."""
        from mysql.connector import Error as MySQLError
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = MySQLError("Duplicate entry 'test@example.com' for key 'email'")
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': 'Test',
            'email': 'test@example.com'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'Email already exists' in data['error']
    
    @patch('app.get_db_connection')
    def test_created_at_timestamp_exists(self, mock_get_conn, client):
        """Test that created_at timestamp is present."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'name': 'Test',
            'email': 'test@example.com',
            'phone': None,
            'created_at': '2026-05-10 12:00:00'
        }
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.get('/users/1')
        data = json.loads(response.data)
        
        assert 'created_at' in data['user']
        assert data['user']['created_at'] is not None


class TestDatabaseConnectionPool:
    """Test database connection handling."""
    
    @patch('app.get_db_connection')
    def test_connection_none_handling(self, mock_get_conn, client):
        """Test handling when connection returns None."""
        mock_get_conn.return_value = None
        
        response = client.get('/users')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'Database connection failed' in data['error']
    
    @patch('app.get_db_connection')
    def test_connection_exception_handling(self, mock_get_conn, client):
        """Test handling when connection raises exception."""
        mock_get_conn.side_effect = MySQLError("Connection refused")
        
        response = client.get('/users')
        assert response.status_code == 500
    
    @patch('app.get_db_connection')
    def test_cursor_creation_failure(self, mock_get_conn, client):
        """Test handling when cursor creation fails."""
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = MySQLError("Cursor creation failed")
        mock_get_conn.return_value = mock_conn
        
        response = client.get('/users')
        assert response.status_code == 500

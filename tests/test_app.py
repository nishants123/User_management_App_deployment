"""Tests for the User Management Flask application."""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import json
from app import validate_email, write_backup_file


class TestValidateEmail:
    """Test email validation function."""
    
    def test_valid_email(self):
        """Test with valid email format."""
        assert validate_email('test@example.com') is True
        assert validate_email('user.name+tag@example.co.uk') is True
        assert validate_email('john_doe@company.org') is True
    
    def test_invalid_email(self):
        """Test with invalid email format."""
        assert validate_email('invalid.email') is False
        assert validate_email('test@') is False
        assert validate_email('@example.com') is False
        assert validate_email('test@example') is False
        assert validate_email('test@.com') is False
        assert validate_email('') is False


class TestHealthEndpoint:
    """Test the health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint returns 200."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'


class TestGetUsersEndpoint:
    """Test GET /users endpoint."""
    
    @patch('app.get_db_connection')
    def test_get_users_success(self, mock_get_conn, client, sample_users):
        """Test successfully fetching all users."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = sample_users
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.get('/users')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'users' in data
        assert len(data['users']) == 2
        assert data['users'][0]['email'] == 'test@example.com'
    
    @patch('app.get_db_connection')
    def test_get_users_no_users(self, mock_get_conn, client):
        """Test fetching users when no users exist."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.get('/users')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['users'] == []
    
    @patch('app.get_db_connection')
    def test_get_users_db_connection_failed(self, mock_get_conn, client):
        """Test when database connection fails."""
        mock_get_conn.return_value = None
        
        response = client.get('/users')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Database connection failed'


class TestGetUserByIdEndpoint:
    """Test GET /users/<id> endpoint."""
    
    @patch('app.get_db_connection')
    def test_get_user_by_id_success(self, mock_get_conn, client, sample_user):
        """Test fetching a specific user by ID."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = sample_user
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.get('/users/1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['id'] == 1
        assert data['user']['email'] == 'test@example.com'
    
    @patch('app.get_db_connection')
    def test_get_user_by_id_not_found(self, mock_get_conn, client):
        """Test when user ID doesn't exist."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.get('/users/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'User not found'
    
    @patch('app.get_db_connection')
    def test_get_user_by_id_db_error(self, mock_get_conn, client):
        """Test when database error occurs."""
        mock_get_conn.return_value = None
        
        response = client.get('/users/1')
        assert response.status_code == 500


class TestCreateUserEndpoint:
    """Test POST /users endpoint."""
    
    @patch('app.write_backup_file')
    @patch('app.get_db_connection')
    def test_create_user_success(self, mock_get_conn, mock_backup, client):
        """Test successfully creating a new user."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'phone': '5555555555'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'message' in data
        assert data['message'] == 'User created'
        assert data['user_id'] == 1
        mock_backup.assert_called_once()
    
    @patch('app.get_db_connection')
    def test_create_user_missing_name(self, mock_get_conn, client):
        """Test creating user without name."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'email': 'newuser@example.com'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('app.get_db_connection')
    def test_create_user_invalid_email(self, mock_get_conn, client):
        """Test creating user with invalid email."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': 'Test User',
            'email': 'invalid-email'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Invalid email format'
    
    @patch('app.write_backup_file')
    @patch('app.get_db_connection')
    def test_create_user_duplicate_email(self, mock_get_conn, mock_backup, client):
        """Test creating user with duplicate email."""
        from mysql.connector import Error as MySQLError
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = MySQLError("Duplicate entry 'test@example.com'")
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        user_data = {
            'name': 'Duplicate User',
            'email': 'test@example.com'
        }
        
        response = client.post('/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'Email already exists' in data['error']


class TestUpdateUserEndpoint:
    """Test PUT /users/<id> endpoint."""
    
    @patch('app.write_backup_file')
    @patch('app.get_db_connection')
    def test_update_user_success(self, mock_get_conn, mock_backup, client):
        """Test successfully updating a user."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        update_data = {
            'name': 'Updated User',
            'email': 'updated@example.com',
            'phone': '1111111111'
        }
        
        response = client.put('/users/1',
                              data=json.dumps(update_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'User updated'
        mock_backup.assert_called_once()
    
    @patch('app.get_db_connection')
    def test_update_user_not_found(self, mock_get_conn, client):
        """Test updating non-existent user."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        update_data = {
            'name': 'Updated User',
            'email': 'updated@example.com'
        }
        
        response = client.put('/users/999',
                              data=json.dumps(update_data),
                              content_type='application/json')
        
        assert response.status_code == 404


class TestDeleteUserEndpoint:
    """Test DELETE /users/<id> endpoint."""
    
    @patch('app.write_backup_file')
    @patch('app.get_db_connection')
    def test_delete_user_success(self, mock_get_conn, mock_backup, client):
        """Test successfully deleting a user."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.delete('/users/1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'User deleted'
        mock_backup.assert_called_once()
    
    @patch('app.get_db_connection')
    def test_delete_user_not_found(self, mock_get_conn, client):
        """Test deleting non-existent user."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.delete('/users/999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'User not found'


class TestBackupEndpoint:
    """Test POST /backup endpoint."""
    
    @patch('app.write_backup_file')
    def test_backup_endpoint(self, mock_backup, client):
        """Test backup endpoint triggers backup file write."""
        response = client.post('/backup')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Backup file updated'
        mock_backup.assert_called_once()


class TestIndexRoute:
    """Test GET / endpoint."""
    
    def test_index_route(self, client):
        """Test index route renders HTML."""
        response = client.get('/')
        assert response.status_code == 200
        # Check if it's HTML
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data


class TestWriteBackupFile:
    """Test write_backup_file function."""
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('app.get_db_connection')
    def test_write_backup_file_with_users(self, mock_get_conn, mock_file, sample_users):
        """Test writing backup file with user data."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = sample_users
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        write_backup_file()
        
        # Check if file was opened for writing
        mock_file.assert_called_with('/backup/Backupuserdata.txt', 'w', encoding='utf-8')
        
        # Check if write was called
        handle = mock_file()
        assert handle.write.called
    
    @patch('builtins.open', new_callable=mock_open)
    def test_write_backup_file_with_data(self, mock_file, sample_users):
        """Test backup file content format."""
        write_backup_file(users=sample_users)
        
        mock_file.assert_called_with('/backup/Backupuserdata.txt', 'w', encoding='utf-8')
        handle = mock_file()
        handle.write.assert_called_once()
        
        # Get the content that was written
        written_content = handle.write.call_args[0][0]
        
        # Check headers
        assert 'id,name,email,phone,created_at' in written_content
        # Check user data
        assert 'Test User' in written_content
        assert 'test@example.com' in written_content

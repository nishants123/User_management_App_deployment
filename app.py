from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
from config import Config
import re
import logging

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return connection
    except mysql.connector.Error as err:
        logger.error(f"Database connection failed: {err}")
        return None

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Get all users
@app.route('/users', methods=['GET'])
def get_users():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        return jsonify({'users': users}), 200
    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({'error': 'Failed to fetch users'}), 500
    finally:
        cursor.close()
        connection.close()

# Get user by ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        if user:
            return jsonify({'user': user}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({'error': 'Failed to fetch user'}), 500
    finally:
        cursor.close()
        connection.close()

# Create new user
@app.route('/users', methods=['POST'])
def create_user():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({'error': 'Name and email are required'}), 400
    
    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if len(data['name'].strip()) == 0:
        return jsonify({'error': 'Name cannot be empty'}), 400
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO users (name, email, phone) VALUES (%s, %s, %s)',
            (data['name'], data['email'], data.get('phone', ''))
        )
        connection.commit()
        user_id = cursor.lastrowid
        return jsonify({'message': 'User created', 'user_id': user_id}), 201
    except mysql.connector.Error as e:
        connection.rollback()
        logger.error(f"Database error: {e}")
        if 'Duplicate entry' in str(e):
            return jsonify({'error': 'Email already exists'}), 409
        return jsonify({'error': 'Failed to create user'}), 500
    finally:
        cursor.close()
        connection.close()

# Update user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    data = request.get_json()
    
    # Validate email if provided
    if data.get('email') and not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            'UPDATE users SET name = %s, email = %s, phone = %s WHERE id = %s',
            (data.get('name'), data.get('email'), data.get('phone'), user_id)
        )
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'message': 'User updated'}), 200
    except mysql.connector.Error as e:
        connection.rollback()
        logger.error(f"Database error: {e}")
        if 'Duplicate entry' in str(e):
            return jsonify({'error': 'Email already exists'}), 409
        return jsonify({'error': 'Failed to update user'}), 500
    finally:
        cursor.close()
        connection.close()

# Delete user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'message': 'User deleted'}), 200
    except mysql.connector.Error as e:
        connection.rollback()
        logger.error(f"Database error: {e}")
        return jsonify({'error': 'Failed to delete user'}), 500
    finally:
        cursor.close()
        connection.close()

# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

# Serve frontend
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

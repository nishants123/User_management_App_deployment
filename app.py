from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
from config import Config

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

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
        print(f"Database connection failed: {err}")
        return None

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
        cursor.close()
        connection.close()
        return jsonify({'users': users}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        cursor.close()
        connection.close()
        
        if user:
            return jsonify({'user': user}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create new user
@app.route('/users', methods=['POST'])
def create_user():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({'error': 'Name and email are required'}), 400
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO users (name, email, phone) VALUES (%s, %s, %s)',
            (data['name'], data['email'], data.get('phone', ''))
        )
        connection.commit()
        user_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        return jsonify({'message': 'User created', 'user_id': user_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    data = request.get_json()
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            'UPDATE users SET name = %s, email = %s, phone = %s WHERE id = %s',
            (data.get('name'), data.get('email'), data.get('phone'), user_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'message': 'User updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        cursor.close()
        connection.close()
        
        return jsonify({'message': 'User deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

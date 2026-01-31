from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from models import DB, get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"success": False, "message": "Credentials required"}), 400

    username = data.get('username')
    password = data.get('password')

    # RBAC Check
    user = DB.query('SELECT * FROM users WHERE username = ?', (username,), one=True)

    if user and check_password_hash(user['password_hash'], password):
        # Generate Token (Mock for now, JWT recommended for production)
        import secrets
        token = secrets.token_hex(16)
        
        # Log Logic
        DB.log_activity(user['id'], user['username'], 'LOGIN', 'User logged in')

        return jsonify({
            "success": True, 
            "token": token,
            "username": user['username'],
            "role": user['role']
        })
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

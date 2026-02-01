from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User, log_activity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"success": False, "message": "Credentials required"}), 400

    username = data.get('username')
    password = data.get('password')

    # RBAC Check
    try:
        user = User.query.filter_by(username=username).first()
    except Exception as e:
        return jsonify({"success": False, "message": f"Database Error: {str(e)}"}), 500

    if not user:
         return jsonify({"success": False, "message": "User not found"}), 404

    if check_password_hash(user.password_hash, password):
        # Generate Token
        import secrets
        token = secrets.token_hex(16)
        
        # Log Logic
        log_activity(user.id, user.username, 'LOGIN', 'User logged in')

        return jsonify({
            "success": True, 
            "token": token,
            "username": user.username,
            "role": user.role
        })
    else:
        return jsonify({"success": False, "message": "Incorrect Password"}), 401

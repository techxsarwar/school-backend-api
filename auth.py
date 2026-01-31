from flask import Blueprint, request, jsonify, current_app

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'password' not in data:
        return jsonify({"success": False, "message": "Credentials required"}), 400

    username = data.get('username')
    password = data.get('password')

    admin_user = current_app.config.get('ADMIN_USER')
    admin_pass = current_app.config.get('ADMIN_PASS')

    # Basic check
    if username == admin_user and password == admin_pass:
        return jsonify({"success": True, "token": "access_granted_token_123"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

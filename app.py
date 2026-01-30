import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS to allow requests from your frontend
CORS(app)

# --- HARDCODED CREDENTIALS ---
ADMIN_PASS = "sarwar123"

# ---------------------------------------------------------
# ✅ NEW: The "Front Door" (Fixes the 404 Error)
# ---------------------------------------------------------
@app.route('/')
def home():
    return "Server is Running! 🚀 Sarwar's API is Live."

# ---------------------------------------------------------
# 🔐 Login Route
# ---------------------------------------------------------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    
    if not data or 'password' not in data:
        return jsonify({"success": False, "message": "Password required"}), 400

    user_password = data['password']

    if user_password == ADMIN_PASS:
        return jsonify({
            "success": True, 
            "token": "secret_session_key_777_access_granted" 
        })
    else:
        return jsonify({"success": False, "message": "Invalid credentials"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
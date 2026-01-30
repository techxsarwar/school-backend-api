from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS to allow requests from your frontend (adjust origins in production)
CORS(app)

# --- HARDCODED CREDENTIALS ---
# This variable remains on the server and is never sent to the client.
# It is invisible to "Inspect Element" or browser network tools.
ADMIN_PASS = "sarwar123"

@app.route('/api/login', methods=['POST'])
def login():
    """
    Receives JSON payload: { "password": "..." }
    Compares it with ADMIN_PASS.
    Returns a success token if matched.
    """
    data = request.json
    
    # Check if 'password' key exists in the request
    if not data or 'password' not in data:
        return jsonify({"success": False, "message": "Password required"}), 400

    user_password = data['password']

    # Security Check
    if user_password == ADMIN_PASS:
        # Success: Return a token (in a real app, generate a JWT or session ID)
        return jsonify({
            "success": True, 
            "token": "secret_session_key_777_access_granted" 
        })
    else:
        # Failure: Return false, do not hint why
        return jsonify({"success": False, "message": "Invalid credentials"})

import os

if __name__ == '__main__':
    # Run the server on port provided by OS or 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

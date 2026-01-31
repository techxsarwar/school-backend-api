import os
import sys
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from models import get_db, close_connection, init_db, DB
from auth import auth_bp
from functools import wraps
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['ADMIN_USER'] = "admin"
app.config['ADMIN_PASS'] = "sarwar123"

CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp)

# Database Teardown
@app.teardown_appcontext
def shutdown_session(exception=None):
    close_connection(exception)

# Initialize DB
# Start DB with detailed error handling
try:
    if not os.path.exists("site_data.db"):
        print(" * Database file not found. Initializing...")
        init_db(app)
    else:
        print(" * Database found. Verifying schema...")
        init_db(app)
except Exception as e:
    import traceback
    print("CRITICAL STARTUP ERROR:", file=sys.stderr)
    traceback.print_exc()
    print("The application may fail to start.", file=sys.stderr)

# --- ROUTES ---

# --- RBAC DECORATOR ---
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # In a real app, verify token and get user role from it.
            # Here we simulate by checking a header 'X-Role' sent from frontend
            # This is NOT SECURE for production but fits the current scope without JWT setup.
            user_role = request.headers.get('X-Role', 'Guest')
            
            if 'Admin' in allowed_roles and user_role == 'Admin':
                return f(*args, **kwargs)
            
            if user_role in allowed_roles:
                return f(*args, **kwargs)
            
            return jsonify({"success": False, "message": "Access Denied"}), 403
        return decorated_function
    return decorator

@app.route('/')
def home():
    return "Server is Running! 🚀 Sarwar's CMS API is Live."

# 🏥 SYSTEM HEALTH
@app.route('/api/system-health', methods=['GET'])
def system_health():
    try:
        db = get_db()
        db.execute('SELECT 1')
        db_status = "OK"
    except:
        db_status = "Error"
    
    return jsonify({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "db_status": db_status,
        "server_status": "Online"
    })

# 🗑 CLEAR LOGS
@app.route('/api/logs', methods=['DELETE'])
def clear_logs():
    db = get_db()
    db.execute('DELETE FROM visits')
    db.commit()
    return jsonify({"success": True, "message": "Analytics cleared"})

# 📥 EXPORT CONTACTS
@app.route('/api/export-contacts', methods=['GET'])
def export_contacts():
    rows = DB.query('SELECT name, email, timestamp FROM messages')
    
    output = "Name,Email,Timestamp\n"
    for row in rows:
        output += f"{row['name']},{row['email']},{row['timestamp']}\n"
    
    from flask import Response
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=contacts.csv"}
    )

# 📊 STATS
@app.route('/api/stats', methods=['GET'])
def get_stats():
    # Using Generic Query Helper for cleanliness, though raw SQL is fine
    total_visits = DB.query('SELECT COUNT(*) FROM visits', one=True)[0]
    mobile_visits = DB.query('SELECT COUNT(*) FROM visits WHERE device_type = "mobile"', one=True)[0]
    desktop_visits = total_visits - mobile_visits
    
    unread_messages = DB.query('SELECT COUNT(*) FROM messages WHERE read_status = 0', one=True)[0]
    total_messages = DB.query('SELECT COUNT(*) FROM messages', one=True)[0]
    active_ads = DB.query('SELECT COUNT(*) FROM ads WHERE is_active = 1', one=True)[0]
    live_projects = DB.query('SELECT COUNT(*) FROM projects WHERE status = "Live"', one=True)[0]
    
    recent_visitors = [dict(row) for row in DB.query('SELECT * FROM visits ORDER BY timestamp DESC LIMIT 10')]

    return jsonify({
        "total_visits": total_visits,
        "device_split": {"mobile": mobile_visits, "desktop": desktop_visits},
        "total_messages": total_messages,
        "unread_messages": unread_messages,
        "active_ads": active_ads,
        "live_projects": live_projects,
        "recent_visitors": recent_visitors
    })

# 🛤 TRACK VISIT
@app.route('/api/track-visit', methods=['POST'])
def track_visit():
    data = request.json
    page = data.get('page', 'unknown')
    user_agent = request.headers.get('User-Agent', '').lower()
    device_type = 'mobile' if 'mobile' in user_agent else 'desktop'

    db = get_db()
    db.execute('INSERT INTO visits (page, device_type) VALUES (?, ?)', (page, device_type))
    db.commit()
    return jsonify({"success": True})

# 📢 ADS MANAGER
@app.route('/api/ads', methods=['GET', 'POST', 'DELETE'])
@role_required(['Admin', 'Editor'])
def manage_ads():
    if request.method == 'GET':
        cursor = get_db().execute('SELECT * FROM ads ORDER BY id DESC')
        return jsonify([dict(row) for row in cursor.fetchall()])

    if request.method == 'POST':
        data = request.json
        title = data.get('title') or data.get('headline') or 'Untitled Ad'
        image_url = data.get('image_url') or data.get('image') or ''
        link_url = data.get('link_url') or data.get('link') or '#'
        
        get_db().execute('INSERT INTO ads (title, image_url, link_url) VALUES (?, ?, ?)', (title, image_url, link_url))
        get_db().commit()
        return jsonify({"success": True, "message": "Ad Created"})

    if request.method == 'DELETE':
        get_db().execute('DELETE FROM ads WHERE id = ?', (request.args.get('id'),))
        get_db().commit()
        return jsonify({"success": True, "message": "Ad Deleted"})

# 🎟 COUPONS
@app.route('/api/coupons', methods=['GET', 'POST'])
@role_required(['Admin', 'Editor'])
def manage_coupons():
    if request.method == 'GET':
        cursor = get_db().execute('SELECT * FROM coupons ORDER BY id DESC')
        return jsonify([dict(row) for row in cursor.fetchall()])

    if request.method == 'POST':
        import random, string
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        discount = request.json.get('discount', '10% OFF')

        get_db().execute('INSERT INTO coupons (code, discount) VALUES (?, ?)', (code, discount))
        get_db().commit()
        return jsonify({"success": True, "code": code, "discount": discount})

# 💬 MESSAGES
@app.route('/api/messages', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_messages():
    if request.method == 'GET':
        rows = DB.get_all_messages()
        return jsonify([dict(row) for row in rows])

    if request.method == 'POST':
        data = request.json
        get_db().execute('INSERT INTO messages (name, email, message) VALUES (?, ?, ?)', 
                         (data.get('name'), data.get('email'), data.get('message')))
        get_db().commit()
        return jsonify({"success": True, "message": "Message sent!"})

    if request.method == 'PUT':
        data = request.json
        get_db().execute('UPDATE messages SET read_status = ? WHERE id = ?', (data.get('read_status', 1), data.get('id')))
        get_db().commit()
        return jsonify({"success": True})

    if request.method == 'DELETE':
        get_db().execute('DELETE FROM messages WHERE id = ?', (request.args.get('id'),))
        get_db().commit()
        return jsonify({"success": True})

# ⚙️ SETTINGS
@app.route('/api/settings', methods=['GET', 'POST'])
@role_required(['Admin', 'Developer'])
def manage_settings():
    if request.method == 'GET':
        cursor = get_db().execute('SELECT * FROM settings')
        return jsonify({row['key']: row['value'] for row in cursor.fetchall()})

    if request.method == 'POST':
        for key, value in request.json.items():
            val_str = str(value).lower() if isinstance(value, bool) else str(value)
            DB.save_setting(key, val_str)
        return jsonify({"success": True, "message": "Settings updated"})

# 🌟 TESTIMONIALS & POSTS
@app.route('/api/testimonials', methods=['GET', 'POST', 'DELETE'])
@role_required(['Admin', 'Editor'])
def manage_testimonials():
    if request.method == 'GET':
        return jsonify([dict(row) for row in DB.query('SELECT * FROM testimonials ORDER BY id DESC')])
    if request.method == 'POST':
        d = request.json
        get_db().execute('INSERT INTO testimonials (name, role, review_text, rating, image_url) VALUES (?,?,?,?,?)',
                   (d.get('name'), d.get('role'), d.get('review_text'), d.get('rating'), d.get('image_url')))
        get_db().commit()
        return jsonify({"success": True})
    if request.method == 'DELETE':
        get_db().execute('DELETE FROM testimonials WHERE id = ?', (request.args.get('id'),))
        get_db().commit()
        return jsonify({"success": True})

@app.route('/api/posts', methods=['GET', 'POST', 'DELETE'])
@role_required(['Admin', 'Editor'])
def manage_posts():
    if request.method == 'GET':
        return jsonify([dict(row) for row in DB.query('SELECT * FROM posts ORDER BY id DESC')])
    if request.method == 'POST':
        d = request.json
        date_posted = d.get('date_posted') or datetime.now().strftime("%Y-%m-%d")
        get_db().execute('INSERT INTO posts (title, content, image_url, date_posted, status) VALUES (?,?,?,?,?)',
                   (d.get('title'), d.get('content'), d.get('image_url'), date_posted, d.get('status', 'Published')))
        get_db().commit()
        return jsonify({"success": True})
    if request.method == 'DELETE':
        get_db().execute('DELETE FROM posts WHERE id = ?', (request.args.get('id'),))
        get_db().commit()
        return jsonify({"success": True})

# 🚀 PROJECTS
@app.route('/api/projects', methods=['GET', 'POST', 'PUT', 'DELETE'])
@role_required(['Admin', 'Developer'])
def manage_projects():
    if request.method == 'GET':
        return jsonify([dict(row) for row in DB.query('SELECT * FROM projects ORDER BY priority DESC, id DESC')])
    
    if request.method == 'POST':
        d = request.json
        get_db().execute('INSERT INTO projects (title, image_url, link_url, tags, description, status, priority) VALUES (?,?,?,?,?,?,?)',
                   (d.get('title'), d.get('image_url'), d.get('link_url'), d.get('tags'), d.get('description'), d.get('status', 'Live'), d.get('priority', 0)))
        get_db().commit()
        return jsonify({"success": True})
    
    if request.method == 'PUT':
        d = request.json
        if 'status' in d:
             get_db().execute('UPDATE projects SET status = ?, last_checked = CURRENT_TIMESTAMP WHERE id = ?', (d['status'], d['id']))
        if 'priority' in d:
             get_db().execute('UPDATE projects SET priority = ? WHERE id = ?', (d['priority'], d['id']))
        get_db().commit()
        return jsonify({"success": True})

    if request.method == 'DELETE':
        get_db().execute('DELETE FROM projects WHERE id=?', (request.args.get('id'),))
        get_db().commit()
        return jsonify({"success": True})

# 📈 LEADS
@app.route('/api/leads', methods=['POST'])
def log_lead():
    d = request.json
    get_db().execute('INSERT INTO leads (plan_name) VALUES (?)', (d.get('plan_name'),))
    get_db().commit()
    return jsonify({"success": True, "message": "Lead logged"})

# 👥 TEAM MANAGEMENT
@app.route('/api/team', methods=['GET'])
@role_required(['Admin'])
def get_team():
    users = DB.query('SELECT id, username, email, role, joined_date FROM users')
    return jsonify([dict(u) for u in users])

@app.route('/api/team/invite', methods=['POST'])
@role_required(['Admin'])
def invite_user():
    d = request.json
    try:
        # Default pass: welcome123
        p_hash = generate_password_hash("welcome123")
        get_db().execute('INSERT INTO users (username, email, role, password_hash) VALUES (?, ?, ?, ?)',
                         (d['username'], d['email'], d['role'], p_hash))
        get_db().commit()
        
        # Log it
        username = request.headers.get('X-User', 'Admin')
        # We need a user_id here but for simplicity just logging static user 1 (Admin) or finding it
        # Skipping user_id for now or using 1
        DB.log_activity(1, username, 'INVITE', f"Invited user {d['username']}")
        
        return jsonify({"success": True, "message": "User invited (Pass: welcome123)"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/api/activity', methods=['GET'])
@role_required(['Admin'])
def get_activity():
    rows = DB.query('SELECT * FROM activity_log ORDER BY id DESC LIMIT 50')
    return jsonify([dict(r) for r in rows])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
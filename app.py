import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, g
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- CONFIG ---
DB_FILE = "site_data.db"
ADMIN_USER = "admin"
ADMIN_PASS = "sarwar123"

# --- DATABASE SETUP ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_FILE)
        db.row_factory = sqlite3.Row  # Return rows as dictionaries (kinda)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # 1. Visits Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page TEXT,
                device_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 6. Messages Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                read_status INTEGER DEFAULT 0
            )
        ''')

        # 7. Testimonials, 8. Projects, 9. Posts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS testimonials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                role TEXT,
                review_text TEXT,
                rating INTEGER,
                image_url TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                image_url TEXT,
                link_url TEXT,
                tags TEXT,
                description TEXT,
                status TEXT DEFAULT 'Live',
                last_checked DATETIME DEFAULT CURRENT_TIMESTAMP,
                priority INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                image_url TEXT,
                date_posted TEXT DEFAULT CURRENT_DATE,
                status TEXT DEFAULT 'Published'
            )
        ''')

        # Schema Migration Helper
        def add_col(table, col, type_def):
            try:
                cursor.execute(f"SELECT {col} FROM {table} LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {type_def}")

        # Run Migrations
        add_col('messages', 'read_status', 'INTEGER DEFAULT 0')
        add_col('projects', 'status', "TEXT DEFAULT 'Live'")
        add_col('projects', 'last_checked', "DATETIME DEFAULT CURRENT_TIMESTAMP")
        add_col('projects', 'priority', "INTEGER DEFAULT 0")
        add_col('posts', 'status', "TEXT DEFAULT 'Published'")

        # Seed default settings if not exist
        defaults = {
            "announcement_text": "Welcome to my official portfolio!",
            "announcement_active": "0",
            "announcement_type": "bar",
            "announcement_color": "#000000",
            "announcement_position": "top",
            "maintenance_mode": "0",
            "maintenance_end_time": "null",
            "profile_name": "Sarwar Altaf",
            "profile_headline": "Building digital empires and merging High Performance Code with Premium Aesthetics.",
            "profile_about": "Started my journey with nothing but Notepad and curiosity. Wrote my first lines of code, fascinated by the ability to create something from nothing.",
            "resume_link": "#",
            "site_title": "Sarwar Altaf Dar | Full Stack Developer",
            "meta_description": "Based in India, Sarwar Altaf Dar is a 17-year-old Full Stack Web Developer building the future of the web.",
            "meta_keywords": "Full Stack, Web Developer, Portfolio, Python, React, JavaScript",
            "social_github": "#",
            "social_linkedin": "#",
            "social_instagram": "#",
            "social_twitter": "#",
            "quick_note": ""
        }
        for key, val in defaults.items():
            cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, val))

        db.commit()

# Initialize DB on start
if not os.path.exists(DB_FILE):
    init_db()
else:
    # Run init anyway to ensure new tables are added if schema changes
    init_db()


# --- ROUTES ---

@app.route('/')
def home():
    return "Server is Running! 🚀 Sarwar's CMS API is Live."

# 🔐 LOGIN
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'password' not in data:
        return jsonify({"success": False, "message": "Credentials required"}), 400

    username = data.get('username')
    password = data.get('password')

    # Basic check - in production use a DB and hash passwords!
    if username == ADMIN_USER and password == ADMIN_PASS:
        return jsonify({"success": True, "token": "access_granted_token_123"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401


# 🏥 SYSTEM HEALTH (New)
@app.route('/api/system-health', methods=['GET'])
def system_health():
    try:
        db = get_db()
        db.execute('SELECT 1') # Ping DB
        db_status = "OK"
    except:
        db_status = "Error"
    
    return jsonify({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "db_status": db_status,
        "server_status": "Online"
    })


# � CLEAR LOGS (New)
@app.route('/api/logs', methods=['DELETE'])
def clear_logs():
    db = get_db()
    db.execute('DELETE FROM visits')
    db.commit()
    return jsonify({"success": True, "message": "Analytics cleared"})


# 📥 EXPORT CONTACTS (New)
@app.route('/api/export-contacts', methods=['GET'])
def export_contacts():
    db = get_db()
    cursor = db.execute('SELECT name, email, timestamp FROM messages')
    rows = cursor.fetchall()
    
    # Simple CSV construction
    output = "Name,Email,Timestamp\n"
    for row in rows:
        output += f"{row['name']},{row['email']},{row['timestamp']}\n"
    
    from flask import Response
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=contacts.csv"}
    )


# �📊 STATS (DASHBOARD)
@app.route('/api/stats', methods=['GET'])
def get_stats():
    db = get_db()
    cursor = db.cursor()

    # Total Visits
    cursor.execute('SELECT COUNT(*) FROM visits')
    total_visits = cursor.fetchone()[0]

    # Mobile vs Desktop
    cursor.execute('SELECT COUNT(*) FROM visits WHERE device_type = "mobile"')
    mobile_visits = cursor.fetchone()[0]
    desktop_visits = total_visits - mobile_visits

    # Unread Messages
    cursor.execute('SELECT COUNT(*) FROM messages WHERE read_status = 0')
    unread_messages = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM messages')
    total_messages = cursor.fetchone()[0]

    # Active Ads
    cursor.execute('SELECT COUNT(*) FROM ads WHERE is_active = 1')
    active_ads = cursor.fetchone()[0]
    
    # Live Projects
    cursor.execute('SELECT COUNT(*) FROM projects WHERE status = "Live"')
    live_projects = cursor.fetchone()[0]

    # Recent Visitors (Last 10)
    cursor.execute('SELECT * FROM visits ORDER BY timestamp DESC LIMIT 10')
    recent_visitors = [dict(row) for row in cursor.fetchall()]

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
    
    # Simple device detection from User-Agent
    user_agent = request.headers.get('User-Agent', '').lower()
    device_type = 'mobile' if 'mobile' in user_agent else 'desktop'

    db = get_db()
    db.execute('INSERT INTO visits (page, device_type) VALUES (?, ?)', (page, device_type))
    db.commit()
    
    return jsonify({"success": True})


# 📢 ADS MANAGER
@app.route('/api/ads', methods=['GET', 'POST', 'DELETE'])
def manage_ads():
    db = get_db()
    
    if request.method == 'GET':
        cursor = db.execute('SELECT * FROM ads ORDER BY id DESC')
        ads = [dict(row) for row in cursor.fetchall()]
        return jsonify(ads)

    if request.method == 'POST':
        data = request.json
        # Aliases for robust handling
        title = data.get('title') or data.get('headline') or 'Untitled Ad'
        image_url = data.get('image_url') or data.get('image') or ''
        link_url = data.get('link_url') or data.get('link') or '#'
        
        db.execute('INSERT INTO ads (title, image_url, link_url) VALUES (?, ?, ?)', 
                   (title, image_url, link_url))
        db.commit()
        return jsonify({"success": True, "message": "Ad Created"})

    if request.method == 'DELETE':
        ad_id = request.args.get('id')
        db.execute('DELETE FROM ads WHERE id = ?', (ad_id,))
        db.commit()
        return jsonify({"success": True, "message": "Ad Deleted"})


# 🎟 COUPONS
@app.route('/api/coupons', methods=['GET', 'POST'])
def manage_coupons():
    db = get_db()
    
    if request.method == 'GET':
        cursor = db.execute('SELECT * FROM coupons ORDER BY id DESC')
        coupons = [dict(row) for row in cursor.fetchall()]
        return jsonify(coupons)

    if request.method == 'POST':
        # Generate random code if not provided
        import random, string
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        discount = request.json.get('discount', '10% OFF')

        db.execute('INSERT INTO coupons (code, discount) VALUES (?, ?)', (code, discount))
        db.commit()
        return jsonify({"success": True, "code": code, "discount": discount})


# 💬 MESSAGES (CONTACT FORM)
@app.route('/api/messages', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_messages():
    db = get_db()

    if request.method == 'GET':
        # Sort unread first, then by date
        cursor = db.execute('SELECT * FROM messages ORDER BY read_status ASC, timestamp DESC')
        msgs = [dict(row) for row in cursor.fetchall()]
        return jsonify(msgs)

    if request.method == 'POST':
        data = request.json
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not name or not message:
             return jsonify({"success": False, "message": "Name and Message required"}), 400

        db.execute('INSERT INTO messages (name, email, message) VALUES (?, ?, ?)', (name, email, message))
        db.commit()
        return jsonify({"success": True, "message": "Message sent!"})

    # PUT: Toggle Read Status
    if request.method == 'PUT':
        msg_id = request.json.get('id')
        status = request.json.get('read_status', 1)
        db.execute('UPDATE messages SET read_status = ? WHERE id = ?', (status, msg_id))
        db.commit()
        return jsonify({"success": True})

    if request.method == 'DELETE':
        msg_id = request.args.get('id')
        db.execute('DELETE FROM messages WHERE id = ?', (msg_id,))
        db.commit()
        return jsonify({"success": True})


# ⚙️ SETTINGS (ANNOUNCEMENTS & MAINTENANCE)
@app.route('/api/settings', methods=['GET', 'POST'])
def manage_settings():
    db = get_db()

    if request.method == 'GET':
        cursor = db.execute('SELECT * FROM settings')
        settings = {row['key']: row['value'] for row in cursor.fetchall()}
        return jsonify(settings)

    if request.method == 'POST':
        data = request.json
        for key, value in data.items():
            # Robust conversion: 
            # Boolean True -> "true", False -> "false"
            # Int 1 -> "1", 0 -> "0"
            if isinstance(value, bool):
                val_str = str(value).lower()
            else:
                val_str = str(value)
            
            # Using INSERT OR REPLACE to handle both new and existing settings
            db.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, val_str))
        db.commit()
        return jsonify({"success": True, "message": "Settings updated"})


# 🌟 TESTIMONIALS
@app.route('/api/testimonials', methods=['GET', 'POST', 'DELETE'])
def manage_testimonials():
    db = get_db()
    
    if request.method == 'GET':
        cursor = db.execute('SELECT * FROM testimonials ORDER BY id DESC')
        return jsonify([dict(row) for row in cursor.fetchall()])

    if request.method == 'POST':
        data = request.json
        db.execute('INSERT INTO testimonials (name, role, review_text, rating, image_url) VALUES (?,?,?,?,?)',
                   (data.get('name'), data.get('role'), data.get('review_text'), data.get('rating'), data.get('image_url')))
        db.commit()
        return jsonify({"success": True})

    if request.method == 'DELETE':
        db.execute('DELETE FROM testimonials WHERE id = ?', (request.args.get('id'),))
        db.commit()
        return jsonify({"success": True})


# 📝 BLOG POSTS
@app.route('/api/posts', methods=['GET', 'POST', 'DELETE'])
def manage_posts():
    db = get_db()

    if request.method == 'GET':
        cursor = db.execute('SELECT * FROM posts ORDER BY id DESC')
        return jsonify([dict(row) for row in cursor.fetchall()])

    if request.method == 'POST':
        data = request.json
        import datetime
        # If date is not provided, use current YYYY-MM-DD
        date_posted = data.get('date_posted') or datetime.datetime.now().strftime("%Y-%m-%d")
        status = data.get('status', 'Published')
        
        db.execute('INSERT INTO posts (title, content, image_url, date_posted, status) VALUES (?,?,?,?,?)',
                   (data.get('title'), data.get('content'), data.get('image_url'), date_posted, status))
        db.commit()
        return jsonify({"success": True})

    if request.method == 'DELETE':
        db.execute('DELETE FROM posts WHERE id = ?', (request.args.get('id'),))
        db.commit()
        return jsonify({"success": True})


# 🚀 PROJECTS
@app.route('/api/projects', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_projects():
    db = get_db()
    
    if request.method == 'GET':
        # Default Sort: Priority DESC (Hero items first), then ID DESC
        cursor = db.execute('SELECT * FROM projects ORDER BY priority DESC, id DESC')
        return jsonify([dict(row) for row in cursor.fetchall()])

    if request.method == 'POST':
        data = request.json
        status = data.get('status', 'Live')
        priority = data.get('priority', 0)
        
        db.execute('INSERT INTO projects (title, image_url, link_url, tags, description, status, priority) VALUES (?,?,?,?,?,?,?)',
                   (data.get('title'), data.get('image_url'), data.get('link_url'), data.get('tags'), data.get('description'), status, priority))
        db.commit()
        return jsonify({"success": True})

    # NEW: Update Project Status or Details
    if request.method == 'PUT':
        data = request.json
        proj_id = data.get('id')
        
        # Determine what to update
        if 'status' in data:
            db.execute('UPDATE projects SET status = ?, last_checked = CURRENT_TIMESTAMP WHERE id = ?', 
                      (data['status'], proj_id))
        
        if 'priority' in data:
             db.execute('UPDATE projects SET priority = ? WHERE id = ?', (data['priority'], proj_id))

        db.commit()
        return jsonify({"success": True})

    if request.method == 'DELETE':
        db.execute('DELETE FROM projects WHERE id=?', (request.args.get('id'),))
        db.commit()
        return jsonify({"success": True})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
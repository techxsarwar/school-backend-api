import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from models import db, User, Visit, Message, Testimonial, Project, Post, Setting, Ad, Coupon, Lead, ActivityLog, MarketingAd, log_activity


from auth import auth_bp
from functools import wraps
from werkzeug.security import generate_password_hash

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['ADMIN_USER'] = "admin"
app.config['ADMIN_PASS'] = "sarwar123"
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-key-change-this')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', '0') == '1'

# Database Configuration
# Fallback to sqlite if DATABASE_URL not set (e.g. local)
db_url = os.getenv('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///site_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}

db.init_app(app)

# Update CORS
CORS(app, resources={r"/api/*": {"origins": "https://sarwaraltaf.in"}}, supports_credentials=True)

# Register Blueprints
app.register_blueprint(auth_bp)

# --- EMAIL HELPERS ---
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl

# Mail Config
app.config['MAIL_SERVER'] = 'smtp.zoho.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_ASCII_ATTACHMENTS'] = False
app.config['MAIL_DEBUG'] = True

def send_async_email(app, subject, to_email, html_body):
    with app.app_context():
        smtp_server = app.config['MAIL_SERVER']
        smtp_port = app.config['MAIL_PORT']
        sender_email = app.config['MAIL_USERNAME']
        sender_password = app.config['MAIL_PASSWORD']
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        try:
            context = ssl.create_default_context()
            # Set timeout to 10 seconds
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=10) as server:
                if app.config['MAIL_DEBUG']:
                    server.set_debuglevel(1)
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, to_email, msg.as_string())
            print("Email sent successfully!")
            print(f" -> Invite email sent to {to_email}")
        except Exception as e:
            print(f" -> Failed to send email: {e}")

def send_invite_email(to_email, username, role, password):
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        print("Warning: Email credentials not set. Skipping email.")
        return

    subject = "Welcome to the Team | Your Creator Access"
    
    # Cinematic Dark Theme HTML
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 40px auto; background: #161b22; border: 1px solid #30363d; border-radius: 12px; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }}
            .header {{ background: linear-gradient(135deg, #1f6feb 0%, #58a6ff 100%); padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; color: white; font-size: 24px; text-transform: uppercase; letter-spacing: 2px; }}
            .content {{ padding: 40px; text-align: center; }}
            .welcome-text {{ font-size: 18px; line-height: 1.6; margin-bottom: 30px; }}
            .credential-box {{ background: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 20px; display: inline-block; text-align: left; margin-bottom: 30px; }}
            .credential-row {{ margin-bottom: 10px; font-family: 'Consolas', monospace; color: #8b949e; }}
            .credential-val {{ color: #58a6ff; font-weight: bold; }}
            .btn {{ display: inline-block; background: #238636; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px; transition: background 0.2s; }}
            .btn:hover {{ background: #2ea043; }}
            .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #8b949e; border-top: 1px solid #30363d; }}
            .security-note {{ color: #d2a8ff; font-size: 13px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Access Granted</h1>
            </div>
            <div class="content">
                <p class="welcome-text">Hello <strong>{username}</strong>,<br>You have been recruited as an <span style="color:#58a6ff">{role}</span>.</p>
                
                <div class="credential-box">
                    <div class="credential-row">URL: <span class="credential-val">https://school-backend-api-5hkh.onrender.com</span></div>
                    <div class="credential-row">Username: <span class="credential-val">{username}</span></div>
                    <div class="credential-row">Password: <span class="credential-val">{password}</span></div>
                </div>

                <a href="https://school-backend-api-5hkh.onrender.com" class="btn">Access Dashboard</a>

                <p class="security-note">⚠ For security, please update your password immediately after logging in.</p>
            </div>
            <div class="footer">
                &copy; 2026 Sarwar Portfolio System. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """

    # Send in background thread
    thread = threading.Thread(target=send_async_email, args=(app, subject, to_email, html_body))
    thread.start()

# --- DB INIT & SEEDING ---
with app.app_context():
    try:
        db.create_all()
        print("Successfully connected to Database!")
        
        # Check Admin
        admin = User.query.filter_by(username='Admin').first()
        if not admin:
            print(" -> Seeding Admin User...")
            p_hash = generate_password_hash("sarwar123")
            admin = User(username='Admin', password_hash=p_hash, role='Admin', email='admin@example.com')
            db.session.add(admin)
            print(" -> Admin Created (Pass: sarwar123)")
        else:
            # Force update password to ensure access
            print(" -> Updating Admin Password...")
            admin.password_hash = generate_password_hash("sarwar123")
            print(" -> Admin Password Reset to: sarwar123")
        
        db.session.commit()
            
        # Seed Settings if empty
        if not Setting.query.first():
             defaults = {
                "announcement_text": "Welcome to my official portfolio!",
                "announcement_active": "0",
                "announcement_type": "bar",
                "announcement_color": "#000000",
                "maintenance_mode": "0",
                "maintenance_end_time": "null",
                "profile_name": "Sarwar Altaf",
                "profile_headline": "Building digital empires...",
                "site_title": "Sarwar Portfolio",
                "meta_description": "Official Portfolio",
                "social_github": "#",
                "quick_note": ""
            }
             for k, v in defaults.items():
                 db.session.add(Setting(key=k, value=v))
             db.session.commit()

    except Exception as e:
        print(f"DB Init Error: {e}")


# --- HELPERS ---
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Allow OPTIONS pre-flight
            if request.method == 'OPTIONS':
                return f(*args, **kwargs)

            # Header check
            user_role = request.headers.get('X-Role', 'Guest')
            if 'Admin' in allowed_roles and user_role == 'Admin':
                return f(*args, **kwargs)
            if user_role in allowed_roles:
                return f(*args, **kwargs)
            return jsonify({"success": False, "message": "Access Denied"}), 403
        return decorated_function
    return decorator

# --- ROUTES ---

@app.route('/')
def home():
    return "Server is Running! 🚀 Sarwar's CMS API is Live (Postgres Ready)."

# 🏥 HEALTH CHECK
@app.route('/api/health', methods=['GET', 'HEAD'])
def health_check():
    # Simple explicit DB check
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({"status": "healthy", "db": "connected", "time": datetime.now().isoformat()})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check_alias():
    return jsonify({"status": "healthy"})

@app.route('/privacy')
def privacy_page():
    return app.send_static_file('privacy.html')

@app.route('/terms')
def terms_page():
    return app.send_static_file('terms.html')

# 🏥 SYSTEM HEALTH
@app.route('/api/system-health', methods=['GET'])
def system_health():
    try:
        db.session.execute(db.text('SELECT 1'))
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
    try:
        Visit.query.delete()
        db.session.commit()
        return jsonify({"success": True, "message": "Analytics cleared"})
    except:
        return jsonify({"success": False}), 500

# 📥 EXPORT CONTACTS
@app.route('/api/export-contacts', methods=['GET'])
def export_contacts():
    msgs = Message.query.all()
    output = "Name,Email,Timestamp\n"
    for m in msgs:
        output += f"{m.name},{m.email},{m.timestamp}\n"
    
    from flask import Response
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=contacts.csv"}
    )

# 📊 STATS
@app.route('/api/stats', methods=['GET'])
def get_stats():
    total_visits = Visit.query.count()
    mobile_visits = Visit.query.filter_by(device_type='mobile').count()
    desktop_visits = total_visits - mobile_visits
    
    unread_messages = Message.query.filter_by(read_status=0).count()
    total_messages = Message.query.count()
    active_ads = Ad.query.filter_by(is_active=1).count()
    live_projects = Project.query.filter_by(status='Live').count()
    
    recent_visitors = []
    # Helper to serialize visits
    visits = Visit.query.order_by(Visit.timestamp.desc()).limit(10).all()
    for v in visits:
        recent_visitors.append({"page": v.page, "time": v.timestamp, "device": v.device_type})

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

    v = Visit(page=page, device_type=device_type)
    db.session.add(v)
    db.session.commit()
    return jsonify({"success": True})

# 📢 ADS MANAGER
@app.route('/api/ads', methods=['GET', 'POST', 'DELETE'])
def manage_ads():
    if request.method == 'GET':
        ads = Ad.query.order_by(Ad.id.desc()).all()
        return jsonify([{"id": a.id, "title": a.title, "image_url": a.image_url, "link_url": a.link_url} for a in ads])

    # Auth Check
    user_role = request.headers.get('X-Role', 'Guest')
    if user_role not in ['Admin', 'Editor']:
        return jsonify({"success": False, "message": "Access Denied"}), 403

    if request.method == 'POST':
        data = request.json
        title = data.get('title') or data.get('headline') or 'Untitled Ad'
        image_url = data.get('image_url') or data.get('image') or ''
        link_url = data.get('link_url') or data.get('link') or '#'
        
        new_ad = Ad(title=title, image_url=image_url, link_url=link_url)
        db.session.add(new_ad)
        db.session.commit()
        return jsonify({"success": True, "message": "Ad Created"})

    if request.method == 'DELETE':
        Ad.query.filter_by(id=request.args.get('id')).delete()
        db.session.commit()
        return jsonify({"success": True, "message": "Ad Deleted"})

# 🎟 COUPONS
@app.route('/api/coupons', methods=['GET', 'POST'])
def manage_coupons():
    # Only Admin/Editor can view/create coupons
    user_role = request.headers.get('X-Role', 'Guest')
    if user_role not in ['Admin', 'Editor']:
        return jsonify({"success": False, "message": "Access Denied"}), 403

    if request.method == 'GET':
        coupons = Coupon.query.order_by(Coupon.id.desc()).all()
        return jsonify([{"id": c.id, "code": c.code, "discount": c.discount} for c in coupons])

    if request.method == 'POST':
        import random, string
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        discount = request.json.get('discount', '10% OFF')
        
        c = Coupon(code=code, discount=discount)
        db.session.add(c)
        db.session.commit()
        return jsonify({"success": True, "code": code, "discount": discount})

# 💬 MESSAGES
@app.route('/api/messages', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_messages():
    if request.method == 'GET':
        msgs = Message.query.order_by(Message.read_status.asc(), Message.timestamp.desc()).all()
        return jsonify([{"id": m.id, "name": m.name, "email": m.email, "message": m.message, "read_status": m.read_status, "timestamp": m.timestamp} for m in msgs])

    if request.method == 'POST':
        data = request.json
        m = Message(name=data.get('name'), email=data.get('email'), message=data.get('message'))
        db.session.add(m)
        db.session.commit()
        return jsonify({"success": True, "message": "Message sent!"})

    if request.method == 'PUT':
        data = request.json
        m = Message.query.get(data.get('id'))
        if m:
            m.read_status = data.get('read_status', 1)
            db.session.commit()
        return jsonify({"success": True})

    if request.method == 'DELETE':
        Message.query.filter_by(id=request.args.get('id')).delete()
        db.session.commit()
        return jsonify({"success": True})

# ⚙️ SETTINGS
@app.route('/api/settings', methods=['GET', 'POST'])
def manage_settings():
    if request.method == 'GET':
        settings = Setting.query.all()
        return jsonify({s.key: s.value for s in settings})

    if request.method == 'POST':
        # Auth Check
        user_role = request.headers.get('X-Role', 'Guest')
        if user_role not in ['Admin', 'Developer']:
            return jsonify({"success": False, "message": "Access Denied"}), 403

        data = request.json
        user_name = request.headers.get('X-User', 'Admin')
        
        if 'maintenance_mode' in data:
            new_mode = data['maintenance_mode']
            log_detail = "Enabled Maintenance" if str(new_mode) in ['1', 'true', 'True'] else "Disabled Maintenance"
            log_activity(1, user_name, 'SETTINGS', log_detail)

        for key, val in data.items():
            s = Setting.query.get(key)
            if s:
                s.value = str(val)
            else:
                db.session.add(Setting(key=key, value=str(val)))
        db.session.commit()
        return jsonify({"success": True, "message": "Settings updated"})

# 🌟 TESTIMONIALS & POSTS
@app.route('/api/testimonials', methods=['GET', 'POST', 'DELETE'])
def manage_testimonials():
    if request.method == 'GET':
        ts = Testimonial.query.order_by(Testimonial.id.desc()).all()
        return jsonify([{"id": t.id, "name": t.name, "role": t.role, "review_text": t.review_text, "rating": t.rating, "image_url": t.image_url} for t in ts])
    
    # Auth Check
    user_role = request.headers.get('X-Role', 'Guest')
    if user_role not in ['Admin', 'Editor']:
        return jsonify({"success": False, "message": "Access Denied"}), 403

    if request.method == 'POST':
        d = request.json
        t = Testimonial(name=d.get('name'), role=d.get('role'), review_text=d.get('review_text'), rating=d.get('rating'), image_url=d.get('image_url'))
        db.session.add(t)
        db.session.commit()
        return jsonify({"success": True})
    if request.method == 'DELETE':
        Testimonial.query.filter_by(id=request.args.get('id')).delete()
        db.session.commit()
        return jsonify({"success": True})

@app.route('/api/posts', methods=['GET', 'POST', 'DELETE'])
def manage_posts():
    if request.method == 'GET':
        posts = Post.query.order_by(Post.id.desc()).all()
        return jsonify([{"id": p.id, "title": p.title, "content": p.content, "image_url": p.image_url, "date_posted": p.date_posted} for p in posts])
    
    # Auth Check
    user_role = request.headers.get('X-Role', 'Guest')
    if user_role not in ['Admin', 'Editor']:
        return jsonify({"success": False, "message": "Access Denied"}), 403

    if request.method == 'POST':
        d = request.json
        date_posted = d.get('date_posted') or datetime.now().strftime("%Y-%m-%d")
        p = Post(title=d.get('title'), content=d.get('content'), image_url=d.get('image_url'), date_posted=date_posted, status=d.get('status', 'Published'))
        db.session.add(p)
        db.session.commit()
        
        user_name = request.headers.get('X-User', 'Editor')
        log_activity(1, user_name, 'BLOG', f"Posted: {d['title']}")
        
        return jsonify({"success": True})
    if request.method == 'DELETE':
        user_name = request.headers.get('X-User', 'Admin')
        log_activity(1, user_name, 'BLOG', f"Deleted Post ID: {request.args.get('id')}")

        Post.query.filter_by(id=request.args.get('id')).delete()
        db.session.commit()
        return jsonify({"success": True})

# 🚀 PROJECTS
@app.route('/api/projects', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_projects():
    if request.method == 'GET':
        projects = Project.query.order_by(Project.priority.desc(), Project.id.desc()).all()
        return jsonify([{"id": p.id, "title": p.title, "image_url": p.image_url, "link_url": p.link_url, "tags": p.tags, "description": p.description, "status": p.status, "priority": p.priority} for p in projects])
    
    # Auth Check
    user_role = request.headers.get('X-Role', 'Guest')
    if user_role not in ['Admin', 'Developer']:
        return jsonify({"success": False, "message": "Access Denied"}), 403

    if request.method == 'POST':
        d = request.json
        p = Project(title=d.get('title'), image_url=d.get('image_url'), link_url=d.get('link_url'), tags=d.get('tags'), description=d.get('description'), status=d.get('status', 'Live'), priority=d.get('priority', 0))
        db.session.add(p)
        db.session.commit()
        return jsonify({"success": True})
    
    if request.method == 'PUT':
        d = request.json
        p = Project.query.get(d['id'])
        if p:
            if 'status' in d: p.status = d['status']
            if 'priority' in d: p.priority = d['priority']
            p.last_checked = datetime.utcnow()
            db.session.commit()
        return jsonify({"success": True})

    if request.method == 'DELETE':
        Project.query.filter_by(id=request.args.get('id')).delete()
        db.session.commit()
        return jsonify({"success": True})

# 📈 LEADS
@app.route('/api/leads', methods=['POST'])
def log_lead():
    d = request.json
    db.session.add(Lead(plan_name=d.get('plan_name')))
    db.session.commit()
    return jsonify({"success": True, "message": "Lead logged"})

# 👥 TEAM MANAGEMENT
@app.route('/api/team', methods=['GET'])
def get_team():
    user_role = request.headers.get('X-Role', 'Guest')
    if user_role != 'Admin': return jsonify([]), 403
    
    users = User.query.all()
    return jsonify([{"id": u.id, "username": u.username, "email": u.email, "role": u.role, "joined_date": u.joined_date} for u in users])

@app.route('/api/team/invite', methods=['POST', 'OPTIONS'])
@cross_origin()
@role_required(['Admin'])
def invite_user():
    if request.method == 'OPTIONS':
        return '', 204

    # Logging
    print(f"Headers: {request.headers}")
    print(f"Data: {request.get_data(as_text=True)}")

    if not request.is_json:
        return jsonify({"success": False, "message": "Content-Type must be application/json"}), 400

    data = request.get_json()
    print(f"Received JSON: {data}")

    if not data:
        return jsonify({"success": False, "message": "No input data provided"}), 400

    # Validation
    required = ['username', 'email', 'role']
    for field in required:
        if field not in data or not data[field]:
            return jsonify({"success": False, "message": f"Missing field: {field}"}), 400

    try:
        # Check existing
        if User.query.filter((User.username == data['username']) | (User.email == data['email'])).first():
             return jsonify({"success": False, "message": "User or Email already exists"}), 400

        temp_pass = "welcome123"
        p_hash = generate_password_hash(temp_pass)
        u = User(username=data['username'], email=data['email'], role=data['role'], password_hash=p_hash)
        db.session.add(u)
        db.session.commit()
        
        username = request.headers.get('X-User', 'Admin')
        log_activity(1, username, 'INVITE', f"Invited user {data['username']}")
        
        # Trigger Email
        send_invite_email(data['email'], data['username'], data['role'], temp_pass)

        return jsonify({"success": True, "message": "User invited & Email sent"})
    except Exception as e:
        print(f"Invite Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/activity', methods=['GET'])
def get_activity():
    user_role = request.headers.get('X-Role', 'Guest')
    if user_role != 'Admin': return jsonify([]), 403

    logs = ActivityLog.query.order_by(ActivityLog.id.desc()).limit(50).all()
    return jsonify([{"id": l.id, "username": l.username, "action": l.action, "details": l.details, "timestamp": l.timestamp} for l in logs])

# 📢 MARKETING POPUP (Daily Ad)
@app.route('/api/marketing/active', methods=['GET'])
def get_active_popup():
    try:
        # Query for the latest active ad
        ad = MarketingAd.query.filter_by(is_active=1).first()
        if not ad:
            return jsonify({"message": "No active ad", "active": False}), 200
        
        return jsonify({
            "id": ad.id,
            "title": ad.title,
            "image_url": ad.image_url,
            "link_url": ad.link_url,
            "active": True
        }), 200
    except Exception as e:
        print(f"Marketing API Error: {e}")
        return jsonify({"active": False, "error": str(e)}), 500

@app.route('/api/marketing/update', methods=['POST'])
def update_popup():
    user_role = request.headers.get('X-Role', 'Guest')
    if user_role not in ['Admin', 'Editor']:
        return jsonify({"success": False, "message": "Access Denied"}), 403

    d = request.json
    
    # We only keep ONE row for simplicity in this "Daily Ad" feature
    ad = MarketingAd.query.first()
    if not ad:
        ad = MarketingAd()
        db.session.add(ad)
    
    ad.title = d.get('title', 'Daily Ad')
    ad.image_url = d.get('image_url', '')
    ad.link_url = d.get('link_url', '#')
    ad.is_active = int(d.get('is_active', 0))
    
    db.session.commit()
    return jsonify({"success": True, "message": "Popup Updated"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
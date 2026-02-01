from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120))
    role = db.Column(db.String(20), default='Admin')
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)

class Visit(db.Model):
    __tablename__ = 'visits'
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(100))
    device_type = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read_status = db.Column(db.Integer, default=0)

class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    role = db.Column(db.String(100))
    review_text = db.Column(db.Text)
    rating = db.Column(db.Integer)
    image_url = db.Column(db.String(255))

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    image_url = db.Column(db.String(255))
    link_url = db.Column(db.String(255))
    tags = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Live')
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    priority = db.Column(db.Integer, default=0)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    date_posted = db.Column(db.String(20), default=datetime.utcnow().strftime("%Y-%m-%d"))
    status = db.Column(db.String(20), default='Published')

class Setting(db.Model):
    __tablename__ = 'settings'
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Text)

class Ad(db.Model):
    __tablename__ = 'ads'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    image_url = db.Column(db.String(255))
    link_url = db.Column(db.String(255))
    is_active = db.Column(db.Integer, default=1)

class Coupon(db.Model):
    __tablename__ = 'coupons'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20))
    discount = db.Column(db.String(50))
    is_active = db.Column(db.Integer, default=1)

class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ActivityLog(db.Model):
    __tablename__ = 'activity_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    username = db.Column(db.String(80))
    action = db.Column(db.String(50))
    details = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class MarketingAd(db.Model):
    __tablename__ = 'marketing_ads'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    image_url = db.Column(db.String(255))
    link_url = db.Column(db.String(255))
    is_active = db.Column(db.Integer, default=0)

class PricingPlan(db.Model):
    __tablename__ = 'pricing_plans'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    billing_cycle = db.Column(db.String(50)) 
    features = db.Column(db.Text) # JSON string
    is_featured = db.Column(db.Boolean, default=False)

class Tool(db.Model):
    __tablename__ = 'tools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    icon_url = db.Column(db.String(255))
    tool_url = db.Column(db.String(255))
    category = db.Column(db.String(100))
    is_locked = db.Column(db.Boolean, default=False)

# Helper for logging
def log_activity(user_id, username, action, details=""):
    try:
        log = ActivityLog(user_id=user_id, username=username, action=action, details=details)
        db.session.add(log)
        db.session.commit()
    except:
        db.session.rollback()

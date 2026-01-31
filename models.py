import sqlite3
from flask import g, current_app

DB_FILE = "site_data.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_FILE)
        db.row_factory = sqlite3.Row
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        try:
            db = get_db()
            cursor = db.cursor()
            print(" -> Checking Database Schema...")

            # --- TABLES DEFINITION ---
            # 1. Visits
            cursor.execute('''CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page TEXT,
                device_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')

            # 6. Messages
            cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                read_status INTEGER DEFAULT 0
            )''')

            # 7. Testimonials
            cursor.execute('''CREATE TABLE IF NOT EXISTS testimonials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                role TEXT,
                review_text TEXT,
                rating INTEGER,
                image_url TEXT
            )''')

            # 8. Projects
            cursor.execute('''CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                image_url TEXT,
                link_url TEXT,
                tags TEXT,
                description TEXT,
                status TEXT DEFAULT 'Live',
                last_checked DATETIME DEFAULT CURRENT_TIMESTAMP,
                priority INTEGER DEFAULT 0
            )''')

            # 9. Posts
            cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                image_url TEXT,
                date_posted TEXT DEFAULT CURRENT_DATE,
                status TEXT DEFAULT 'Published'
            )''')
            
            # 10. Settings, Coupons, Ads
            cursor.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT, image_url TEXT, link_url TEXT, is_active INTEGER DEFAULT 1
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS coupons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT, discount TEXT, is_active INTEGER DEFAULT 1
            )''')

            # --- ROBUST MIGRATION LOGIC ---
            def check_and_add_column(table, col, col_def):
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [info[1] for info in cursor.fetchall()]
                if col not in columns:
                    print(f" -> Migrating {table}: Adding {col}...")
                    try:
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}")
                    except Exception as e:
                        print(f"    ! Error adding {col} to {table}: {e}")
                else:
                    pass # Column exists

            # Run Checks
            check_and_add_column('messages', 'read_status', 'INTEGER DEFAULT 0')
            check_and_add_column('projects', 'status', "TEXT DEFAULT 'Live'")
            check_and_add_column('projects', 'last_checked', "DATETIME DEFAULT CURRENT_TIMESTAMP")
            check_and_add_column('projects', 'priority', "INTEGER DEFAULT 0")
            check_and_add_column('posts', 'status', "TEXT DEFAULT 'Published'")
            
            # 11. Leads (New)
            cursor.execute('''CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_name TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # --- SEEDING ---
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
            for key, val in defaults.items():
                cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, val))

            db.commit()
            print(" -> Database Initialized & Verified.")

        except Exception as e:
            print(f"CRITICAL DB ERROR: {e}")
            raise e

# --- HELPER CLASSES ---
class DB:
    @staticmethod
    def query(sql, args=(), one=False):
        db = get_db()
        cursor = db.execute(sql, args)
        rv = cursor.fetchall()
        db.commit() # Auto commit for convenience in this simple app
        return (rv[0] if rv else None) if one else rv

    @staticmethod
    def get_all_messages():
        return DB.query('SELECT * FROM messages ORDER BY read_status ASC, timestamp DESC')

    @staticmethod
    def save_setting(key, value):
        db = get_db()
        db.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, str(value)))
        db.commit()

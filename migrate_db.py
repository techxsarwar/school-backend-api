import sqlite3
import sys

try:
    conn = sqlite3.connect('site_data.db')
    c = conn.cursor()
    
    # Check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not c.fetchone():
        print("Creating users table...")
        c.execute('''CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password_hash TEXT,
                email TEXT,
                role TEXT DEFAULT 'Editor',
                joined_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
    else:
        # Check column
        c.execute("PRAGMA table_info(users)")
        cols = [r[1] for r in c.fetchall()]
        if 'role' not in cols:
            print("Adding role column...")
            c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'Editor'")
        else:
            print("Role column exists.")
            
    # Check activity_log
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='activity_log'")
    if not c.fetchone():
         print("Creating activity_log table...")
         c.execute('''CREATE TABLE activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT, 
                action TEXT,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')

    # Seed Admin
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        print("Seeding Admin...")
        # Hash for sarwar123
        h = "scrypt:32768:8:1$lT8oD3Qe3x0$5b340026e7920150935574345757476579294285863266946658097034479905"
        c.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', ('admin', h, 'Admin'))
    else:
        c.execute("UPDATE users SET role='Admin' WHERE username='admin'")
        print("Admin role verified.")

    conn.commit()
    conn.close()
    print("Migration Success.")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

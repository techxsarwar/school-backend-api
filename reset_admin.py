import sqlite3
from werkzeug.security import generate_password_hash

DB_FILE = "site_data.db"

def reset_admin():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        print(f"Connected to {DB_FILE}...")
        
        # 1. Delete existing Admin
        cursor.execute("DELETE FROM users WHERE username = 'Admin' OR username = 'admin'")
        print(" - Deleted existing 'Admin' user(s).")
        
        # 2. Create new Admin
        password = "welcome123"
        p_hash = generate_password_hash(password)
        
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, email) 
            VALUES (?, ?, ?, ?)
        ''', ('Admin', p_hash, 'Admin', 'admin@example.com'))
        
        conn.commit()
        print(f" - Created new 'Admin' with password '{password}'.")
        
        # Verify
        cursor.execute("SELECT username, role FROM users WHERE username='Admin'")
        user = cursor.fetchone()
        print(f" - Verification: Found user {user}")
        
        conn.close()
        print("Done.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reset_admin()

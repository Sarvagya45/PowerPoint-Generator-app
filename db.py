import sqlite3
import hashlib
import os

DB_NAME = "app_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table for Local AND Google Users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT,
            salt TEXT,
            full_name TEXT,
            user_id TEXT,
            auth_provider TEXT DEFAULT 'local'
        )
    """)
    
    # Table for Presentations History
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            topic TEXT,
            num_slides INTEGER,
            audience TEXT,
            filename TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    """)
    
    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hashed, salt

def register_user(username, password, full_name="", user_id="", auth_provider="local"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT username FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists."
        
    password_hash, salt = "", ""
    if password:
        password_hash, salt = hash_password(password)
        
    cursor.execute("""
        INSERT INTO users (username, password_hash, salt, full_name, user_id, auth_provider)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, password_hash, salt, full_name, user_id, auth_provider))
    
    conn.commit()
    conn.close()
    return True, "Success"

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, salt, full_name, user_id, auth_provider FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return False, "User not found.", None, None
        
    db_hash, salt, full_name, user_id, auth_provider = row
        
    # Verify local pass
    hashed, _ = hash_password(password, salt)
    if hashed == db_hash:
        return True, "Success", full_name, user_id
    else:
        return False, "Incorrect password.", None, None

def save_history(username, topic, num_slides, audience, filename):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO history (username, topic, num_slides, audience, filename)
        VALUES (?, ?, ?, ?, ?)
    """, (username, topic, num_slides, audience, filename))
    conn.commit()
    conn.close()

def get_user_history(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT topic, num_slides, audience, filename, timestamp 
        FROM history 
        WHERE username=? 
        ORDER BY timestamp DESC
    """, (username,))
    history = cursor.fetchall()
    conn.close()
    
    return [
        {
            "topic": row[0],
            "num_slides": row[1],
            "audience": row[2],
            "filename": row[3],
            "timestamp": row[4]
        }
        for row in history
    ]

# Initialize db file automatically upon import if it doesn't exist
init_db()

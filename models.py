import sqlite3

DB_NAME = "database.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

#USER TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        bio TEXT,
        username TEXT,
        password TEXT,
        gender TEXT,
        looking_for TEXT,
        UTR REAL,
        location TEXT,
        max_distance REAL
        
)
""")

#LIKED PEOPLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        liked_user_id INTEGER
    )
    """)

#MESSAGE TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER,
        receiver_id INTEGER,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        seen INTEGER DEFAULT 0
    )
    """)

#PASS TABLE
    cursor.execute("""
CREATE TABLE IF NOT EXISTS passes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    passed_user_id INTEGER
)
""")

    conn.commit()
    conn.close()


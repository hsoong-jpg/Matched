import sqlite3

DB_NAME = "database.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        bio TEXT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        gender TEXT,
        looking_for TEXT,
        UTR REAL,
        location TEXT,
        max_distance REAL
    )
    """)

    # LIKES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        liked_user_id INTEGER NOT NULL,
        UNIQUE(user_id, liked_user_id),
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(liked_user_id) REFERENCES users(id)
    )
    """)

    # PASSES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS passes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        passed_user_id INTEGER NOT NULL,
        UNIQUE(user_id, passed_user_id),
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(passed_user_id) REFERENCES users(id)
    )
    """)

    # MESSAGES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        seen INTEGER DEFAULT 0,
        FOREIGN KEY(sender_id) REFERENCES users(id),
        FOREIGN KEY(receiver_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()
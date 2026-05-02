
from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"


# ----------------------------
# DATABASE
# ----------------------------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # USERS (login only)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # PROFILES (public data)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            gender TEXT,
            utr TEXT,
            bio TEXT
        )
    """)

    # LIKES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            liked_user_id INTEGER
        )
    """)

    # MATCHES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER,
            user2_id INTEGER,
            UNIQUE(user1_id, user2_id)
        )
    """)

    # SEEN USERS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seen_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            seen_user_id INTEGER
        )
    """)

    # MESSAGES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ----------------------------
# SIGNUP
# ----------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        gender = request.form["gender"]
        utr = request.form["utr"]
        bio = request.form["bio"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # 1. create user
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )

        user_id = cursor.lastrowid

        # 2. create profile linked to user
        cursor.execute("""
            INSERT INTO profiles (user_id, name, gender, utr, bio)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, gender, utr, bio))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("signup.html")


# ----------------------------
# LOGIN
# ----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM users
            WHERE username=? AND password=?
        """, (username, password))

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["index"] = 0
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")


# ----------------------------
# LOGOUT
# ----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ----------------------------
# GET UNSEEN PROFILES
# ----------------------------
def get_unseen_profiles(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM profiles
        WHERE user_id != ?
        AND user_id NOT IN (
            SELECT liked_user_id FROM likes WHERE user_id = ?
        )
        AND user_id NOT IN (
            SELECT seen_user_id FROM seen_users WHERE user_id = ?
        )
    """, (user_id, user_id, user_id))

    profiles = cursor.fetchall()
    conn.close()
    return profiles


# ----------------------------
# HOME (SWIPE FEED)
# ----------------------------
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    profiles = get_unseen_profiles(user_id)
    idx = session.get("index", 0)

    if len(profiles) == 0:
        return render_template("index.html, no_profiles=True")
    

    if idx >= len(profiles):
        session["index"] = 0
        idx = 0

    profile = profiles[idx]

    return render_template("index.html", profile={
        "user_id": profile[1],
        "name": profile[2],
        "gender": profile[3],
        "utr": profile[4],
        "bio": profile[5]
    },
    no_profiles=False)
</div> <!-- end card -->




# ----------------------------
# LIKE
# ----------------------------
@app.route("/like", methods=["POST"])
def like():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    idx = session.get("index", 0)

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    profiles = get_unseen_profiles(user_id)

    if idx >= len(profiles):
        return redirect("/")

    profile = profiles[idx]
    other_user_id = profile[1]

    # save like
    cursor.execute("""
        INSERT INTO likes (user_id, liked_user_id)
        VALUES (?, ?)
    """, (user_id, other_user_id))

    # mark seen
    cursor.execute("""
        INSERT INTO seen_users (user_id, seen_user_id)
        VALUES (?, ?)
    """, (user_id, other_user_id))

    # check match
    cursor.execute("""
        SELECT * FROM likes
        WHERE user_id=? AND liked_user_id=?
    """, (other_user_id, user_id))

    if cursor.fetchone():
        user1 = min(user_id, other_user_id)
        user2 = max(user_id, other_user_id)

        cursor.execute("""
            INSERT OR IGNORE INTO matches (user1_id, user2_id)
            VALUES (?, ?)
        """, (user1, user2))

    session["index"] = idx + 1

    conn.commit()
    conn.close()

    return redirect("/")


# ----------------------------
# SKIP
# ----------------------------
@app.route("/pass", methods=["POST"])
def skip():
    user_id = session["user_id"]
    idx = session.get("index", 0)

    profiles = get_unseen_profiles(user_id)

    if idx < len(profiles):
        other_user_id = profiles[idx][1]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO seen_users (user_id, seen_user_id)
            VALUES (?, ?)
        """, (user_id, other_user_id))

        conn.commit()
        conn.close()

    session["index"] = idx + 1
    return redirect("/")


# ----------------------------
# MATCHES
# ----------------------------
@app.route("/matches")
def matches():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.name, p.bio
        FROM matches m
        JOIN profiles p
        ON p.user_id = m.user1_id OR p.user_id = m.user2_id
        WHERE m.user1_id=? OR m.user2_id=?
        GROUP BY p.user_id
    """, (user_id, user_id))

    matches = cursor.fetchall()
    conn.close()

    return render_template("matches.html", profiles=matches)


# ----------------------------
# CHAT
# ----------------------------
@app.route("/chat/<int:user2_id>")
def chat(user2_id):
    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sender_id, receiver_id, message, timestamp
        FROM messages
        WHERE (sender_id=? AND receiver_id=?)
           OR (sender_id=? AND receiver_id=?)
        ORDER BY timestamp ASC
    """, (user_id, user2_id, user2_id, user_id))

    messages = cursor.fetchall()
    conn.close()

    return render_template("chat.html", messages=messages, user2_id=user2_id)


# ----------------------------
# SEND MESSAGE
# ----------------------------
@app.route("/send_message/<int:user2_id>", methods=["POST"])
def send_message(user2_id):
    user_id = session["user_id"]
    message = request.form["message"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (sender_id, receiver_id, message)
        VALUES (?, ?, ?)
    """, (user_id, user2_id, message))

    conn.commit()
    conn.close()

    return redirect(f"/chat/{user2_id}")


# ----------------------------
# RUN APP
# ----------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
    
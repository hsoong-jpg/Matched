import sqlite3
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "secretkey"

# ----------------------------
# DATABASE INIT
# ----------------------------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            bio TEXT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            liked_user_id INTEGER
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ----------------------------
# SIGNUP
# ----------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        bio = request.form.get("bio")
        username = request.form.get("username")
        password = request.form.get("password")
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (name, bio, username, password)
            VALUES (?, ?, ?, ?)
        """, (name, bio, username, password))

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
            SELECT * FROM users WHERE username=? AND password=?
        """, (username, password))

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")


# ----------------------------
# HOME (SWIPE PROFILE)
# ----------------------------
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id != ?", (session["user_id"],))
    users = cursor.fetchall()
    conn.close()

    if len(users) == 0:
        return render_template("index.html", no_profiles=True)

    session["index"] = 0
    return render_template("index.html", user=users[0])


# ----------------------------
# LIKE BUTTON
# ----------------------------
@app.route("/like", methods=["POST"])
def like():
    if "user_id" not in session:
        return redirect("/login")

    liked_id = request.form["liked_user_id"]
    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO likes (user_id, liked_user_id)
        VALUES (?, ?)
    """, (user_id, liked_id))

    conn.commit()
    conn.close()

    return redirect("/")


# ----------------------------
# PEOPLE WHO LIKED YOU
# ----------------------------
@app.route("/likes")
def likes():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT users.id, users.name, users.bio
        FROM likes
        JOIN users ON users.id = likes.user_id
        WHERE likes.liked_user_id = ?
    """, (user_id,))

    likes = cursor.fetchall()
    conn.close()

    return render_template("likes.html", likes=likes)


# ----------------------------
# PEOPLE YOU LIKED
# ----------------------------
@app.route("/liked")
def liked():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT users.id, users.name, users.bio
        FROM likes
        JOIN users ON users.id = likes.liked_user_id
        WHERE likes.user_id = ?
    """, (user_id,))

    liked_people = cursor.fetchall()
    conn.close()

    return render_template("liked.html", liked=liked_people)
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

    # mutual likes = MATCHES
    cursor.execute("""
        SELECT users.id, users.name, users.bio
        FROM likes l1
        JOIN likes l2 ON l1.user_id = l2.liked_user_id
                      AND l1.liked_user_id = l2.user_id
        JOIN users ON users.id = l2.user_id
        WHERE l1.user_id = ?
    """, (user_id,))

    matches = cursor.fetchall()
    conn.close()

    return render_template("matches.html", matches=matches)

# ----------------------------
# LOGOUT
# ----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
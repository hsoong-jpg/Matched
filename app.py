#Flask = main web, render_template = loads HTML files
#Request = handles incoming form data, Redirect = sends user to another route
#Session stores login state (like User ID)
from flask import Flask, render_template, request, redirect, session

#Date and time
from datetime import datetime
#Allows database to be created in a file 
import sqlite3

#Hash password import
from werkzeug.security import generate_password_hash, check_password_hash

#Allows for instant messaging 
from flask_socketio import SocketIO, emit, join_room

#Creates app
app = Flask(__name__)

#Used to secure session data 
app.secret_key = "secretkey"

#allows for instant messaging 
socketio = SocketIO(app)

# ----------------------------
# DATABASE 
# ----------------------------
def init_db():

    #Connects to a file called "database.db"
    conn = sqlite3.connect("database.db")

    #Cursor lets you run SQL commands
    cursor = conn.cursor()

    #USERS TABLE
    #id = unique user id, name and bio = profile info 
    #username = unique, password = stored as plain text 
    cursor.execute("""
    CREATE TABLE  IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        bio TEXT,
        username TEXT,
        password TEXT,
        gender TEXT,
        looking_for TEXT,
        UTR TEXT
)
""")

    #LIKES TABLE
    #Stores who liked who 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            liked_user_id INTEGER
        )
    """)

    #MESSAGE TABLE
    #stores all messages
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            seen INTEGER
        )
        """)

    #Saves changes 
    conn.commit()

    #Closes DB connection
    conn.close()

#Runs this setup when app starts 
init_db()

# ----------------------------
# SIGNUP
#URL: /signup
#GET = request page and data in it
#POST = send data to server to update 
# ----------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():

#Password stores secure hash 
    if request.method == "POST":

        name = request.form.get("name")
        bio = request.form.get("bio")
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        gender = request.form.get("gender")

        looking_for = ",".join(request.form.getlist("looking_for"))

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (name, bio, username, password, gender, looking_for)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, bio, username, password, gender, looking_for))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("signup.html")


# ----------------------------
# LOGIN
# ----------------------------

#GET = viewing page, POST = submitted login form
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        #Gets data from HTML form
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        #Searches database for the user 
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))

        #Gets first matching user
        user = cursor.fetchone()

        conn.close()

        #user = makes sure user exists
        #user[4] gets stored hashed password
        #Check_Password_hash = compares typed password and hashed password
        if user and check_password_hash(user[4], password):

            #this browser is logged in at user[0] (user id)
            session["user_id"] = user[0]
            return redirect("/")
        else:
            return "Invalid username or password"

    return render_template("login.html")

# ----------------------------
# HOME (SWIPE PROFILE)
# ----------------------------
@app.route("/")
def index():

    #Blocks access if not logged in
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    #Gets all users except current user
    cursor.execute("SELECT * FROM users WHERE id != ?", (session["user_id"],))
    
    #List of users
    users = cursor.fetchall()
    conn.close()

    #If no profiles exist 
    if len(users) == 0:
        return render_template("index.html", no_profiles=True)

    #Shows first user 
    session["index"] = 0
    return render_template("index.html", user=users[0])


# ----------------------------
# LIKE BUTTON
# ----------------------------
@app.route("/like", methods=["POST"])
def like():
    if "user_id" not in session:
        return redirect("/login")

    #Who you liked
    liked_id = request.form["liked_user_id"]

    #Who you are
    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    #Saves the like
    cursor.execute("""
        INSERT INTO likes (user_id, liked_user_id)
        VALUES (?, ?)
    """, (user_id, liked_id))

    conn.commit()
    conn.close()

    #Reloads for next profile
    return redirect("/")
# ----------------------------
# PASS
# ----------------------------
@app.route("/pass", methods=["POST"])
def pass_user():
    if "user_id" not in session:
        return redirect("/login")

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

    #Finds users who liked you
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

    #Finds users you liked
    #WHERE = who liked me (filter to people who liked me)
    #JOIN = take each user_id and match it with the full user profile in the users table 
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
# IS MATCH
# ----------------------------
def is_match(a, b):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM likes
        WHERE (user_id=? AND liked_user_id=?)
        OR (user_id=? AND liked_user_id=?)
    """, (a, b, b, a))

    return cursor.fetchone() is not None
# ----------------------------
# SEND MESSAGE 
# ----------------------------

@socketio.on("send_message")
def handle_message(data):
    sender_id = session.get("user_id")

    if not sender_id:
        return

    if not is_match(sender_id, data["receiver_id"]):
        return

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (sender_id, receiver_id, message)
        VALUES (?, ?, ?)
    """, (sender_id, data["receiver_id"], data["message"]))

    conn.commit()
    conn.close()

    room = f"chat_{min(sender_id, data['receiver_id'])}_{max(sender_id, data['receiver_id'])}"

    emit("receive_message", {
        "sender_id": sender_id,
        "message": data["message"],
        "timestamp": datetime.now().strftime("%b %d, %H:%M")
    }, room=room)
# ----------------------------
# JOIN ROOM EVENT
# ----------------------------

@socketio.on("join")
def on_join(data):
    room = data["room"]
    join_room(room)


# ----------------------------
# CHAT PAGE
# ----------------------------

@app.route("/chat/<int:user_id>")
def chat(user_id):
    if "user_id" not in session:
        return redirect("/login")
    
    current_user = session["user_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM messages
        WHERE (sender_id =? AND receiver_id=?)
        OR (sender_id =? AND receiver_id=?)
        ORDER BY timestamp
                   """, (current_user, user_id, user_id, current_user))
    
    messages = cursor.fetchall()
    conn.close()

    return render_template(
    "chat.html",
    messages=messages,
    current_user=session["user_id"],
    user_id=user_id
)


# ----------------------------
# START TYPING
# ----------------------------
@socketio.on("typing")
def handle_typing(data):
    room = data["room"]
    emit("show_typing", {"user_id": session.get("user_id")}, room=room, include_self=False)

# ----------------------------
# STOP TYPING
# ----------------------------

@socketio.on("stop_typing")
def handle_stop_typing(data):
    room = data["room"]
    emit("hide_typing", room=room)


# ----------------------------
# INBOX
# ----------------------------
@app.route("/inbox")
def inbox(): 
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.id, u.name,
        -- last message
        (
            SELECT message FROM messages
                   WHERE (sender_id = u.id AND receiver_id = ?)
                   OR (sender_id = ? AND receiver_id = u.id)
                   ORDER BY id DESC LIMIT 1
                   ),

                   -- last time 
                   (
                   SELECT timestamp FROM messages
                   WHERE (sender_id = u.id AND receiver_id =?)
                   OR (sender_id = ? AND receiver_id = u.id)
                   ORDER BY id DESC LIMIT 1
                   ),
                    -- unread count
        (
            SELECT COUNT(*) FROM messages
            WHERE receiver_id = ?
            AND sender_id = u.id
            AND seen = 0
        )

        FROM users u
        WHERE u.id IN (
            SELECT l1.user_id
            FROM likes l1
            JOIN likes l2
            ON l1.user_id = l2.liked_user_id
            AND l1.liked_user_id = l2.user_id
            WHERE l1.user_id = ?
        )
    """, (user_id, user_id, user_id, user_id, user_id, user_id))

    matches = cursor.fetchall()
    conn.close()

    return render_template("inbox.html", matches=matches)

# ----------------------------
# LOGOUT
# ----------------------------
@app.route("/logout")
def logout():

    #Logs user out
    session.clear()
    return redirect("/login")

#Runs server locally 
if __name__ == "__main__":
    #Auto reloads and shows errors 
    socketio.run(app, debug=True)
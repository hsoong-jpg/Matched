#Allows database to be created in a file 
import sqlite3

#Flask = main web, render_template = loads HTML files
#Request = handles incoming form data, Redirect = sends user to another route
#Session stores login state (like User ID)
from flask import Flask, render_template, request, redirect, session

#Creates app
app = Flask(__name__)

#Used to secure session data 
app.secret_key = "secretkey"

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
        looking_for TEXT
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

    if request.method == "POST":

        name = request.form.get("name")
        bio = request.form.get("bio")
        username = request.form.get("username")
        password = request.form.get("password")
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
@app.route("/login", methods=["GET", "POST"])
def login():

    #Gets submitted login 
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        #Checks if user exists
        cursor.execute("""
            SELECT * FROM users WHERE username=? AND password=?
        """, (username, password))

        #Gets first matching user
        user = cursor.fetchone()
        conn.close()

        #Saves logged in user ID in session
        if user:
            session["user_id"] = user[0]

            #Go to homepage
            return redirect("/")
        
        #If login does not match any users 
        else:
            return "Invalid login"

    #Stay on login page 
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
    app.run(debug=True)
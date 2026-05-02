# Flask = web framework
# render_template = sends HTML files to browser
# request = reads form data (what user types)
# redirect = sends user to another page
# session = remembers logged-in user
from flask import Flask, render_template, request, redirect, session
import sqlite3

# ----------------------------
# CREATE APP
# ----------------------------
app = Flask(__name__)

# secret key is required for sessions (login system)
app.secret_key = "your_secret_key"


# ----------------------------
# DATABASE SETUP
# ----------------------------
def init_db():
    # connect to database file (creates it if it doesn't exist)
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # USERS table (login system)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)

    # PROFILES table (what users see in feed)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            bio TEXT
        )
    """)

    # LIKES table (who liked who)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            liked_profile_id INTEGER
        )
    """)

    # MATCHES table (mutual likes)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user1_id INTEGER,
        user2_id INTEGER,
        UNIQUE(user1_id, user2_id)
)
""")
    # seen users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS seen_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        seen_profile_id INTEGER
    )
""")

    # save changes
    conn.commit()
    conn.close()


# ----------------------------
# SAMPLE DATA (ONLY ONCE)
# ----------------------------
def seed_profiles():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # check if profiles already exist
    cursor.execute("SELECT COUNT(*) FROM profiles")
    count = cursor.fetchone()[0]

    # only add sample data if database is empty
    if count == 0:
        cursor.execute("INSERT INTO profiles (user_id, name, bio) VALUES (1, 'Alice', 'Loves hiking')")
        cursor.execute("INSERT INTO profiles (user_id, name, bio) VALUES (2, 'Bob', 'Coffee addict')")
        cursor.execute("INSERT INTO profiles (user_id, name, bio) VALUES (3, 'Charlie', 'Tech nerd')")

    conn.commit()
    conn.close()


# ----------------------------
# HELPER FUNCTION
# ----------------------------
# gets all profiles except current user
def get_profiles(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM profiles
        WHERE user_id != ?
    """, (user_id,))

    profiles = cursor.fetchall()
    conn.close()
    return profiles


# ----------------------------
# SIGNUP PAGE
# ----------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():

    # if user submits form
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # create user account
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )

        # get new user ID
        user_id = cursor.lastrowid

        # automatically create a profile for that user
        cursor.execute(
            "INSERT INTO profiles (user_id, name, bio) VALUES (?, ?, ?)",
            (user_id, username, "New user!")
        )

        conn.commit()
        conn.close()

        # send user to login page
        return redirect("/login")

    # show signup page
    return render_template("signup.html")


# ----------------------------
# LOGIN PAGE
# ----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # check if user exists
        cursor.execute(
            "SELECT id FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            # store user in session (keeps them logged in)
            session["user_id"] = user[0]

            # reset feed index
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
    # clears session (logs user out)
    session.clear()
    return redirect("/login")


# ----------------------------
# HOMEPAGE (FEED)
# ----------------------------
@app.route("/")
def index():

    # must be logged in
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    # create index if it doesn't exist
    if "index" not in session:
        session["index"] = 0

    # get all other profiles
    profiles = get_unseen_profiles(user_id)

    #which profile the user is current viewing
    idx = session["index"]

    # if no more profiles left
    if len(profiles) == 0:
        return "No profiles available"

# reset loop instead of stopping
    if idx >= len(profiles):
        session["index"] = 0
        idx = 0

    profile = profiles[idx]

    # send current profile to HTML
    return render_template(
        "index.html",
        profile={
            "id": profile[0],
            "name": profile[2],
            "bio": profile[3]
        }
    )



# ----------------------------
# LIKE BUTTON
# ----------------------------
@app.route("/like", methods=["POST"])
def like():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    idx = session.get("index", 0)

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    profiles = get_profiles(user_id)

    # make sure index is valid
    if idx < len(profiles):

        profile = profiles[idx]
        profile_id = profile[0]
        other_user_id = profile[1]

        # ----------------------------
        # SAVE LIKE
        # ----------------------------
        cursor.execute("""
            SELECT * FROM likes
            WHERE user_id=? AND liked_profile_id=?
        """, (user_id, profile_id))

        already_liked = cursor.fetchone()

        # only insert if not already liked
        if not already_liked:
            cursor.execute("""
                INSERT INTO likes (user_id, liked_profile_id)
                VALUES (?, ?)
            """, (user_id, profile_id))

        cursor.execute("""
    INSERT INTO seen_users (user_id, seen_profile_id)
    VALUES (?, ?)
""", (user_id, profile_id))

        # ----------------------------
        # CHECK MATCH
        # ----------------------------
        # check if other user already liked me
    cursor.execute("""
    SELECT * FROM likes
    WHERE user_id=? AND liked_profile_id=?
""", (other_user_id, user_id))

    match = cursor.fetchone()

    if match:
    # normalize order so duplicates never happen
        user1 = min(user_id, other_user_id)
        user2 = max(user_id, other_user_id)

    # insert match safely
    cursor.execute("""
        INSERT OR IGNORE INTO matches (user1_id, user2_id)
        VALUES (?, ?)
    """, (user1, user2))

        # move to next profile
    session["index"] = session.get("index", 0) + 1

    conn.commit()
    conn.close()

    return redirect("/")


# ----------------------------
# PASS BUTTON
# ----------------------------
@app.route("/pass", methods=["POST"])
def skip():

    # just move to next profile
    session["index"] = session.get("index", 0) + 1
    return redirect("/")


# ----------------------------
# MATCHES PAGE
# ----------------------------
@app.route("/matches")
def show_matches():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # get all matches for this user
    cursor.execute("""
        SELECT profiles.name, profiles.bio
        FROM matches
        JOIN profiles ON matches.user2_id = profiles.id
        WHERE matches.user1_id = ?
    """, (user_id,))

    matches = cursor.fetchall()
    conn.close()

    # convert to clean format for HTML
    result = [{"name": m[0], "bio": m[1]} for m in matches]

    return render_template("matches.html", profiles=result)


# ----------------------------
# LIKES PAGE
# ----------------------------
@app.route("/likes")
def show_likes():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # get all profiles user liked
    cursor.execute("""
        SELECT profiles.name, profiles.bio
        FROM likes
        JOIN profiles ON likes.liked_profile_id = profiles.id
        WHERE likes.user_id = ?
    """, (user_id,))

    
    likes = cursor.fetchall()
    conn.close()

    result = [{"name": l[0], "bio": l[1]} for l in likes]

    return render_template("likes.html", profiles=result)

# ----------------------------
# FITLER UNSEEN PROFILES
# ----------------------------
def get_unseen_profiles(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM profiles
        WHERE user_id != ?
        AND id NOT IN (
            SELECT liked_profile_id FROM likes WHERE user_id = ?
        )
    """, (user_id, user_id))

    profiles = cursor.fetchall()
    conn.close()

    return profiles

# ----------------------------
# GET UNSEEN PROFILES
# ----------------------------

def get_unseen_profiles(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM profiles
        WHERE user_id != ?
        AND id NOT IN (
            SELECT liked_profile_id FROM likes WHERE user_id = ?
        )
        AND id NOT IN (
            SELECT seen_profile_id FROM seen_users WHERE user_id = ?
        )
    """, (user_id, user_id, user_id))

    profiles = cursor.fetchall()
    conn.close()
    return profiles

# ----------------------------
# SKIP
# ----------------------------  
  
@app.route("/pass", methods=["POST"])
def skip_profile():

    user_id = session["user_id"]
    idx = session.get("index", 0)

    profiles = get_unseen_profiles(user_id)

    if idx < len(profiles):
        profile = profiles[idx]
        profile_id = profile[0]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # mark as seen
        cursor.execute("""
            INSERT INTO seen_users (user_id, seen_profile_id)
            VALUES (?, ?)
        """, (user_id, profile_id))

        conn.commit()
        conn.close()

    session["index"] = idx + 1
    return redirect("/")

# ----------------------------
# RUN SERVER
# ----------------------------
if __name__ == "__main__":
    init_db()        # create tables
    seed_profiles()  # add sample data
    app.run(debug=True)
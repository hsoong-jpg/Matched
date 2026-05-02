# Flask creates web app, render_template sends HTML to browser, request reads user actions
#redirect sends users to another page, sqlite3 ability to use database
#session remebers who is logged in
from flask import Flask, render_template, request, redirect, session
import sqlite3

#creates app
app = Flask(__name__)
#enables sessions 
app.secret_key = "your_secret_key"

#tracks what profile user is viewing
current_index = 0

# ----------------------------
# DATABASE SETUP
# ----------------------------

#Function that creates database tables 
def init_db():
    #opens or creates a file called database.db
    conn = sqlite3.connect("database.db")
    #cursor is a tool to run SQL 
    cursor = conn.cursor()
    #Creates table called users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)
    #creates a table called profiles
    #id = unique number for each row, int, 
    # primary key (main identifier) and autoincrement is automaticlaly increases
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            bio TEXT
        )
    """)
    #stores likes
    #user_id = the user who liked id
    #liked_profile_id is the profile that got liked id
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            liked_profile_id INTEGER
        )
    """)
#stores a matches table 

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user1_id INTEGER,
        user2_id INTEGER
    )
""")
    
    #saves changed to database
    conn.commit()
    #closes database connection
    conn.close()


# ----------------------------
# ADD SAMPLE DATA 
# ----------------------------

def seed_profiles():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    #counts how many profiles exist and returns as tuple
    cursor.execute("SELECT COUNT(*) FROM profiles")
    #take the first value in the tuple so count is normal number
    count = cursor.fetchone()[0]
    #only insert profiles if table is empty
    if count == 0:
        #adds rows to database
        cursor.execute("INSERT INTO profiles (name, bio) VALUES ('Alice', 'Loves hiking')")
        cursor.execute("INSERT INTO profiles (name, bio) VALUES ('Bob', 'Coffee addict')")
        cursor.execute("INSERT INTO profiles (name, bio) VALUES ('Charlie', 'Tech nerd')")

    conn.commit()
    conn.close()

# ----------------------------
# SIGNUP
# ----------------------------
# Get = show page 
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # connect to database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # insert user
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )

        # get new user's id
        user_id = cursor.lastrowid

        # create profile for that user
        cursor.execute(
            "INSERT INTO profiles (user_id, name, bio) VALUES (?, ?, ?)",
            (user_id, username, "New user!")
        )

        # save and close
        conn.commit()
        conn.close()

        # redirect to login
        return redirect("/login")

    # show signup page
    return render_template("signup.html")

# ----------------------------
# LOGIN
# ----------------------------
@app.route("/login", methods = ["GET", "POST"])
def login():
    #if user clicks login button
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        #Asks if there is a user name with this username and password
        cursor.execute(
            "SELECT id FROM users WHERE username=? AND password=?",
            (username,password)
        )
        #gets result from execute
        user = cursor.fetchone()
        conn.close()
        #if user exists
        if user:
            #store user ID in memory
            session["user_id"] = user[0]
            #send user to homepage
            return redirect("/")
        #show error message
        else: 
            return "Invalid login"
        #if just opening page 
    return render_template("login.html")

# ----------------------------
# LOGOUT
# ----------------------------
@app.route("/logout")
def logout():
    #clears who is logged in
    session.clear()
    return redirect("/login")

# ----------------------------
# HOMEPAGE
# ----------------------------
#when user visits / this runs
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login") 
    
    #get users own index 
    if "index" not in session:
        session["index"] = 0
    #connect to database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    #Get all profiles
    user_id = session["user_id"]
    cursor.execute("""
                   SELECT * FROM profiles
                   WHERE user_id = ?
                   """, (user_id,))
    profiles = cursor.fetchall()
    conn.close()
    #if you run out of profiles 
    if current_index >=len(profiles):
        return "No more profiles"

    #pick current profile 
    profile = profiles[current_index]

    #Send to HTML in correct format 
    return render_template(
        "index.html",
        profile={
            "id" : profile[0],
            "name" : profile[1],
            "bio": profile[2]

        }
    )


# ----------------------------
# LIKE
# ----------------------------
#methods allows this to run when user clicks like
@app.route("/like", methods=["POST"])
def like():
    if "user_id" not in session:
        return redirect("/login") 
    
    #get users own index 
    if "index" not in session:
        session["index"] = 0
    
    user_id = session["user_id"]
    current_index = session["index"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM profiles")
    profiles = cursor.fetchall()
    # prevent crash if index is too big
    if current_index < len(profiles):
        #gets current profile
        profile = profiles[current_index]
        #saves the like into database
        cursor.execute(
            "INSERT INTO likes (user_id, liked_profile_id) VALUES (?, ?)", #inserts new row into likes table
            (user_id, profile[0])  # user liked profile[id]
        )
        #check if the other user already liked this user
        other_user_id = profile[1]  # because profile = (id, user_id, name, bio)

    cursor.execute("""
    SELECT * FROM likes
    WHERE user_id = ? AND liked_profile_id = ?
""", (other_user_id, user_id))
    match = cursor.fetchone()

    if match:
            cursor.execute(
                "INSERT INTO matches (user1_id, user2_id) VALUES (?,?)",
                (user_id, profile[0])
            )

    conn.commit()
    conn.close()
    #move to next profile
    current_index += 1
    return redirect("/")
# ----------------------------
# MATCHES
# ----------------------------
@app.route("/matches")
def show_matches():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT profiles.name, profiles.bio
        FROM matches
        JOIN profiles ON matches.user2_id = profiles.id
        WHERE matches.user1_id = ?
    """, (user_id,))

    matches = cursor.fetchall()
    conn.close()

    result = []
    for m in matches:
        result.append({"name": m[0], "bio": m[1]})

    return render_template("matches.html", profiles=result)
# ----------------------------
# PASS
# ----------------------------

@app.route("/pass", methods=["POST"])
def skip():
    if "index" not in session:
        session["index"] = 0
    session["index"] +=1
    return redirect("/")


# ----------------------------
# VIEW LIKES 
# ----------------------------

@app.route("/likes")
def show_likes():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    user_id = session["user_id"]

    #Gets the name and bio of all profiles user liked
    # select = these columns 
    # from = from likes table
    # join = connects liked_profile_id and id to combine data 
    # where = what user likes  
    cursor.execute("""
        SELECT profiles.name, profiles.bio
        FROM likes
        JOIN profiles On likes.liked_profile_id = profiles.id
        WHERE likes.user_id = ?
    """, (user_id,))

    liked_profiles = cursor.fetchall()

    conn.close()

    
    result = []
    for p in liked_profiles:
        result.append({"name": p[0], "bio": p[1]})
    #returns JSON
    return render_template("likes.html", profiles=result)


# ----------------------------
# RUN APP
# ----------------------------

if __name__ == "__main__":
    #Create tables and add data
    init_db()
    seed_profiles()
    #start server 
    app.run(debug=True)
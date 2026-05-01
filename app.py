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
@app.route("/signup", methods = ["GET", "POST"])
def signup():
    #if user clicked create account
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        #connects to database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        #inserts new user 
        cursor.execute(
    "INSERT INTO users (username, password) VALUES (?, ?)",
    (username, password)
)
        conn.commit()
        conn.close()
        #sends user back to login page after signing up
        return redirect("/login")
    #show sign up page if not POST
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
# HOMEPAGE
# ----------------------------
#when user visits / this runs
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login") 
    #if they are logged in
    return render_template("index.html")


# ----------------------------
# LIKE
# ----------------------------
#methods allows this to run when user clicks like
@app.route("/like", methods=["POST"])
def like():
    global current_index
    user_id = session["user_id"]

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

    conn.commit()
    conn.close()
    #move to next profile
    current_index += 1
    return redirect("/")


# ----------------------------
# PASS
# ----------------------------

@app.route("/pass", methods=["POST"])
def skip():
    global current_index
    current_index += 1
    return redirect("/")


# ----------------------------
# VIEW LIKES 
# ----------------------------

@app.route("/likes")
def show_likes():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    #Gets the name and bio of all profiles user liked
    # select = these columns 
    # from = from likes table
    # join = connects liked_profile_id and id to combine data 
    # where = what user likes  
    cursor.execute("""
        SELECT profiles.name, profiles.bio
        FROM likes
        JOIN profiles ON likes.liked_profile_id = profiles.id
        WHERE likes.user_id = 1
    """)

    liked_profiles = cursor.fetchall()

    conn.close()

    
    result = []
    for p in liked_profiles:
        result.append({"name": p[0], "bio": p[1]})
    #returns JSON
    return {"liked_profiles": result}


# ----------------------------
# RUN APP
# ----------------------------

if __name__ == "__main__":
    #Create tables and add data
    init_db()
    seed_profiles()
    #start server 
    app.run(debug=True)
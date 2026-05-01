# Flask creates web app, render_template sends HTML to browser, request reads user actions
#redirect sends users to another page, sqlite3 ability to use database
from flask import Flask, render_template, request, redirect
import sqlite3

#creates app
app = Flask(__name__)

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
    #counts how many profiles exist
    cursor.execute("SELECT COUNT(*) FROM profiles")
    #gets result and extracts number
    count = cursor.fetchone()[0]
    #only insert profiles if table is empty
    if count == 0:
        #adds row to database
        cursor.execute("INSERT INTO profiles (name, bio) VALUES ('Alice', 'Loves hiking')")
        cursor.execute("INSERT INTO profiles (name, bio) VALUES ('Bob', 'Coffee addict')")
        cursor.execute("INSERT INTO profiles (name, bio) VALUES ('Charlie', 'Tech nerd')")

    conn.commit()
    conn.close()


# ----------------------------
# HOMEPAGE
# ----------------------------
#when user visits / this runs
@app.route("/")
def index():
    #use shared variable
    global current_index
    #connect to database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    #Get all profiles and returns list
    cursor.execute("SELECT * FROM profiles")
    profiles = cursor.fetchall()

    conn.close()
    #stops if user reaches end
    if current_index >= len(profiles):
        return "No more profiles"
    #gets current profile
    profile = profiles[current_index]
    #converts tuple to a dictonary so HTML can use it
    return render_template(
        "index.html",
        profile={
            "id": profile[0],
            "name": profile[1],
            "bio": profile[2]
        }
    )


# ----------------------------
# LIKE
# ----------------------------
#methods allows this to run when user clicks like
@app.route("/like", methods=["POST"])
def like():
    global current_index

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
            (1, profile[0])  # user 1 liked profile[id]
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
# VIEW LIKES (NOW FROM DB)
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
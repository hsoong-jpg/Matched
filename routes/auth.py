from flask import Blueprint, render_template, request, redirect
from werkzeug.security import generate_password_hash
from models import get_connection
from werkzeug.security import check_password_hash
from flask import session

#Creates a Blueprint for auth
auth_bp = Blueprint("auth", __name__)

#SIGNUP ROUTE (GET: display signup page, POST: process submitted form)
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        #retrieves the values from the HTML form
        username = request.form.get("username")
        password = request.form.get("password")

        #Checks if either field is empty 
        if not username or not password:
            return "Missing required fields", 400

        try:
            #Gets value from the form and converts it to a number
            #max(0, value) prevents negative numbers
            max_distance = max(0, float(request.form.get("max_distance", 0)))
            #Converts UTR into a float
            utr = float(request.form.get("UTR"))
            #catches conversion errors
        except (ValueError, TypeError):
            return "Invalid numeric input", 400

        conn = get_connection()

        try:
            cursor = conn.cursor()

            #Checks to see if username is taken 
            cursor.execute(
                "SELECT id FROM users WHERE username=?",
                (username,)
            )

            if cursor.fetchone():
                return "Username already exists", 400

            #inserts new user
            cursor.execute("""
                INSERT INTO users (
                    name, bio, username, password,
                    gender, looking_for, UTR,
                    location, max_distance
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request.form.get("name"),
                request.form.get("bio"),
                username,
                #hashes password before saving 
                generate_password_hash(password),
                request.form.get("gender"),
                #.join turns the list (looking for) into a string
                ",".join(request.form.getlist("looking_for")),
                utr,
                request.form.get("location"),
                max_distance
            ))

            conn.commit()

        finally:
            conn.close()

        return redirect("/login")

    return render_template("signup.html")

#LOGIN ROUTE
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_connection()
        cursor = conn.cursor()

        #Looks for matching username
        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()
        conn.close()

        #only logs in if user and password is correct
        #compare password hash to user[4] which is password
        if user and check_password_hash(user[4], password):
            session["user_id"] = user[0]
            return redirect("/")

        return "Invalid login", 400

    return render_template("login.html")

#LOGOUT ROUTE
@auth_bp.route("/logout")
def logout():
    #Deletes session data 
    session.clear()
    return redirect("/login")
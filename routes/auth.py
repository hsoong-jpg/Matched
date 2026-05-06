from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import get_connection



auth = Blueprint("auth", __name__)

# ----------------------------
# SIGNUP
# ----------------------------
@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        try:
            max_distance = float(request.form.get("max_distance"))
        except:
            return "Invalid distance", 400

        if max_distance < 0:
            max_distance = 0

        conn = get_connection()
        cursor = conn.cursor()

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
            request.form.get("username"),
            generate_password_hash(request.form.get("password")),
            request.form.get("gender"),
            ",".join(request.form.getlist("looking_for")),
            float(request.form.get("UTR")),
            request.form.get("location"),
            max_distance
        ))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("signup.html")


# ----------------------------
# LOGIN
# ----------------------------
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (request.form["username"],))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[4], request.form["password"]):
            session["user_id"] = user[0]
            return redirect("/")
        return "Invalid login"

    return render_template("login.html")


# ----------------------------
# LOGOUT
# ----------------------------
@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import get_connection

auth = Blueprint("auth", __name__)

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (name, bio, username, password, gender, looking_for)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            request.form["name"],
            request.form["bio"],
            request.form["username"],
            generate_password_hash(request.form["password"]),
            request.form["gender"],
            ",".join(request.form.getlist("looking_for"))
        ))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("signup.html")


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

@auth.route("/logout")
def logout():
    session.clear()   # removes user_id + everything else
    return redirect("/login")
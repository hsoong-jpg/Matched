from flask import Blueprint, render_template, request, redirect
from werkzeug.security import generate_password_hash
from models import get_connection
from werkzeug.security import check_password_hash
from flask import session

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return "Missing required fields", 400

        try:
            max_distance = max(0, float(request.form.get("max_distance", 0)))
            utr = float(request.form.get("UTR"))
        except (ValueError, TypeError):
            return "Invalid numeric input", 400

        conn = get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id FROM users WHERE username=?",
                (username,)
            )

            if cursor.fetchone():
                return "Username already exists", 400

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
                generate_password_hash(password),
                request.form.get("gender"),
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

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[4], password):
            session["user_id"] = user[0]
            return redirect("/")

        return "Invalid login", 400

    return render_template("login.html")



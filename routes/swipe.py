from flask import Blueprint, render_template, session, redirect
from models import get_connection

swipe_bp = Blueprint("swipe", __name__)

@swipe_bp.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, bio, gender FROM users WHERE id != ?", (session["user_id"],))
    users = cursor.fetchall()
    conn.close()

    return render_template("index.html", users=users)
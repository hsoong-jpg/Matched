from flask import Blueprint, render_template, session, redirect, request
from models import get_connection

swipe_bp = Blueprint("swipe", __name__)

@swipe_bp.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id != ?", (session["user_id"],))
    users = cursor.fetchall()
    conn.close()

    return render_template("index.html", user=users[0] if users else None)


@swipe_bp.route("/like", methods=["POST"])
def like():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO likes (user_id, liked_user_id)
        VALUES (?, ?)
    """, (session["user_id"], request.form["liked_user_id"]))

    conn.commit()
    conn.close()

    return redirect("/")
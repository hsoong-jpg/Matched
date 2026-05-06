from flask import Blueprint, render_template, session, redirect
from models import get_connection

matches_bp = Blueprint("matches", __name__)

@matches_bp.route("/matches")
def matches():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT users.id, users.name, users.bio
        FROM likes l1
        JOIN likes l2
        ON l1.user_id = l2.liked_user_id
        AND l1.liked_user_id = l2.user_id
        JOIN users ON users.id = l2.user_id
        WHERE l1.user_id = ?
    """, (session["user_id"],))

    data = cursor.fetchall()
    conn.close()

    return render_template("matches.html", matches=data)
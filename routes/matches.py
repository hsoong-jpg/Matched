from flask import Blueprint, render_template, session, redirect
from models import get_connection

matches_bp = Blueprint("matches", __name__)


@matches_bp.route("/matches")
def matches():

    # Require login
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    # Get mutual matches
    cursor.execute("""
        SELECT DISTINCT
            u.id,
            u.name,
            u.bio,
            u.UTR,
            u.location

        FROM users u

        JOIN likes l1
            ON l1.liked_user_id = u.id

        JOIN likes l2
            ON l2.user_id = u.id

        WHERE l1.user_id = ?
        AND l2.liked_user_id = ?
    """, (user_id, user_id))

    matches = cursor.fetchall()

    conn.close()

    return render_template("matches.html", matches=matches)
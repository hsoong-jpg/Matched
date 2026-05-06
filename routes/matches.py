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
SELECT *
FROM users
WHERE id != ?
AND location = ?
""", (session["user_id"], user_location))

    data = cursor.fetchall()
    conn.close()

    return render_template("matches.html", matches=data)
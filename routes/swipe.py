from flask import Blueprint, render_template, session, redirect, request
from models import get_connection

swipe_bp = Blueprint("swipe", __name__)


# ----------------------------
# HOME (SHOW NEXT PROFILE)
# ----------------------------
@swipe_bp.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id != ?", (session["user_id"],))
    users = cursor.fetchall()
    conn.close()

    index = session.get("index", 0)

    # reset if out of range
    if index >= len(users):
        session["index"] = 0
        return render_template("index.html", no_profiles=True)

    return render_template("index.html", user=users[index])


# ----------------------------
# LIKE
# ----------------------------
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

    # move to next profile
    session["index"] = session.get("index", 0) + 1

    return redirect("/")


# ----------------------------
# PASS
# ----------------------------
@swipe_bp.route("/pass", methods=["POST"])
def pass_user():
    session["index"] = session.get("index", 0) + 1
    return redirect("/")
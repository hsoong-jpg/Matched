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

    user_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    # Get next available profile (excluding liked/passed/self)
    cursor.execute("""
        SELECT id, name, bio, username, gender, looking_for, UTR
        FROM users
        WHERE id != ?

        AND id NOT IN (
            SELECT liked_user_id
            FROM likes
            WHERE user_id = ?
        )

        AND id NOT IN (
            SELECT passed_user_id
            FROM passes
            WHERE user_id = ?
        )

        ORDER BY RANDOM()
        LIMIT 1
    """, (user_id, user_id, user_id))

    user = cursor.fetchone()
    conn.close()

    return render_template("index.html", user=user)


# ----------------------------
# LIKE
# ----------------------------
@swipe_bp.route("/like", methods=["POST"])
def like():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    liked_user_id = request.form.get("liked_user_id")

    if not liked_user_id or int(liked_user_id) == user_id:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO likes (user_id, liked_user_id)
            VALUES (?, ?)
        """, (user_id, liked_user_id))

        conn.commit()
    finally:
        conn.close()

    return redirect("/")


# ----------------------------
# PASS
# ----------------------------
@swipe_bp.route("/pass", methods=["POST"])
def pass_user():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    passed_user_id = request.form.get("passed_user_id")

    if not passed_user_id or int(passed_user_id) == user_id:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO passes (user_id, passed_user_id)
            VALUES (?, ?)
        """, (user_id, passed_user_id))

        conn.commit()
    finally:
        conn.close()

    return redirect("/")
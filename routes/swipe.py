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

    #WHERE = dont show my own profile 
    #AND id NOT in = dont show users liked or passed
    #UNION = join lists of users ive liked or passed
    #ORDER BY RANDOM = shuffle profiles 
    #LIMIT = 1 profile on the page 
    cursor.execute("""
        SELECT id, name, bio, username, gender, looking_for, UTR
        FROM users
        WHERE id != ?

        AND id NOT IN (
            SELECT liked_user_id FROM likes WHERE user_id = ?
            UNION
            SELECT passed_user_id FROM passes WHERE user_id = ?
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

    #Get id of liked user 
    try:
        liked_user_id = int(request.form.get("liked_user_id"))
    except (TypeError, ValueError):
        return redirect("/")

    if liked_user_id == user_id:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT OR IGNORE INTO likes (user_id, liked_user_id)
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

    try:
        passed_user_id = int(request.form.get("passed_user_id"))
    except (TypeError, ValueError):
        return redirect("/")

    if passed_user_id == user_id:
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
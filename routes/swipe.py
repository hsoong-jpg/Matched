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

    user_id = session["user_id"]

    # get users already liked
    cursor.execute("SELECT liked_user_id FROM likes WHERE user_id = ?", (user_id,))
    liked = [row[0] for row in cursor.fetchall()]

    # get users already passed
    cursor.execute("SELECT passed_user_id FROM passes WHERE user_id = ?", (user_id,))
    passed = [row[0] for row in cursor.fetchall()]

    excluded = liked + passed + [user_id]

    # get next available profile
    cursor.execute("""
        SELECT id, name, bio, username, gender, looking_for, UTR
        FROM users
        WHERE id NOT IN ({seq})
        LIMIT 1
    """.format(seq=",".join(["?"]*len(excluded))), excluded)

    user = cursor.fetchone()

    conn.close()

    return render_template("index.html", user=user)

   


# ----------------------------
# LIKE
# ----------------------------
@swipe_bp.route("/like", methods=["POST"])
def like():
    conn = get_connection()
    cursor = conn.cursor()

    user_id = session["user_id"]
    liked_user_id = request.form["liked_user_id"]

    cursor.execute("""
        INSERT INTO likes (user_id, liked_user_id)
        VALUES (?, ?)
    """, (user_id, liked_user_id))

    conn.commit()
    conn.close()

    return redirect("/")


# ----------------------------
# PASS
# ----------------------------
@swipe_bp.route("/pass", methods=["POST"])
def pass_user():
    conn = get_connection()
    cursor = conn.cursor()

    user_id = session["user_id"]
    passed_user_id = request.form["passed_user_id"]

    cursor.execute("""
        INSERT INTO passes (user_id, passed_user_id)
        VALUES (?, ?)
    """, (user_id, passed_user_id))

    conn.commit()
    conn.close()

    return redirect("/")
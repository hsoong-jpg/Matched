from flask import Blueprint, render_template, session, request, redirect
from models import get_connection

profile_bp = Blueprint("profile", __name__)

# ----------------------------
# VIEW PROFILE
# ----------------------------
@profile_bp.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, bio, username, gender, looking_for, UTR
        FROM users
        WHERE id = ?
    """, (session["user_id"],))

    user = cursor.fetchone()
    conn.close()

    return render_template("profile.html", user=user)


# ----------------------------
# EDIT PROFILE
# ----------------------------
@profile_bp.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        cursor.execute("""
            UPDATE users
            SET name = ?, bio = ?, gender = ?, looking_for = ?, UTR = ?
            WHERE id = ?
        """, (
            request.form.get("name"),
            request.form.get("bio"),
            request.form.get("gender"),
            request.form.get("looking_for"),
            request.form.get("UTR"),
            session["user_id"]
        ))

        conn.commit()
        conn.close()

        return redirect("/profile")

    cursor.execute("""
        SELECT name, bio, gender, looking_for, UTR
        FROM users
        WHERE id = ?
    """, (session["user_id"],))

    user = cursor.fetchone()
    conn.close()

    return render_template("edit_profile.html", user=user)
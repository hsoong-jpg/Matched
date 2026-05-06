from flask import Blueprint, render_template, request, redirect, session
from models import get_connection

profile_bp = Blueprint("profile", __name__)


# VIEW PROFILE
@profile_bp.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, bio, username, gender, looking_for, UTR, location
        FROM users
        WHERE id = ?
    """, (session["user_id"],))

    user = cursor.fetchone()
    conn.close()

    return render_template("profile.html", user=user)


# EDIT PROFILE
@profile_bp.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        try:
            utr = float(request.form.get("UTR") or 0)
        except:
            utr = 0

        cursor.execute("""
            UPDATE users
            SET bio = ?, looking_for = ?, UTR = ?, location = ?
            WHERE id = ?
        """, (
            request.form.get("bio"),
            ",".join(request.form.getlist("looking_for")),
            utr,
            request.form.get("location"),
            session["user_id"]
        ))

        conn.commit()
        conn.close()
        return redirect("/profile")

    cursor.execute("""
        SELECT bio, looking_for, UTR, location
        FROM users
        WHERE id = ?
    """, (session["user_id"],))

    user = cursor.fetchone()
    conn.close()

    return render_template("edit_profile.html", user=user)
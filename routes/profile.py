from flask import Blueprint, render_template, request, redirect, session
from models import get_connection

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                bio,
                username,
                gender,
                looking_for,
                UTR,
                location
            FROM users
            WHERE id = ?
        """, (session["user_id"],))

        user = cursor.fetchone()

        if not user:
            session.clear()
            return redirect("/login")

    finally:
        conn.close()

    return render_template("profile.html", user=user)


@profile_bp.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()

    try:
        cursor = conn.cursor()

        if request.method == "POST":

            #Gets UTR and converts to float and if invalid set it to 0
            try:
                utr = float(request.form.get("UTR") or 0)
            except (ValueError, TypeError):
                utr = 0

            bio = request.form.get("bio", "")[:500]
            location = request.form.get("location", "")[:100]

            #Updates users table 
            cursor.execute("""
                UPDATE users
                SET
                    bio = ?,
                    looking_for = ?,
                    UTR = ?,
                    location = ?
                WHERE id = ?
            """, (
                bio,
                ",".join(request.form.getlist("looking_for")),
                utr,
                location,
                session["user_id"]
            ))

            conn.commit()

            return redirect("/profile")

        cursor.execute("""
            SELECT bio, looking_for, UTR, location
            FROM users
            WHERE id = ?
        """, (session["user_id"],))

        user = cursor.fetchone()

    finally:
        conn.close()

    return render_template("edit_profile.html", user=user)
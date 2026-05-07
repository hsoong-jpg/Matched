from flask import Blueprint, render_template, session, redirect
from models import get_connection

inbox_bp = Blueprint("inbox", __name__)


# ----------------------------
# INBOX ROUTE
# ----------------------------
@inbox_bp.route("/inbox")
def inbox():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT u.id, u.name,

    SELECT
    u.id,
    u.name,

    COALESCE((
        SELECT message
        FROM messages
        WHERE (
            sender_id = u.id AND receiver_id = ?
        ) OR (
            sender_id = ? AND receiver_id = u.id
        )
        ORDER BY timestamp DESC
        LIMIT 1
    ), '') AS last_message

FROM users u

WHERE u.id != ?

AND EXISTS (
    SELECT 1
    FROM likes l1
    JOIN likes l2
      ON l1.user_id = l2.liked_user_id
     AND l1.liked_user_id = l2.user_id
    WHERE l1.user_id = ?
      AND l1.liked_user_id = u.id
)

ORDER BY (
    SELECT MAX(timestamp)
    FROM messages
    WHERE (
        sender_id = u.id AND receiver_id = ?
    ) OR (
        sender_id = ? AND receiver_id = u.id
    )
) DESC
""", (user_id, user_id, user_id, user_id))

    matches = cursor.fetchall()
    conn.close()

    return render_template("inbox.html", matches=matches)
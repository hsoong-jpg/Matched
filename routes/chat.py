from flask import Blueprint, render_template, session, redirect
from flask_socketio import emit, join_room
from datetime import datetime, timezone
from models import get_connection
from extensions import socketio

chat_bp = Blueprint("chat", __name__)


# ---------------------------
# CHAT PAGE
# ---------------------------
@chat_bp.route("/chat/<int:user_id>")
def chat(user_id):
    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "chat.html",
        messages=[],
        receiver_id=user_id,
        user_id=session["user_id"]
    )


# ---------------------------
# CONNECT (FIXED LOCATION)
# ---------------------------
@socketio.on("connect")
def on_connect():
    user_id = session.get("user_id")
    if not user_id:
        return


# ---------------------------
# JOIN ROOM
# ---------------------------
@socketio.on("join")
def join(data):
    user_id = session.get("user_id")
    if not user_id:
        return

    receiver_id = data.get("receiver_id")
    if not receiver_id:
        return

    room = f"chat_{min(user_id, receiver_id)}_{max(user_id, receiver_id)}"
    join_room(room)


# ---------------------------
# SEND MESSAGE
# ---------------------------
@socketio.on("send_message")
def send_message(data):
    sender_id = session.get("user_id")
    if not sender_id:
        return

    receiver_id = data.get("receiver_id")
    message = (data.get("message") or "").strip()

    if not receiver_id or not message:
        return

    if len(message) > 2000:
        return

    room = f"chat_{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (sender_id, receiver_id, message, timestamp)
        VALUES (?, ?, ?, ?)
    """, (
        sender_id,
        receiver_id,
        message,
        datetime.now(timezone.utc).isoformat()
    ))

    conn.commit()
    conn.close()

    emit("receive_message", {
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "message": message,
        "timestamp": datetime.now(timezone.utc).strftime("%H:%M")
    }, room=room)
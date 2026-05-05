from flask import Blueprint, render_template, session, request
from flask_socketio import emit, join_room
from datetime import datetime
from models import get_connection
from extensions import socketio

chat_bp = Blueprint("chat", __name__)


# ---------- CHAT PAGE ----------
@chat_bp.route("/chat/<int:user_id>")
def chat(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM messages
        WHERE (sender_id=? AND receiver_id=?)
        OR (sender_id=? AND receiver_id=?)
        ORDER BY timestamp
    """, (session["user_id"], user_id, user_id, session["user_id"]))

    messages = cursor.fetchall()
    conn.close()

    return render_template("chat.html", messages=messages, user_id=user_id)


# ---------- SOCKET EVENTS ----------

@socketio.on("join")
def join(data):
    join_room(data["room"])


@socketio.on("send_message")
def send_message(data):
    sender = session.get("user_id")
    if not sender:
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (sender_id, receiver_id, message, timestamp)
        VALUES (?, ?, ?, ?)
    """, (
        sender,
        data["receiver_id"],
        data["message"],
        datetime.now()
    ))

    conn.commit()
    conn.close()

    room = f"chat_{min(sender, data['receiver_id'])}_{max(sender, data['receiver_id'])}"

    emit("receive_message", {
        "sender_id": sender,
        "message": data["message"]
    }, room=room)
from flask import Blueprint, render_template, session
from flask_socketio import emit, join_room
from datetime import datetime
from models import get_connection
from extensions import socketio

chat_bp = Blueprint("chat", __name__)


@socketio.on("send_message")
def send_message(data):

    sender = session.get("user_id")

    if not sender:
        return

    receiver = data.get("receiver_id")
    message = data.get("message", "").strip()

    if not receiver or not message:
        return

    if len(message) > 2000:
        return

    room = f"chat_{min(sender, receiver)}_{max(sender, receiver)}"

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages (
                sender_id,
                receiver_id,
                message,
                timestamp
            )
            VALUES (?, ?, ?, ?)
        """, (
            sender,
            receiver,
            message,
            datetime.utcnow().isoformat()
        ))

        conn.commit()

    finally:
        conn.close()

    emit("receive_message", {
        "sender_id": sender,
        "message": message
    }, room=room)



@socketio.on("join")
def join(data):

    sender = session.get("user_id")

    if not sender:
        return

    receiver = data.get("receiver_id")

    if not receiver:
        return

    room = f"chat_{min(sender, receiver)}_{max(sender, receiver)}"

    join_room(room)
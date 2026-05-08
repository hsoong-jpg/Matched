from flask import Blueprint, render_template, session
from flask_socketio import emit, join_room
from datetime import datetime, timezone
from models import get_connection
from extensions import socketio

#Current time in UTR 
datetime.now(timezone.utc)
chat_bp = Blueprint("chat", __name__)

#when frontend sends "send_message" event run this function
@socketio.on("send_message")

#data is information sent from frontend 
def send_message(data):

    #Logged in person is the sender
    sender = session.get("user_id")

    #if user is not logged in then stop
    if not sender:
        return

    #receiver: who gets message, message: text, .strip():removes spaces
    receiver = data.get("receiver_id")
    message = data.get("message", "").strip()

    #Stops empty messages or missing receiver 
    if not receiver or not message:
        return

    #prevents spam
    if len(message) > 2000:
        return

    #Creates a unqiue room for every 2 users 
    #Use min and max so both users always get the same room name 
    room = f"chat_{min(sender, receiver)}_{max(sender, receiver)}"

    conn = get_connection()

    try:
        cursor = conn.cursor()

        #inserts new message row
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
            datetime.now(timezone.utc).isoformat()
        ))

        conn.commit()

    finally:
        conn.close()

    #emit.. room =room: send this event to only to users in this group chat
    emit("receive_message", {
        #Data that you need 
        "sender_id": sender,
        "message": message
    }, room=room)


#Joining a chat 
@socketio.on("join")
def join(data):

    sender = session.get("user_id")

    if not sender:
        return

    #who you want to talk to 
    receiver = data.get("receiver_id")

    if not receiver:
        return

    room = f"chat_{min(sender, receiver)}_{max(sender, receiver)}"

    join_room(room)
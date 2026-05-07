from flask import Flask
import os

from extensions import socketio

from routes.auth import auth
from routes.swipe import swipe_bp
from routes.matches import matches_bp
from routes.chat import chat_bp
from routes.inbox import inbox_bp
from routes.profile import profile_bp

from models import init_db


def create_app():
    app = Flask(__name__)

    # safer secret key
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

    # SocketIO
    socketio.init_app(app, cors_allowed_origins="*")

    # Blueprints
    app.register_blueprint(auth)
    app.register_blueprint(swipe_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(inbox_bp)
    app.register_blueprint(profile_bp)

    return app


app = create_app()

# initialize DB (dev-safe pattern)
with app.app_context():
    init_db()


if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
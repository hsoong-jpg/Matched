from flask import Flask
from extensions import socketio
from models import init_db

# Blueprints
from routes.auth import auth_bp
from routes.swipe import swipe_bp
from routes.matches import matches_bp
from routes.chat import chat_bp
from routes.inbox import inbox_bp
from routes.profile import profile_bp


def create_app():
    app = Flask(__name__)

    # SECURITY (you should move this to env later)
    app.config["SECRET_KEY"] = "secretkey"

    # INIT SOCKETIO
    socketio.init_app(app)

    # REGISTER BLUEPRINTS
    app.register_blueprint(auth_bp)
    app.register_blueprint(swipe_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(inbox_bp)
    app.register_blueprint(profile_bp)

    return app


app = create_app()


# ----------------------------
# INIT DATABASE ON STARTUP
# ----------------------------
with app.app_context():
    init_db()


# ----------------------------
# MAIN ENTRY
# ----------------------------
if __name__ == "__main__":
    socketio.run(app, debug=True)
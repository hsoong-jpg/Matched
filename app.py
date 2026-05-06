from flask import Flask
from extensions import socketio

def create_app():
    app = Flask(__name__)
    app.secret_key = "secretkey"

    socketio.init_app(app)

    # blueprints
    from routes.auth import auth
    from routes.swipe import swipe_bp
    from routes.matches import matches_bp
    from routes.chat import chat_bp
    from routes.inbox import inbox_bp

    app.register_blueprint(auth)
    app.register_blueprint(swipe_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(inbox_bp)

    return app


app = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True)
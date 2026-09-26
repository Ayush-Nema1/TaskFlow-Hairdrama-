from flask import Flask, jsonify
from flask_cors import CORS

from config import FRONTEND_URL, PORT


def create_app():
    app = Flask(__name__)

    # Only allow requests from our frontend.
    CORS(app, resources={r"/api/*": {"origins": FRONTEND_URL}})

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "message": "TaskFlow API is running"}), 200

    from routes.auth import auth_bp
    from routes.tasks import tasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)

    return app



app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)

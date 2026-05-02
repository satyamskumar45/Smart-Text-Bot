import logging
import os
import re

from flask import Flask, jsonify, request, current_app
from flask_cors import CORS
from pymongo.errors import PyMongoError
from werkzeug.exceptions import HTTPException

from config.settings import Settings
from database.db import init_db
from routes.auth_routes import auth_bp
from routes.chatbot_routes import chatbot_bp
from routes.dashboard_routes import dashboard_bp
from routes.grammar_routes import grammar_bp
from routes.image_routes import image_bp
from routes.sentiment_routes import sentiment_bp
from routes.summarize_routes import summarize_bp
from routes.translate_routes import translate_bp
from routes.voice_routes import voice_bp


def _validate_required_settings():
    if not Settings.JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY environment variable is required.")
    if not os.getenv("MONGO_URI"):
        raise RuntimeError("MONGO_URI environment variable is required.")


def create_app():
    _validate_required_settings()

    # Logging setup
    level = getattr(Settings, "LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(numeric_level)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))

    logging.root.setLevel(numeric_level)
    logging.root.addHandler(handler)

    # Init DB
    init_db()

    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    # ✅ FIX 1: flask-cors does NOT support compiled regex in `origins`.
    # Use a callable instead to match dynamic preview URLs.
    def origin_check(origin):
        if not origin:
            return False
        allowed_exact = {
            "https://smart-text-bot.pages.dev",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        }
        if origin in allowed_exact:
            return True
        # Match Cloudflare preview domains
        return bool(re.match(r"^https://.*\.smart-text-bot\.pages\.dev$", origin))

    CORS(
        app,
        supports_credentials=True,
        origins=origin_check,            # ✅ callable, not a list with regex
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        expose_headers=["Content-Type", "Authorization"],  # ✅ FIX 2: expose headers to client
        max_age=600,                     # ✅ FIX 3: cache preflight for 10 min
    )

    # ✅ FIX 4: Explicitly handle OPTIONS preflight so it never hits auth middleware
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            return app.make_default_options_response()

    # Logging requests
    @app.before_request
    def _log_request():
        current_app.logger.info("%s %s", request.method, request.path)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(translate_bp)
    app.register_blueprint(grammar_bp)
    app.register_blueprint(sentiment_bp)
    app.register_blueprint(summarize_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(voice_bp)

    # Error handlers
    @app.errorhandler(RuntimeError)
    def handle_runtime_error(error):
        return jsonify({"status": "fail", "message": str(error)}), 500

    @app.errorhandler(PyMongoError)
    def handle_pymongo_error(_error):
        return jsonify({"status": "fail", "message": "Database error"}), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({"status": "fail", "message": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled server error")
        return jsonify({
            "status": "fail",
            "message": str(error) if app.debug else "Internal server error."
        }), 500

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
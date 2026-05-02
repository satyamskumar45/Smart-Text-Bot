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


def _cors_origins():
    """
    Returns allowed CORS origins.
    Supports:
    - Production domain
    - All preview subdomains (smart-text-bot.pages.dev)
    - Local development
    """

    env_origins = os.getenv("FRONTEND_ORIGINS", "")

    # IMPORTANT: no "*" origin with supports_credentials=True.
    # Use strings (regex patterns or literal origins). We'll match them later.
    origins = [
        r"^https://([a-z0-9-]+\.)?smart-text-bot\.pages\.dev$",
        "https://smart-text-bot.pages.dev",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    origins.extend(
        origin.strip()
        for origin in env_origins.split(",")
        if origin.strip() and origin.strip() != "*" and "*" not in origin
    )

    return origins


def _validate_required_settings():
    if not Settings.JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY environment variable is required.")
    if not os.getenv("MONGO_URI"):
        raise RuntimeError("MONGO_URI environment variable is required.")


def create_app():
    _validate_required_settings()

    # Logging setup
    import logging
    level = getattr(Settings, "LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(numeric_level)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)

    logging.root.setLevel(numeric_level)
    logging.root.addHandler(handler)

    init_db()

    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    # CORS config
    # Apply Flask-CORS with permissive resource mapping but strict origin checking
    CORS(
        app,
        resources={r"/*": {"origins": _cors_origins()}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # Helper: check whether an origin is allowed by configured patterns
    allowed_origin_patterns = _cors_origins()

    def _origin_allowed(origin: str) -> bool:
        if not origin:
            return False
        for pattern in allowed_origin_patterns:
            try:
                # if pattern looks like a regex (starts with ^ or contains regex tokens)
                if pattern.startswith("^") or any(ch in pattern for ch in "\\().[]?+|$"):
                    if re.match(pattern, origin):
                        return True
                else:
                    if origin == pattern:
                        return True
            except re.error:
                # fallback to exact compare
                if origin == pattern:
                    return True
        return False

    # Log every request and its payload for debugging
    @app.before_request
    def _log_request():
        try:
            current_app.logger.info("%s %s", request.method, request.path)
            # only log small payloads
            data = request.get_data(as_text=True)
            if data:
                current_app.logger.debug("Request data: %s", data)
        except Exception:
            current_app.logger.exception("Error logging request")

    # Ensure CORS headers are set for all responses and handle OPTIONS preflight
    @app.after_request
    def _apply_cors_headers(response):
        origin = request.headers.get("Origin")
        if origin and _origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization, X-Requested-With"
            )
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        return response

    @app.route("/<path:_any>", methods=["OPTIONS"])
    @app.route("/", methods=["OPTIONS"])
    def _handle_options(_any=None):
        # Return a short-circuit response for preflight requests
        response = jsonify({"status": "ok"})
        origin = request.headers.get("Origin")
        if origin and _origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization, X-Requested-With"
            )
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        return response

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

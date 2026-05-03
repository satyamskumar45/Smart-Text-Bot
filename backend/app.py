import logging
import os
import re
from logging import StreamHandler

from flask import Flask, request, current_app
from flask_cors import CORS
from pymongo.errors import PyMongoError
from werkzeug.exceptions import HTTPException

from config.settings import Settings
from config.error_handlers import register_error_handlers
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


# ================= VALIDATION =================
def _validate_required_settings():
    if not Settings.JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY environment variable is required.")


# ================= APP FACTORY =================
def create_app():
    _validate_required_settings()

    # ================= LOGGING =================
    level = getattr(Settings, "LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.root.handlers.clear()
    handler = StreamHandler()
    handler.setLevel(numeric_level)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logging.root.setLevel(numeric_level)
    logging.root.addHandler(handler)

    app = Flask(__name__)
    app.config.from_object(Settings)
    app.config["JSON_SORT_KEYS"] = False

    # ================= CORS (FINAL FIX) =================
    FRONTEND_URL = "https://5664ca3c.smart-text-bot.pages.dev"

    CORS(
        app,
        resources={r"/*": {"origins": [FRONTEND_URL]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # 🔥 HARD CORS FIX (guarantees preflight works)
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")

        if origin and (
            origin == FRONTEND_URL
            or re.match(r"^https://.*\.smart-text-bot\.pages\.dev$", origin)
        ):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"

        return response

    # ================= DB INIT =================
    try:
        init_db()
    except Exception:
        app.logger.exception("Database initialization failed during startup")

    # ================= REQUEST LOGGING =================
    @app.before_request
    def log_request():
        current_app.logger.info("%s %s", request.method, request.path)

    # ================= HEALTH =================
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # ================= ROUTES =================
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(translate_bp)
    app.register_blueprint(grammar_bp)
    app.register_blueprint(sentiment_bp)
    app.register_blueprint(summarize_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(voice_bp)

    # ================= ERROR HANDLERS =================
    register_error_handlers(app)

    return app


# ================= ENTRY =================
app = create_app()


@app.route("/routes")
def list_routes():
    return {"routes": [str(rule) for rule in app.url_map.iter_rules()]}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
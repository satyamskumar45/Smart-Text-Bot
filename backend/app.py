import logging
import os
import re
from logging import StreamHandler

from flask import Flask, jsonify, request, current_app
from utils.response import error_response
from config.error_handlers import register_error_handlers
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

# ================= VALIDATION =================
def _validate_required_settings():
    if not Settings.JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY environment variable is required.")
    # Do not require MONGO_URI at startup to allow the app to boot without a DB during
    # early deployment steps. DB initialization is attempted in `init_db()` and
    # failures are logged; endpoints must handle DB unavailability.


# ================= CORS CHECK =================
def _is_allowed_origin(origin):
    if not origin:
        return False

    allowed_exact = {
        "https://smart-text-bot.pages.dev",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    }

    if origin in allowed_exact:
        return True

    # ✅ Allow Cloudflare preview URLs
    return bool(re.match(r"^https://.*\.smart-text-bot\.pages\.dev$", origin))


# ================= APP FACTORY =================
def create_app():
    _validate_required_settings()

    # Logging setup
    level = getattr(Settings, "LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Ensure we don't duplicate handlers when reloading in dev
    logging.root.handlers.clear()
    handler = StreamHandler()
    handler.setLevel(numeric_level)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logging.root.setLevel(numeric_level)
    logging.root.addHandler(handler)

    app = Flask(__name__)
    app.config.from_object(Settings)
    app.config["JSON_SORT_KEYS"] = False

    # ================= CORS =================
    allowed_origins_env = os.getenv(
        "ALLOWED_ORIGINS",
        "https://smart-text-bot.pages.dev,http://localhost:5173,http://127.0.0.1:5173",
    )
    allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
    # Allow Cloudflare preview pattern as well
    allowed_origins.append(r"^https://.*\\.smart-text-bot\\.pages\\.dev$")

    CORS(app, origins=allowed_origins, supports_credentials=True)

    # Init DB (attempt; will raise if misconfigured)
    try:
        init_db()
    except Exception:
        app.logger.exception("Database initialization failed during startup")

    # ================= LOG REQUESTS =================
    @app.before_request
    def _log_request():
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

    # Register centralized error handlers
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
import os
from flask import Flask, jsonify
from flask_cors import CORS
from pymongo.errors import PyMongoError
from werkzeug.exceptions import HTTPException

from database.db import init_db
from routes.auth_routes import auth_bp
from routes.chatbot_routes import chatbot_bp
from routes.dashboard_routes import dashboard_bp
from routes.grammar_routes import grammar_bp
from routes.translate_routes import translate_bp
from routes.voice_routes import voice_bp


def create_app():
    app = Flask(__name__)
    frontend_origins = [
        origin.strip()
        for origin in os.getenv("FRONTEND_ORIGINS", "").split(",")
        if origin.strip()
    ]
    if not frontend_origins:
        raise RuntimeError("FRONTEND_ORIGINS environment variable is required.")
    CORS(
        app,
        resources={r"/*": {"origins": frontend_origins}},
        supports_credentials=True,
    )

    try:
        init_db()
    except Exception:
        app.logger.exception("MongoDB startup initialization failed.")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(translate_bp)
    app.register_blueprint(grammar_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(voice_bp)

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"status": "fail", "message": "Route not found."}), 404

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify({"status": "fail", "message": "Internal server error."}), 500

    @app.errorhandler(RuntimeError)
    def runtime_error(error):
        return jsonify({"status": "fail", "message": str(error)}), 500

    @app.errorhandler(PyMongoError)
    def pymongo_error(_error):
        return jsonify({"status": "fail", "message": "Database error"}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        if isinstance(error, HTTPException):
            return jsonify({"status": "fail", "message": error.description}), error.code
        app.logger.exception("Unhandled server error")
        return jsonify({"status": "fail", "message": "Internal server error."}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run()
=======
from flask import Flask # type: ignore
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.history_routes import history_bp
from routes.translate_routes import translate_bp
from routes.grammar_routes import grammar_bp
from routes.chatbot_routes import chatbot_bp
from routes.voice_routes import voice_bp
from routes.summarize_routes import summarize_bp
from routes.image_routes import image_bp
from routes.context_routes import context_bp
from routes.sentiment_routes import sentiment_bp
from routes.doc_pipeline import doc_pipeline_bp
from routes.learning_routes import learning_bp
from middleware.rate_limiter import enforce_rate_limit

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

frontend_origins = os.getenv(
    'FRONTEND_ORIGINS',
    'http://localhost:5173,http://127.0.0.1:5173',
).split(',')

CORS(
    app,
    supports_credentials=True,
    origins=[origin.strip() for origin in frontend_origins if origin.strip()],
)

@app.before_request
def before_request_rate_limit():
    result = enforce_rate_limit()
    if result is not None:
        return result

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(history_bp)
app.register_blueprint(translate_bp)
app.register_blueprint(grammar_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(voice_bp)
app.register_blueprint(summarize_bp)
app.register_blueprint(image_bp)
app.register_blueprint(context_bp)
app.register_blueprint(sentiment_bp)
app.register_blueprint(doc_pipeline_bp)
app.register_blueprint(learning_bp)

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    debug = os.getenv('FLASK_ENV', 'development') != 'production'
    app.run(debug=debug, host=host, port=port)
>>>>>>> 7a39e76952f1835cf7031449b83138e654424a73

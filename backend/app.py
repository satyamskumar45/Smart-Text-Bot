import os
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

"""
Flask Application - Refactored with Clean Architecture
Entry point with proper middleware, error handling, and configuration.
"""

from flask import Flask
from flask_cors import CORS

# Import middleware
from middleware.error_handler import register_error_handlers

# Import routes (use refactored versions when ready)
from routes.auth_routes import auth_bp
from routes.translate_routes_refactored import translate_bp  # Refactored
from routes.grammar_routes import grammar_bp
from routes.chatbot_routes import chatbot_bp
from routes.voice_routes import voice_bp
from routes.summarize_routes import summarize_bp
from routes.image_routes import image_bp
from routes.context_routes import context_bp
from routes.sentiment_routes import sentiment_bp
from routes.doc_pipeline import doc_pipeline_bp

# Import configuration
from config.settings import Settings


def create_app() -> Flask:
    """
    Application factory pattern.
    Creates and configures the Flask application.
    """
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    blueprints = [
        (auth_bp, '/api/auth'),
        (translate_bp, '/api'),
        (grammar_bp, '/api'),
        (chatbot_bp, '/api'),
        (voice_bp, '/api'),
        (summarize_bp, '/api'),
        (image_bp, '/api'),
        (context_bp, '/api'),
        (sentiment_bp, '/api'),
        (doc_pipeline_bp, '/api'),
    ]
    
    for blueprint, url_prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)
        print(f"[APP] Registered blueprint: {blueprint.name} at {url_prefix}")
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return {
            'status': 'healthy',
            'service': 'SmartTextBot API',
            'version': '2.0.0'
        }
    
    print("[APP] Application initialized successfully")
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SmartTextBot API Server Starting...")
    print("="*60)
    print(f"📝 Log Level: {Settings.LOG_LEVEL}")
    print(f"🤖 Default Model: {Settings.DEFAULT_MODEL}")
    print(f"🔄 Max Retry Attempts: {Settings.MAX_RETRY_ATTEMPTS}")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

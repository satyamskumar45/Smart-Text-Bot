"""
Global error handler middleware.
Catches all exceptions and returns standardized error responses.
"""

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from core.exceptions import AppException, ValidationError, AIServiceError
from utils.response import error


def register_error_handlers(app: Flask):
    """Register global error handlers with Flask app"""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e: ValidationError):
        """Handle validation errors (400)"""
        print(f"[ERROR] Validation: {e.message}")
        return error(e.message, 400)
    
    @app.errorhandler(AIServiceError)
    def handle_ai_service_error(e: AIServiceError):
        """Handle AI service errors (500)"""
        print(f"[ERROR] AI Service: {e.message}")
        if e.original_error:
            print(f"[ERROR] Original: {str(e.original_error)}")
        return error(f"AI service error: {e.message}", 500)
    
    @app.errorhandler(AppException)
    def handle_app_exception(e: AppException):
        """Handle custom application exceptions"""
        print(f"[ERROR] App Exception: {e.message}")
        return error(e.message, e.status_code)
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        """Handle HTTP exceptions (404, 405, etc.)"""
        print(f"[ERROR] HTTP {e.code}: {e.description}")
        return error(e.description, e.code)
    
    @app.errorhandler(Exception)
    def handle_generic_exception(e: Exception):
        """Handle all other exceptions (500)"""
        print(f"[ERROR] Unhandled Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return error(f"Internal server error: {str(e)}", 500)
    
    print("[MIDDLEWARE] Error handlers registered")

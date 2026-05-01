"""
Custom exceptions for the application.
Provides specific error types for better error handling and debugging.
"""


class AppException(Exception):
    """Base exception for all application errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(AppException):
    """Raised when input validation fails"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class AIServiceError(AppException):
    """Raised when AI service calls fail"""
    def __init__(self, message: str, original_error: Exception = None):
        self.original_error = original_error
        super().__init__(message, status_code=500)


class OCRError(AppException):
    """Raised when OCR processing fails"""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class TranslationError(AIServiceError):
    """Raised when translation fails"""
    pass


class RateLimitError(AppException):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


class ConfigurationError(AppException):
    """Raised when configuration is invalid"""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

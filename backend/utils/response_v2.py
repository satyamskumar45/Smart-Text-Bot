"""
Standardized Response Format v2.0 - Product Quality Standards

All API responses follow a unified schema with consistent field naming,
metadata structure, and error handling across all modules.

Schema:
{
    "success": true|false,
    "data": {
        "output": "...",      # PRIMARY OUTPUT (standardized)
        "details": {...},     # Additional structured data
        "metrics": {...}      # Performance/quality metrics
    },
    "error": null | {...},
    "metadata": {
        "module": "...",
        "operation": "...",
        "timestamp": "...",
        ...
    }
}
"""

from flask import jsonify
from datetime import datetime
from typing import Any, Dict, Optional, List
import time


# ============================================================================
# ERROR CODES
# ============================================================================

class ErrorCode:
    """Standardized error codes across all modules."""
    
    # Client Errors (4xx)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MISSING_FIELD = "MISSING_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    INVALID_LANGUAGE = "INVALID_LANGUAGE"
    INVALID_MODE = "INVALID_MODE"
    TEXT_TOO_LONG = "TEXT_TOO_LONG"
    TEXT_TOO_SHORT = "TEXT_TOO_SHORT"
    UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    
    # Rate Limiting (429)
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # Server Errors (5xx)
    AI_SERVICE_ERROR = "AI_SERVICE_ERROR"
    OCR_ERROR = "OCR_ERROR"
    TRANSLATION_ERROR = "TRANSLATION_ERROR"
    SUMMARIZATION_ERROR = "SUMMARIZATION_ERROR"
    GRAMMAR_ERROR = "GRAMMAR_ERROR"
    CHAT_ERROR = "CHAT_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


# ============================================================================
# MODULE NAMES
# ============================================================================

class Module:
    """Standardized module names."""
    TRANSLATOR = "translator"
    SUMMARIZER = "summarizer"
    WRITING_ASSISTANT = "writing_assistant"
    CHATBOT = "chatbot"
    DOCUMENT_PIPELINE = "document_pipeline"
    OCR = "ocr"
    INTELLIGENCE = "intelligence"


# ============================================================================
# METADATA BUILDER
# ============================================================================

class MetadataBuilder:
    """Build standardized metadata for responses."""
    
    def __init__(self, module: str, operation: str):
        self.metadata = {
            'module': module,
            'operation': operation,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def add_processing_time(self, start_time: float) -> 'MetadataBuilder':
        """Add processing time in milliseconds."""
        processing_time = int((time.time() - start_time) * 1000)
        self.metadata['processing_time_ms'] = processing_time
        return self
    
    def add_model(self, model: str) -> 'MetadataBuilder':
        """Add model used for processing."""
        self.metadata['model_used'] = model
        return self
    
    def add_tokens(self, tokens: int) -> 'MetadataBuilder':
        """Add token count."""
        self.metadata['tokens_used'] = tokens
        return self
    
    def add_confidence(self, confidence: float) -> 'MetadataBuilder':
        """Add confidence score (0.0 to 1.0)."""
        self.metadata['confidence'] = round(confidence, 2)
        return self
    
    def add_version(self, version: str) -> 'MetadataBuilder':
        """Add API version."""
        self.metadata['version'] = version
        return self
    
    def add_custom(self, key: str, value: Any) -> 'MetadataBuilder':
        """Add custom metadata field."""
        self.metadata[key] = value
        return self
    
    def build(self) -> Dict:
        """Return built metadata dictionary."""
        return self.metadata


# ============================================================================
# RESPONSE FORMATTERS
# ============================================================================

def success(
    output: Any,
    module: str,
    operation: str,
    details: Optional[Dict] = None,
    metrics: Optional[Dict] = None,
    metadata: Optional[Dict] = None,
    status_code: int = 200
):
    """
    Return standardized success response.
    
    Args:
        output: Primary output (main result)
        module: Module name (use Module constants)
        operation: Operation name
        details: Additional structured data
        metrics: Performance/quality metrics
        metadata: Additional metadata fields
        status_code: HTTP status code
    
    Returns:
        Flask JSON response with standardized schema
    
    Example:
        return success(
            output="Translated text",
            module=Module.TRANSLATOR,
            operation="translate",
            details={'source_lang': 'en', 'target_lang': 'es'},
            metrics={'confidence': 0.95, 'processing_time_ms': 850}
        )
    """
    # Build data object
    data = {'output': output}
    
    if details:
        data['details'] = details
    
    if metrics:
        data['metrics'] = metrics
    
    # Build metadata
    meta = {
        'module': module,
        'operation': operation,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    if metadata:
        meta.update(metadata)
    
    # Build response
    response = {
        'success': True,
        'data': data,
        'error': None,
        'metadata': meta
    }
    
    return jsonify(response), status_code


def error(
    message: str,
    code: str,
    module: Optional[str] = None,
    operation: Optional[str] = None,
    details: Optional[str] = None,
    field: Optional[str] = None,
    status_code: int = 400
):
    """
    Return standardized error response.
    
    Args:
        message: User-friendly error message
        code: Error code (use ErrorCode constants)
        module: Module name (use Module constants)
        operation: Operation name
        details: Technical details for debugging
        field: Field that caused the error
        status_code: HTTP status code
    
    Returns:
        Flask JSON response with standardized error schema
    
    Example:
        return error(
            message="No text provided. Please include text in your request.",
            code=ErrorCode.MISSING_FIELD,
            module=Module.TRANSLATOR,
            operation="translate",
            field="text",
            status_code=400
        )
    """
    # Build error object
    error_obj = {
        'message': message,
        'code': code
    }
    
    if details:
        error_obj['details'] = details
    
    if field:
        error_obj['field'] = field
    
    # Build metadata
    meta = {
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    if module:
        meta['module'] = module
    
    if operation:
        meta['operation'] = operation
    
    # Build response
    response = {
        'success': False,
        'data': None,
        'error': error_obj,
        'metadata': meta
    }
    
    return jsonify(response), status_code


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_translation_response(
    translated_text: str,
    source_lang: str,
    target_lang: str,
    detected_lang: Optional[str] = None,
    word_count: Optional[int] = None,
    confidence: Optional[float] = None,
    processing_time_ms: Optional[int] = None,
    model: str = "llama-3.1-8b-instant"
):
    """Format translation response with standardized schema."""
    details = {
        'source_lang': source_lang,
        'target_lang': target_lang
    }
    
    if detected_lang:
        details['detected_lang'] = detected_lang
    
    if word_count:
        details['word_count'] = word_count
    
    metrics = {}
    if confidence is not None:
        metrics['confidence'] = round(confidence, 2)
    
    if processing_time_ms is not None:
        metrics['processing_time_ms'] = processing_time_ms
    
    metadata = {'model_used': model}
    
    return success(
        output=translated_text,
        module=Module.TRANSLATOR,
        operation="translate",
        details=details,
        metrics=metrics if metrics else None,
        metadata=metadata
    )


def format_summary_response(
    summary: str,
    bullets: List[str],
    original_word_count: int,
    summary_word_count: int,
    compression_ratio: Optional[float] = None,
    confidence: Optional[float] = None,
    processing_time_ms: Optional[int] = None,
    model: str = "llama-3.1-8b-instant"
):
    """Format summarization response with standardized schema."""
    details = {
        'bullets': bullets,
        'original_word_count': original_word_count,
        'summary_word_count': summary_word_count
    }
    
    if compression_ratio:
        details['compression_ratio'] = round(compression_ratio, 2)
    
    metrics = {}
    if confidence is not None:
        metrics['confidence'] = round(confidence, 2)
    
    if processing_time_ms is not None:
        metrics['processing_time_ms'] = processing_time_ms
    
    metadata = {'model_used': model}
    
    return success(
        output=summary,
        module=Module.SUMMARIZER,
        operation="summarize",
        details=details,
        metrics=metrics if metrics else None,
        metadata=metadata
    )


def format_grammar_response(
    corrected_text: str,
    mode: str,
    changes: List[Dict],
    tone_style: Optional[str] = None,
    improvement_score: Optional[float] = None,
    confidence: Optional[float] = None,
    processing_time_ms: Optional[int] = None,
    model: str = "llama-3.1-8b-instant"
):
    """Format grammar/writing assistant response with standardized schema."""
    details = {
        'mode': mode,
        'changes': changes,
        'change_count': len(changes)
    }
    
    if tone_style:
        details['tone_style'] = tone_style
    
    if improvement_score is not None:
        details['improvement_score'] = round(improvement_score, 2)
    
    metrics = {}
    if confidence is not None:
        metrics['confidence'] = round(confidence, 2)
    
    if processing_time_ms is not None:
        metrics['processing_time_ms'] = processing_time_ms
    
    metadata = {'model_used': model}
    
    return success(
        output=corrected_text,
        module=Module.WRITING_ASSISTANT,
        operation="grammar_check",
        details=details,
        metrics=metrics if metrics else None,
        metadata=metadata
    )


def format_chat_response(
    reply: str,
    conversation_id: Optional[str] = None,
    message_count: Optional[int] = None,
    context: Optional[str] = None,
    suggested_actions: Optional[List[str]] = None,
    confidence: Optional[float] = None,
    processing_time_ms: Optional[int] = None,
    model: str = "llama-3.1-8b-instant"
):
    """Format chatbot response with standardized schema."""
    details = {}
    
    if conversation_id:
        details['conversation_id'] = conversation_id
    
    if message_count is not None:
        details['message_count'] = message_count
    
    if context:
        details['context'] = context
    
    if suggested_actions:
        details['suggested_actions'] = suggested_actions
    
    metrics = {}
    if confidence is not None:
        metrics['confidence'] = round(confidence, 2)
    
    if processing_time_ms is not None:
        metrics['processing_time_ms'] = processing_time_ms
    
    metadata = {'model_used': model}
    
    return success(
        output=reply,
        module=Module.CHATBOT,
        operation="chat",
        details=details if details else None,
        metrics=metrics if metrics else None,
        metadata=metadata
    )


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_required_field(data: Dict, field: str, module: str, operation: str):
    """
    Validate that a required field exists and is not empty.
    
    Returns error response if validation fails, None if valid.
    """
    if not data:
        return error(
            message="Request body must be JSON.",
            code=ErrorCode.INVALID_FORMAT,
            module=module,
            operation=operation,
            status_code=400
        )
    
    value = data.get(field, '').strip() if isinstance(data.get(field), str) else data.get(field)
    
    if not value:
        return error(
            message=f"No {field} provided. Please include {field} in your request.",
            code=ErrorCode.MISSING_FIELD,
            module=module,
            operation=operation,
            field=field,
            status_code=400
        )
    
    return None


def validate_text_length(
    text: str,
    min_length: int = 1,
    max_length: int = 50000,
    module: str = None,
    operation: str = None
):
    """
    Validate text length.
    
    Returns error response if validation fails, None if valid.
    """
    text_length = len(text)
    
    if text_length < min_length:
        return error(
            message=f"Text is too short. Minimum length is {min_length} characters.",
            code=ErrorCode.TEXT_TOO_SHORT,
            module=module,
            operation=operation,
            details=f"Provided: {text_length} characters",
            status_code=400
        )
    
    if text_length > max_length:
        return error(
            message=f"Text is too long. Maximum length is {max_length} characters.",
            code=ErrorCode.TEXT_TOO_LONG,
            module=module,
            operation=operation,
            details=f"Provided: {text_length} characters",
            status_code=400
        )
    
    return None


# ============================================================================
# BACKWARD COMPATIBILITY (DEPRECATED)
# ============================================================================

def success_legacy(data, status_code=200):
    """
    DEPRECATED: Legacy success response format.
    Use success() with new standardized schema instead.
    """
    return jsonify({
        'success': True,
        'data': data,
        'error': None
    }), status_code


def error_legacy(message, status_code=400):
    """
    DEPRECATED: Legacy error response format.
    Use error() with new standardized schema instead.
    """
    return jsonify({
        'success': False,
        'data': None,
        'error': message
    }), status_code

"""
Input validation utilities.
Validates and sanitizes request data before processing.
"""

from typing import Dict, Any
from core.exceptions import ValidationError
from config.settings import Settings


def validate_text_input(text: str, min_length: int = 1, max_length: int = 50000) -> str:
    """Validate text input"""
    if not text or not isinstance(text, str):
        raise ValidationError("Text must be a non-empty string")
    
    text = text.strip()
    
    if len(text) < min_length:
        raise ValidationError(f"Text must be at least {min_length} characters")
    
    if len(text) > max_length:
        raise ValidationError(f"Text must not exceed {max_length} characters")
    
    return text


def validate_language_code(code: str) -> str:
    """Validate language code"""
    if not code or not isinstance(code, str):
        raise ValidationError("Language code must be a non-empty string")
    
    code = code.strip().lower()
    
    if code == "auto":
        return code
    
    if code not in Settings.SUPPORTED_LANGUAGES:
        raise ValidationError(
            f"Unsupported language code: {code}. "
            f"Supported: {', '.join(Settings.SUPPORTED_LANGUAGES.keys())}"
        )
    
    return code


def validate_translation_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate translation request data"""
    if not data:
        raise ValidationError("Request body must be JSON")
    
    text = validate_text_input(data.get('text', ''))
    target_lang = validate_language_code(data.get('target_lang', 'en'))
    source_lang = validate_language_code(data.get('source_lang', 'auto'))
    
    return {
        'text': text,
        'target_lang': target_lang,
        'source_lang': source_lang
    }


def validate_grammar_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate grammar/rewrite request data"""
    if not data:
        raise ValidationError("Request body must be JSON")
    
    text = validate_text_input(data.get('text', ''))
    mode = data.get('mode', 'grammar').lower()
    
    valid_modes = ['grammar', 'tone', 'rewrite']
    if mode not in valid_modes:
        raise ValidationError(f"Invalid mode. Must be one of: {', '.join(valid_modes)}")
    
    tone_style = data.get('tone_style', 'professional').lower()
    valid_tones = ['formal', 'professional', 'academic', 'casual', 'friendly']
    if tone_style not in valid_tones:
        raise ValidationError(f"Invalid tone_style. Must be one of: {', '.join(valid_tones)}")
    
    return {
        'text': text,
        'mode': mode,
        'tone_style': tone_style
    }


def validate_summarization_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate summarization request data"""
    if not data:
        raise ValidationError("Request body must be JSON")
    
    text = validate_text_input(data.get('text', ''), min_length=50)
    
    return {'text': text}


def validate_chat_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate chat request data"""
    if not data:
        raise ValidationError("Request body must be JSON")
    
    message = validate_text_input(data.get('message', ''))
    history = data.get('history', [])
    
    if not isinstance(history, list):
        raise ValidationError("History must be an array")
    
    return {
        'message': message,
        'history': history
    }

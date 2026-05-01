"""
Translation Routes - Refactored with clean architecture.
Routes only handle HTTP concerns, business logic is in services.
"""

from flask import Blueprint, request
from services.text.translation_service import TranslationService
from utils.validators import validate_translation_request
from utils.response import success, error
from core.exceptions import ValidationError, TranslationError

translate_bp = Blueprint('translate', __name__)

# Initialize service
translation_service = TranslationService()


@translate_bp.route('/translate', methods=['POST'])
def translate():
    """
    Translate text to target language.
    
    Request: { "text": "...", "target_lang": "en", "source_lang": "auto" }
    Response: { "success": true, "data": {...}, "error": null }
    """
    try:
        # Validate input
        data = validate_translation_request(request.json)
        
        # Call service
        result = translation_service.translate(
            text=data['text'],
            target_lang=data['target_lang'],
            source_lang=data['source_lang']
        )
        
        return success(result)
        
    except ValidationError as e:
        return error(str(e), 400)
    except TranslationError as e:
        return error(str(e), 500)


@translate_bp.route('/explain', methods=['POST'])
def explain():
    """
    Explain a translation.
    
    Request: { "original": "...", "translation": "..." }
    Response: { "success": true, "data": { "explanation": "..." }, "error": null }
    """
    try:
        data = request.json
        
        if not data:
            raise ValidationError("Request body must be JSON")
        
        original = data.get('original', '').strip()
        translation = data.get('translation', '').strip()
        
        if not original:
            raise ValidationError("No original text provided")
        
        if not translation:
            raise ValidationError("No translation provided")
        
        # Call service
        result = translation_service.explain_translation(original, translation)
        
        return success(result)
        
    except ValidationError as e:
        return error(str(e), 400)
    except TranslationError as e:
        return error(str(e), 500)


@translate_bp.route('/batch-translate', methods=['POST'])
def batch_translate():
    """
    Translate multiple texts at once.
    
    Request: { "texts": ["...", "..."], "target_lang": "en", "source_lang": "auto" }
    Response: { "success": true, "data": { "results": [...] }, "error": null }
    """
    try:
        data = request.json
        
        if not data:
            raise ValidationError("Request body must be JSON")
        
        texts = data.get('texts', [])
        target_lang = data.get('target_lang', 'en')
        source_lang = data.get('source_lang', 'auto')
        
        if not isinstance(texts, list) or not texts:
            raise ValidationError("texts must be a non-empty array")
        
        # Call service
        results = translation_service.batch_translate(texts, target_lang, source_lang)
        
        return success({'results': results})
        
    except ValidationError as e:
        return error(str(e), 400)
    except TranslationError as e:
        return error(str(e), 500)

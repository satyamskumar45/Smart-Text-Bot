"""
EXAMPLE: Refactored Routes with Standardized Response Schema

This file demonstrates how to refactor existing routes to use the new
standardized response format. Use these examples as templates for updating
all modules.

Key Changes:
1. Use 'output' field for primary result (not 'result', 'translated_text', etc.)
2. Include 'details' for additional structured data
3. Include 'metrics' for performance/quality measurements
4. Include standardized 'metadata' with module, operation, timestamp
5. Use ErrorCode constants for consistent error handling
6. Use Module constants for module names
"""

import time
from flask import Blueprint, request
from config.settings import Settings
from services.groq_service import complete, translate_text, complete_json
from utils.response_v2 import (
    success, error, 
    ErrorCode, Module,
    MetadataBuilder,
    format_translation_response,
    format_summary_response,
    format_grammar_response,
    format_chat_response,
    validate_required_field,
    validate_text_length
)
import json


# ============================================================================
# TRANSLATION MODULE - REFACTORED
# ============================================================================

translate_bp_v2 = Blueprint('translate_v2', __name__)


@translate_bp_v2.route('/translate', methods=['POST'])
def translate():
    """
    Translate text to target language.
    
    Request:
        {
            "text": "Hello world",
            "target_lang": "es",
            "source_lang": "auto"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "output": "Hola mundo",
                "details": {
                    "source_lang": "auto",
                    "target_lang": "es",
                    "detected_lang": "en",
                    "word_count": 2
                },
                "metrics": {
                    "confidence": 0.98,
                    "processing_time_ms": 850
                }
            },
            "error": null,
            "metadata": {
                "module": "translator",
                "operation": "translate",
                "timestamp": "2024-01-15T10:30:00Z",
                "model_used": "llama-3.1-8b-instant"
            }
        }
    """
    start_time = time.time()
    
    try:
        data = request.json
        
        # Validate required fields
        validation_error = validate_required_field(data, 'text', Module.TRANSLATOR, 'translate')
        if validation_error:
            return validation_error
        
        validation_error = validate_required_field(data, 'target_lang', Module.TRANSLATOR, 'translate')
        if validation_error:
            return validation_error
        
        text = data['text'].strip()
        target_lang = data['target_lang'].strip()
        source_lang = data.get('source_lang', 'auto').strip()
        
        # Validate text length
        length_error = validate_text_length(
            text, 
            min_length=1, 
            max_length=10000,
            module=Module.TRANSLATOR,
            operation='translate'
        )
        if length_error:
            return length_error
        
        # Validate language code
        if target_lang.lower() not in Settings.SUPPORTED_LANGUAGES:
            return error(
                message=f"Invalid target language '{target_lang}'. Supported languages: {', '.join(Settings.SUPPORTED_LANGUAGES.keys())}",
                code=ErrorCode.INVALID_LANGUAGE,
                module=Module.TRANSLATOR,
                operation="translate",
                field="target_lang",
                status_code=400
            )
        
        # Perform translation
        print(f"[TRANSLATE] Translating to {target_lang}...")
        translated = translate_text(text, target_lang, source_lang)
        
        # Calculate metrics
        processing_time = int((time.time() - start_time) * 1000)
        word_count = len(text.split())
        
        # Build response using helper
        return format_translation_response(
            translated_text=translated,
            source_lang=source_lang,
            target_lang=target_lang,
            detected_lang="en",  # TODO: Add language detection
            word_count=word_count,
            confidence=0.95,
            processing_time_ms=processing_time
        )
        
    except ValueError as e:
        return error(
            message="Invalid input provided.",
            code=ErrorCode.VALIDATION_ERROR,
            module=Module.TRANSLATOR,
            operation="translate",
            details=str(e),
            status_code=400
        )
    except Exception as e:
        return error(
            message="Translation failed. Please try again.",
            code=ErrorCode.TRANSLATION_ERROR,
            module=Module.TRANSLATOR,
            operation="translate",
            details=str(e),
            status_code=500
        )


@translate_bp_v2.route('/translate/explain', methods=['POST'])
def explain():
    """
    Explain a translation.
    
    Request:
        {
            "original": "Hello world",
            "translation": "Hola mundo",
            "source_lang": "en",
            "target_lang": "es"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "output": "This is a direct translation...",
                "details": {
                    "explanation_type": "linguistic",
                    "key_points": [...]
                },
                "metrics": {
                    "processing_time_ms": 650
                }
            },
            "error": null,
            "metadata": {...}
        }
    """
    start_time = time.time()
    
    try:
        data = request.json
        
        # Validate required fields
        validation_error = validate_required_field(data, 'original', Module.TRANSLATOR, 'explain')
        if validation_error:
            return validation_error
        
        validation_error = validate_required_field(data, 'translation', Module.TRANSLATOR, 'explain')
        if validation_error:
            return validation_error
        
        original = data['original'].strip()
        translation = data['translation'].strip()
        
        # Generate explanation
        system = "You are an expert linguist and translator. Provide clear, concise explanations."
        user = (
            f"Explain this translation in 3-5 lines:\n\n"
            f"Original: {original}\n"
            f"Translation: {translation}"
        )
        
        explanation = complete(system, user)
        
        # Calculate metrics
        processing_time = int((time.time() - start_time) * 1000)
        
        # Build response
        return success(
            output=explanation,
            module=Module.TRANSLATOR,
            operation="explain",
            details={
                'explanation_type': 'linguistic',
                'original_length': len(original),
                'translation_length': len(translation)
            },
            metrics={
                'processing_time_ms': processing_time
            },
            metadata={
                'model_used': 'llama-3.1-8b-instant'
            }
        )
        
    except Exception as e:
        return error(
            message="Explanation generation failed. Please try again.",
            code=ErrorCode.AI_SERVICE_ERROR,
            module=Module.TRANSLATOR,
            operation="explain",
            details=str(e),
            status_code=500
        )


# ============================================================================
# SUMMARIZATION MODULE - REFACTORED
# ============================================================================

summarize_bp_v2 = Blueprint('summarize_v2', __name__)


@summarize_bp_v2.route('/summarize', methods=['POST'])
def summarize():
    """
    Summarize provided text.
    
    Request:
        {
            "text": "Long document text...",
            "length": "medium",
            "format": "bullets"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "output": "Concise 2-3 sentence summary",
                "details": {
                    "bullets": [...],
                    "compression_ratio": 0.15,
                    "original_word_count": 500,
                    "summary_word_count": 75
                },
                "metrics": {
                    "processing_time_ms": 1200,
                    "confidence": 0.92
                }
            },
            "error": null,
            "metadata": {...}
        }
    """
    start_time = time.time()
    
    try:
        data = request.json
        
        # Validate required field
        validation_error = validate_required_field(data, 'text', Module.SUMMARIZER, 'summarize')
        if validation_error:
            return validation_error
        
        text = data['text'].strip()
        
        # Validate text length
        length_error = validate_text_length(
            text,
            min_length=50,
            max_length=50000,
            module=Module.SUMMARIZER,
            operation='summarize'
        )
        if length_error:
            return length_error
        
        # Generate summary
        system = (
            "You are an expert summarizer. Return a JSON object with two keys: "
            "'paragraph' (a concise 2-3 sentence summary) and "
            "'bullets' (an array of 4-6 key bullet point strings). "
            "Return ONLY the JSON object."
        )
        user = f"Summarize the following text:\n\n{text}"
        
        raw = complete_json(system, user)
        result = json.loads(raw)
        
        # Extract data
        summary = result.get('paragraph', '')
        bullets = result.get('bullets', [])
        
        # Calculate metrics
        processing_time = int((time.time() - start_time) * 1000)
        original_word_count = len(text.split())
        summary_word_count = len(summary.split())
        compression_ratio = summary_word_count / original_word_count if original_word_count > 0 else 0
        
        # Build response using helper
        return format_summary_response(
            summary=summary,
            bullets=bullets,
            original_word_count=original_word_count,
            summary_word_count=summary_word_count,
            compression_ratio=compression_ratio,
            confidence=0.92,
            processing_time_ms=processing_time
        )
        
    except json.JSONDecodeError as e:
        return error(
            message="Failed to parse summary response.",
            code=ErrorCode.INVALID_FORMAT,
            module=Module.SUMMARIZER,
            operation="summarize",
            details=str(e),
            status_code=500
        )
    except Exception as e:
        return error(
            message="Summarization failed. Please try again.",
            code=ErrorCode.SUMMARIZATION_ERROR,
            module=Module.SUMMARIZER,
            operation="summarize",
            details=str(e),
            status_code=500
        )


# ============================================================================
# GRAMMAR/WRITING ASSISTANT MODULE - REFACTORED
# ============================================================================

grammar_bp_v2 = Blueprint('grammar_v2', __name__)

TONE_STYLES = {
    'formal': 'very formal and official',
    'professional': 'professional and business-appropriate',
    'academic': 'academic and scholarly',
    'casual': 'casual and conversational',
    'friendly': 'warm, friendly, and approachable',
}


@grammar_bp_v2.route('/grammar', methods=['POST'])
def grammar():
    """
    Fix grammar or rewrite text with specified tone.
    
    Request:
        {
            "text": "Text with errors",
            "mode": "grammar",
            "tone_style": "professional"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "output": "Corrected text",
                "details": {
                    "mode": "grammar",
                    "tone_style": "professional",
                    "changes": [...],
                    "change_count": 2,
                    "improvement_score": 0.85
                },
                "metrics": {
                    "processing_time_ms": 950,
                    "confidence": 0.94
                }
            },
            "error": null,
            "metadata": {...}
        }
    """
    start_time = time.time()
    
    try:
        data = request.json
        
        # Validate required field
        validation_error = validate_required_field(data, 'text', Module.WRITING_ASSISTANT, 'grammar_check')
        if validation_error:
            return validation_error
        
        text = data['text'].strip()
        mode = data.get('mode', 'grammar').lower()
        tone_style = data.get('tone_style', 'professional').lower()
        
        # Validate mode
        if mode not in ['grammar', 'tone', 'rewrite']:
            return error(
                message=f"Invalid mode '{mode}'. Supported modes: grammar, tone, rewrite",
                code=ErrorCode.INVALID_MODE,
                module=Module.WRITING_ASSISTANT,
                operation="grammar_check",
                field="mode",
                status_code=400
            )
        
        # Build prompt based on mode
        if mode == 'grammar':
            system = (
                "You are a professional editor. Fix all grammar, spelling, punctuation, and syntax errors. "
                "Return a JSON object with two keys: "
                "'result' (the corrected text) and "
                "'changes' (array of strings describing each correction made). "
                "If no corrections are needed, set changes to an empty array. Return ONLY the JSON."
            )
            user = f"Fix the grammar and spelling in this text:\n\n{text}"
        
        elif mode == 'tone':
            style = TONE_STYLES.get(tone_style, TONE_STYLES['professional'])
            system = (
                f"You are an expert writing coach. Rewrite the text to have a {style} tone. "
                "Return a JSON object with two keys: "
                "'result' (the rewritten text) and "
                "'changes' (array of strings noting the tone improvements made). Return ONLY the JSON."
            )
            user = f"Improve the tone of this text to be {tone_style}:\n\n{text}"
        
        else:  # rewrite
            system = (
                "You are a skilled writer. Rewrite the given text to make it clearer, more engaging, "
                "and better structured while preserving the original meaning. "
                "Return a JSON object with two keys: "
                "'result' (the rewritten text) and "
                "'changes' (array of strings describing improvements made). Return ONLY the JSON."
            )
            user = f"Rewrite and improve this text:\n\n{text}"
        
        # Generate result
        raw = complete_json(system, user)
        result = json.loads(raw)
        
        corrected_text = result.get('result', text)
        changes = result.get('changes', [])
        
        # Calculate metrics
        processing_time = int((time.time() - start_time) * 1000)
        
        # Build response using helper
        return format_grammar_response(
            corrected_text=corrected_text,
            mode=mode,
            changes=changes,
            tone_style=tone_style if mode == 'tone' else None,
            improvement_score=0.85,
            confidence=0.94,
            processing_time_ms=processing_time
        )
        
    except json.JSONDecodeError as e:
        return error(
            message="Failed to parse grammar check response.",
            code=ErrorCode.INVALID_FORMAT,
            module=Module.WRITING_ASSISTANT,
            operation="grammar_check",
            details=str(e),
            status_code=500
        )
    except Exception as e:
        return error(
            message="Grammar processing failed. Please try again.",
            code=ErrorCode.GRAMMAR_ERROR,
            module=Module.WRITING_ASSISTANT,
            operation="grammar_check",
            details=str(e),
            status_code=500
        )


# ============================================================================
# CHATBOT MODULE - REFACTORED
# ============================================================================

chatbot_bp_v2 = Blueprint('chatbot_v2', __name__)

SYSTEM_PROMPT = (
    "You are SmartTextBot, an intelligent AI language assistant. "
    "You help users with translation, text analysis, writing improvement, and language questions. "
    "Be helpful, concise, and friendly."
)


@chatbot_bp_v2.route('/chat', methods=['POST'])
def chat():
    """
    Chat with the AI assistant.
    
    Request:
        {
            "message": "How do I translate text?",
            "history": [...],
            "context": "translation"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "output": "To translate text, you can use...",
                "details": {
                    "conversation_id": "conv_123456",
                    "message_count": 3,
                    "context": "translation",
                    "suggested_actions": [...]
                },
                "metrics": {
                    "processing_time_ms": 800,
                    "confidence": 0.91
                }
            },
            "error": null,
            "metadata": {...}
        }
    """
    start_time = time.time()
    
    try:
        data = request.json
        
        # Validate required field
        validation_error = validate_required_field(data, 'message', Module.CHATBOT, 'chat')
        if validation_error:
            return validation_error
        
        message = data['message'].strip()
        history = data.get('history', [])
        context = data.get('context', None)
        
        # Generate reply
        reply = complete(SYSTEM_PROMPT, message, model="llama-3.1-8b-instant")
        
        # Calculate metrics
        processing_time = int((time.time() - start_time) * 1000)
        
        # Build response using helper
        return format_chat_response(
            reply=reply,
            conversation_id=None,  # TODO: Add conversation tracking
            message_count=len(history) + 1,
            context=context,
            suggested_actions=None,  # TODO: Add action suggestions
            confidence=0.91,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        return error(
            message="Chat processing failed. Please try again.",
            code=ErrorCode.CHAT_ERROR,
            module=Module.CHATBOT,
            operation="chat",
            details=str(e),
            status_code=500
        )


# ============================================================================
# USAGE NOTES
# ============================================================================

"""
MIGRATION CHECKLIST:

1. Import new response utilities:
   from utils.response_v2 import success, error, ErrorCode, Module

2. Replace all 'result', 'translated_text', 'reply' fields with 'output'

3. Add 'details' dict for additional structured data

4. Add 'metrics' dict for performance/quality measurements

5. Use Module constants for module names

6. Use ErrorCode constants for error codes

7. Add processing time tracking with time.time()

8. Use helper functions (format_translation_response, etc.) when available

9. Add proper validation with validate_required_field and validate_text_length

10. Update error messages to be user-friendly and actionable

11. Test all endpoints with new schema

12. Update frontend to handle new response structure

13. Update API documentation
"""

import json
import re
from flask import Blueprint, request, g
from services.groq_service import complete, complete_json, translate_text
from services.history_service import save_history_entry
from services.auth_service import track_guest_usage
from middleware.auth_middleware import optional_auth
from utils.response import success, error

translate_bp = Blueprint('translate', __name__)

def extract_json(text):
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass
    return None


@translate_bp.route('/translate', methods=['POST'])
@optional_auth
def translate():
    """
    Translate text to target language.
    
    Request: { "text": "...", "target_lang": "en", "source_lang": "auto" }
    Response: { "success": true, "data": { "translated_text": "...", "source_lang": "...", "target_lang": "..." }, "error": null }
    """
    print("[TRANSLATE] POST /translate endpoint called")
    try:
        data = request.get_json(silent=True)
        print(f"[DEBUG] Request data: {data}")
        
        if not data:
            return error("Request body must be JSON", 400)
        
        text = data.get('text', '').strip()
        target_lang = data.get('target_lang', 'en').strip()
        source_lang = data.get('source_lang', 'auto').strip()
        
        print(f"[DEBUG] Extracted values: text={text[:50]}..., target={target_lang}, source={source_lang}")

        if not text:
            return error("No text provided", 400)
        
        if not target_lang:
            return error("No target language provided", 400)

        print("[TRANSLATE] Calling translate_text function...")
        translated = translate_text(text, target_lang, source_lang)
        
        translate_data = {
            'translated_text': translated,
            'source_lang': source_lang,
            'target_lang': target_lang
        }

        current = getattr(g, 'current_user', None)
        if current:
            save_history_entry(
                user_id=current.get('id') if current.get('role') == 'user' else None,
                guest_session_id=current.get('guest_session_id') if current.get('role') == 'guest' else None,
                module_type='translation',
                input_text=text,
                output_text=translated,
                metadata=json.dumps({'source_lang': source_lang, 'target_lang': target_lang}),
            )
            if current.get('role') == 'guest':
                track_guest_usage(current.get('guest_session_id'), 'translations')

        print(f"[TRANSLATE] Successfully translated text")
        return success(translate_data)

    except ValueError as e:
        print(f"[ERROR] ValueError in translate: {str(e)}")
        return error(f"Invalid input: {str(e)}", 400)
    except Exception as e:
        print(f"[ERROR] Exception in translate: {str(e)}")
        import traceback
        traceback.print_exc()
        return error(f"Translation failed: {str(e)}", 500)


@translate_bp.route('/explain', methods=['POST'])
def explain():
    """
    Explain a translation.
    
    Request: { "original": "...", "translation": "...", "source_lang": "...", "target_lang": "..." }
    Response: { "success": true, "data": { "explanation": "..." }, "error": null }
    """
    print("[EXPLAIN] POST /explain endpoint called")
    try:
        data = request.get_json(silent=True)
        print(f"[DEBUG] Request data: {data}")
        
        if not data:
            return error("Request body must be JSON", 400)
        
        original = data.get('original', '').strip()
        translation = data.get('translation', '').strip()
        
        print(f"[DEBUG] Extracted values: original={original[:50]}..., translation={translation[:50]}...")

        if not original:
            return error("No original text provided", 400)
        
        if not translation:
            return error("No translation provided", 400)

        system = (
            "You are an expert linguist and translator. Provide a structured, learner-friendly explanation "
            "for the given translation. Return only valid JSON with these keys: meaning, pronunciation, usage_tip, "
            "example_sentence, cultural_note."
        )
        user = (
            f"Explain this translation in a clear and concise format.\n\n"
            f"Original: {original}\n"
            f"Translation: {translation}\n\n"
            f"Return JSON only."
        )

        print("[EXPLAIN] Calling complete_json() function for explanation...")
        explanation_json = complete_json(
            system,
            user,
            default_structure={
                "meaning": "",
                "pronunciation": "",
                "usage_tip": "",
                "example_sentence": "",
                "cultural_note": "",
            },
        )
        explanation_data = json.loads(explanation_json)
        
        print(f"[EXPLAIN] Successfully generated structured explanation")
        return success(explanation_data)

    except Exception as e:
        print(f"[ERROR] Exception in explain: {str(e)}")
        import traceback
        traceback.print_exc()
        return error(f"Explanation failed: {str(e)}", 500)


from flask import Blueprint,request,jsonify
import language_tool_python

grammar_bp=Blueprint('grammar',__name__)
tool=language_tool_python.LanguageTool('en-US')

@grammar_bp.route('/grammar',methods=['POST'])
def grammar():
    text=request.json['text']
    matches=tool.check(text)
    corrected=language_tool_python.utils.correct(text,matches)
    return jsonify({'corrected':corrected})
=======
import json
from flask import Blueprint, request, g
from services.groq_service import complete_json, complete
from services.history_service import save_history_entry
from services.auth_service import track_guest_usage
from middleware.auth_middleware import optional_auth
from utils.response import success, error

grammar_bp = Blueprint('grammar', __name__)

TONE_STYLES = {
    'formal': 'very formal and official',
    'professional': 'professional and business-appropriate',
    'simple': 'simple, plain-language, and easy to understand',
    'academic': 'academic and scholarly',
    'casual': 'casual and conversational',
    'friendly': 'warm, friendly, and approachable',
}


@grammar_bp.route('/grammar', methods=['POST'])
@optional_auth
def grammar():
    """
    Fix grammar or rewrite text with specified tone.
    
    Request: { "text": "...", "mode": "grammar|tone|rewrite", "tone_style": "..." }
    Response: { "success": true, "data": { "result": "...", "changes": [...] }, "error": null }
    """
    data = request.get_json(silent=True) or {}
    text = data.get('text', '').strip()
    mode = data.get('mode', 'grammar').lower()
    tone_style = data.get('tone_style', 'professional').lower()

    if not text:
        return error('No text provided', 400)

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

    elif mode == 'rewrite':
        system = (
            "You are a skilled writer. Rewrite the given text to make it clearer, more engaging, "
            "and better structured while preserving the original meaning. "
            "Return a JSON object with two keys: "
            "'result' (the rewritten text) and "
            "'changes' (array of strings describing improvements made). Return ONLY the JSON."
        )
        user = f"Rewrite and improve this text:\n\n{text}"

    else:
        return error('Invalid mode', 400)

    try:
        raw = complete_json(system, user, default_structure={'result': '', 'changes': []})
        result = json.loads(raw)
        
        grammar_data = {
            'result': result.get('result', text),
            'changes': result.get('changes', []),
            'mode': mode,
        }

        current = getattr(g, 'current_user', None)
        if current:
            save_history_entry(
                user_id=current.get('id') if current.get('role') == 'user' else None,
                guest_session_id=current.get('guest_session_id') if current.get('role') == 'guest' else None,
                module_type='writing_assistant',
                input_text=text,
                output_text=grammar_data['result'],
                metadata=json.dumps({'mode': mode, 'tone_style': tone_style, 'changes': grammar_data['changes']}),
            )
            if current.get('role') == 'guest':
                track_guest_usage(current.get('guest_session_id'), 'writing')

        print(f"[GRAMMAR] Processed text with mode '{mode}', made {len(grammar_data['changes'])} changes")
        return success(grammar_data)
    except Exception as e:
        print(f"[ERROR] Grammar processing failed: {str(e)}")
        return error(f"Grammar processing failed: {str(e)}", 500)

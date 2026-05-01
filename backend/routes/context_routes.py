import json
from flask import Blueprint, request, g
from services.groq_service import complete
from services.history_service import save_history_entry
from services.auth_service import track_guest_usage
from middleware.auth_middleware import optional_auth
from utils.response import success, error

context_bp = Blueprint('context', __name__)

TONE_DESCRIPTIONS = {
    'formal': 'very formal, respectful, and structured — suitable for official documents or ceremonies',
    'professional': 'professional and business-appropriate — suitable for workplace communication, emails, and reports',
    'academic': 'academic and scholarly — with precise vocabulary, passive voice where appropriate, and a research paper style',
    'casual': 'casual and conversational — relaxed, friendly, and easy to read',
    'persuasive': 'persuasive and compelling — designed to convince the reader with strong arguments',
}


@context_bp.route('/context/transform', methods=['POST'])
@optional_auth
def transform():
    """
    Transform text to specified tone.
    
    Request: { "text": "...", "tone": "formal|professional|academic|casual|persuasive" }
    Response: { "success": true, "data": { "transformed": "...", "tone": "..." }, "error": null }
    """
    data = request.get_json(silent=True) or {}
    text = data.get('text', '').strip()
    tone = data.get('tone', 'professional').lower()

    if not text:
        return error('No text provided', 400)

    if tone not in TONE_DESCRIPTIONS:
        return error(f'Invalid tone. Supported: {", ".join(TONE_DESCRIPTIONS.keys())}', 400)

    tone_desc = TONE_DESCRIPTIONS.get(tone, TONE_DESCRIPTIONS['professional'])

    system = (
        f"You are an expert writing coach. Rewrite the provided text to match a {tone_desc} tone. "
        "Preserve the original meaning and key information. "
        "Only output the rewritten text — no explanations, no labels."
    )
    user = f"Rewrite this text in a {tone} tone:\n\n{text}"

    try:
        result = complete(system, user)
        
        context_data = {
            'transformed': result,
            'tone': tone,
        }

        current = getattr(g, 'current_user', None)
        if current:
            save_history_entry(
                user_id=current.get('id'),
                guest_session_id=current.get('guest_session_id'),
                module_type='context_engine',
                input_text=text,
                output_text=result,
                metadata=json.dumps({'tone': tone}),
            )
            if current.get('guest_session_id'):
                track_guest_usage(current.get('guest_session_id'), 'writing')

        return success(context_data)
    except Exception as exc:
        return error(f"Context transformation failed: {exc}", 500)

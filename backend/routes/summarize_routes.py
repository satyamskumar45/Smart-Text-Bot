import json
from flask import Blueprint, request, g
from services.groq_service import complete_json
from services.history_service import save_history_entry
from services.auth_service import track_guest_usage
from middleware.auth_middleware import optional_auth
from utils.response import success, error

summarize_bp = Blueprint('summarize', __name__)


def _read_summary_input():
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        uploaded = request.files.get('file')
        if not uploaded:
            return '', None
        raw = uploaded.read()
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            text = raw.decode('latin-1', errors='ignore')
        return text.strip(), uploaded.filename

    data = request.get_json(silent=True) or {}
    return (data.get('text') or '').strip(), None


@summarize_bp.route('/summarize', methods=['POST'])
@optional_auth
def summarize():
    """
    Summarize provided text.
    
    Request: { "text": "..." }
    Response: { "success": true, "data": { "summary": "...", "bullets": [...] }, "error": null }
    """
    text, filename = _read_summary_input()

    if not text:
        return error('No text provided', 400)

    data = request.get_json(silent=True) or {}
    mode = (request.form.get('mode') if request.form else data.get('mode', 'short')) or 'short'
    mode = mode.strip().lower()
    if mode not in {'short', 'detailed'}:
        return error("Mode must be 'short' or 'detailed'", 400)

    system = (
        "You are an expert summarizer. Return a JSON object with three keys: "
        "'paragraph' (a concise 2-3 sentence summary), "
        "'detailed_summary' (a fuller paragraph summary), and "
        "'bullets' (an array of 4-6 key bullet point strings). "
        "Return ONLY the JSON object."
    )
    user = (
        f"Summarize the following text in {mode} mode.\n"
        "Keep the paragraph concise and make detailed_summary more complete.\n\n"
        f"{text}"
    )

    try:
        raw = complete_json(
            system,
            user,
            default_structure={'paragraph': '', 'detailed_summary': '', 'bullets': []},
        )
        result = json.loads(raw)
        
        summary_data = {
            'summary': result.get('paragraph', ''),
            'detailed_summary': result.get('detailed_summary') or result.get('paragraph', ''),
            'bullets': result.get('bullets', []),
            'mode': mode,
            'document_name': filename,
        }

        current = getattr(g, 'current_user', None)
        if current:
            save_history_entry(
                user_id=current.get('id') if current.get('role') == 'user' else None,
                guest_session_id=current.get('guest_session_id') if current.get('role') == 'guest' else None,
                module_type='summary',
                input_text=text,
                output_text=summary_data['summary'],
                metadata=json.dumps({
                    'bullets': summary_data['bullets'],
                    'detailed_summary': summary_data['detailed_summary'],
                    'mode': mode,
                    'document_name': filename,
                }),
            )
            if current.get('role') == 'guest':
                track_guest_usage(current.get('guest_session_id'), 'summaries')
        
        print(f"[SUMMARIZE] Summarized text, generated {len(summary_data['bullets'])} bullet points")
        return success(summary_data)
    except Exception as e:
        print(f"[ERROR] Summarization failed: {str(e)}")
        return error(f"Summarization failed: {str(e)}", 500)

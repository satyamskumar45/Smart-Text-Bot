import json
from flask import Blueprint, request, g, current_app
from services.chatbot_service import summarize as summarize_service
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
    text, filename = _read_summary_input()

    if not text:
        return error('No text provided', 400)

    data = request.get_json(silent=True) or {}
    mode = (request.form.get('mode') if request.form else data.get('mode', 'short')) or 'short'
    try:
        result = summarize_service(text=text, mode=mode, filename=filename)

        current = getattr(g, 'current_user', None)
        if current:
            save_history_entry(
                user_id=current.get('id'),
                guest_session_id=current.get('guest_session_id'),
                module_type='summary',
                input_text=text,
                output_text=result['summary'],
                metadata=json.dumps({
                    'bullets': result.get('bullets', []),
                    'detailed_summary': result.get('detailed_summary', ''),
                    'mode': result.get('mode', 'short'),
                    'document_name': filename,
                }),
            )
            if current.get('guest_session_id'):
                track_guest_usage(current.get('guest_session_id'), 'summaries')

        return success(result)
    except ValueError as ve:
        current_app.logger.info("Summarize validation error: %s", ve)
        return error(str(ve), 400)
    except Exception as exc:
        current_app.logger.exception("Summarization failed")
        return error(f"Summarization failed: {exc}", 500)

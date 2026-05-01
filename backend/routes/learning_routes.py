from flask import Blueprint, g, request

from middleware.auth_middleware import jwt_required, optional_auth
from services.auth_service import track_guest_usage
from services.learning_service import get_learning_snapshot, record_learning_activity
from utils.response import error, success


learning_bp = Blueprint('learning', __name__)


@learning_bp.route('/learning/progress', methods=['GET'])
@jwt_required
def learning_progress():
    current = g.current_user
    snapshot = get_learning_snapshot(
        user_id=current.get('id') if current['role'] == 'user' else None,
        guest_session_id=current.get('guest_session_id') if current['role'] == 'guest' else None,
    )
    snapshot['guest_mode'] = current['role'] == 'guest'
    return success(snapshot)


@learning_bp.route('/learning/progress', methods=['POST'])
@optional_auth
def save_learning_progress():
    current = getattr(g, 'current_user', None)
    if not current:
        return error('Authentication required', 401)

    payload = request.get_json(silent=True) or {}
    activity_type = (payload.get('activity_type') or '').strip().lower()
    language = (payload.get('language') or 'en').strip().lower()
    input_text = (payload.get('input_text') or '').strip()
    output_text = (payload.get('output_text') or '').strip()
    xp_delta = int(payload.get('xp_delta') or 0)
    metadata = payload.get('metadata') or {}
    favorite = bool(payload.get('favorite', False))

    if not activity_type:
        return error('activity_type is required', 400)
    if not input_text:
        return error('input_text is required', 400)
    if not output_text:
        return error('output_text is required', 400)

    try:
        history_id, progress = record_learning_activity(
            activity_type=activity_type,
            language=language,
            input_text=input_text,
            output_text=output_text,
            user_id=current.get('id') if current.get('role') == 'user' else None,
            guest_session_id=current.get('guest_session_id') if current.get('role') == 'guest' else None,
            xp_delta=xp_delta,
            favorite=favorite,
            metadata=metadata,
        )
        if current.get('role') == 'guest':
            track_guest_usage(current.get('guest_session_id'), 'language_quest')
        return success({'history_id': history_id, 'progress': progress}, status_code=201)
    except ValueError as exc:
        return error(str(exc), 400)
    except Exception as exc:
        print(f"[LEARNING] save failed: {exc}")
        return error(f"Learning progress failed: {exc}", 500)

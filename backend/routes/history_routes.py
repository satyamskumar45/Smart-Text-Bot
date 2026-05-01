from flask import Blueprint, request, g
from services.history_service import save_history_entry, get_history, toggle_favorite
from utils.response import success, error
from middleware.auth_middleware import jwt_required

history_bp = Blueprint('history', __name__)

@history_bp.route('/history', methods=['GET'])
@jwt_required
def history_list():
    current = g.current_user
    if current['role'] == 'user':
        data = get_history(user_id=current['id'])
    else:
        data = get_history(guest_session_id=current['guest_session_id'])
    return success({'items': data})

@history_bp.route('/history/favorites', methods=['GET'])
@jwt_required
def history_favorites():
    current = g.current_user
    if current['role'] == 'user':
        data = get_history(user_id=current['id'], only_favorites=True)
    else:
        data = get_history(guest_session_id=current['guest_session_id'], only_favorites=True)
    return success({'items': data})

@history_bp.route('/history', methods=['POST'])
@jwt_required
def save_history():
    payload = request.json or {}
    module_type = payload.get('module_type')
    input_text = payload.get('input')
    output_text = payload.get('output')
    metadata = payload.get('metadata')
    status = payload.get('status', 'complete')

    current = g.current_user
    if current['role'] == 'user':
        record_id = save_history_entry(
            user_id=current['id'],
            module_type=module_type,
            input_text=input_text,
            output_text=output_text,
            metadata=metadata,
            status=status,
        )
    else:
        record_id = save_history_entry(
            guest_session_id=current['guest_session_id'],
            module_type=module_type,
            input_text=input_text,
            output_text=output_text,
            metadata=metadata,
            status=status,
        )

    return success({'record_id': record_id}, status_code=201)

@history_bp.route('/history/<history_id>/favorite', methods=['PATCH'])
@jwt_required
def favorite_history(history_id):
    payload = request.json or {}
    favorite = payload.get('favorite', True)
    current = g.current_user
    updated = toggle_favorite(
        history_id,
        favorite,
        user_id=current.get('id') if current['role'] == 'user' else None,
        guest_session_id=current.get('guest_session_id') if current['role'] == 'guest' else None,
    )
    if not updated:
        return error('History item not found', 404)
    return success({'history_id': history_id, 'favorite': favorite})

from flask import Blueprint, jsonify, g
from services.dashboard_service import build_dashboard_summary
from utils.response import success, error
from middleware.auth_middleware import jwt_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
@jwt_required
def dashboard():
    current = g.current_user
    if current.get('role') == 'user':
        data = build_dashboard_summary(user_id=current['id'])
    else:
        data = build_dashboard_summary(guest_session_id=current['guest_session_id'])

    if data is None:
        return error('Unable to load dashboard', 500)

    return success(data)

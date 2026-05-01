
from flask import Blueprint, g, jsonify, request

from models.history_model import HistoryModel
from models.progress_model import ProgressModel
from models.user_model import UserModel
from utils.auth import auth_required


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/history", methods=["GET"])
@auth_required
def get_history():
    favorites_only = request.args.get("favorites", "false").lower() == "true"
    try:
        limit = max(1, min(int(request.args.get("limit", 100)), 500))
    except ValueError:
        limit = 100
    items = HistoryModel.list_history(g.current_user_id, favorites_only=favorites_only, limit=limit)
    return jsonify({"status": "success", "items": items})


@dashboard_bp.route("/history", methods=["POST"])
@auth_required
def create_history():
    payload = request.get_json(silent=True) or {}
    item = HistoryModel.create_history(g.current_user_id, payload)
    UserModel.update_streak(g.current_user_id)
    return jsonify({"status": "success", "item": item}), 201


@dashboard_bp.route("/history/<history_id>/favorite", methods=["PATCH"])
@auth_required
def update_favorite(history_id):
    payload = request.get_json(silent=True) or {}
    is_favorite = payload.get("is_favorite", True)
    item = HistoryModel.toggle_favorite(history_id, g.current_user_id, is_favorite)
    if not item:
        return jsonify({"status": "fail", "message": "History item not found."}), 404
    return jsonify({"status": "success", "item": item})


@dashboard_bp.route("/history/<history_id>", methods=["DELETE"])
@auth_required
def delete_history(history_id):
    deleted = HistoryModel.delete_history(history_id, g.current_user_id)
    if not deleted:
        return jsonify({"status": "fail", "message": "History item not found."}), 404
    return jsonify({"status": "success"})


@dashboard_bp.route("/dashboard", methods=["GET"])
@dashboard_bp.route("/dashboard/stats", methods=["GET"])
@auth_required
def dashboard_stats():
    history_stats = HistoryModel.get_stats(g.current_user_id)
    progress_summary = ProgressModel.get_summary(g.current_user_id)
    user = UserModel.find_by_id(g.current_user_id)

    return jsonify(
        {
            "status": "success",
            "stats": {
                **history_stats,
                **progress_summary,
                "streak_count": user.get("streak_count", 0) if user else 0,
            },
        }
    )


@dashboard_bp.route("/progress", methods=["GET"])
@auth_required
def get_progress():
    items = ProgressModel.list_progress(g.current_user_id)
    summary = ProgressModel.get_summary(g.current_user_id)
    return jsonify({"status": "success", "items": items, "summary": summary})


@dashboard_bp.route("/progress", methods=["POST"])
@auth_required
def upsert_progress():
    data = request.get_json(silent=True) or {}
    module = data.get("module")
    if not module:
        return jsonify({"status": "fail", "message": "Module is required."}), 400

    try:
        completed_lessons = data.get("completed_lessons")
        total_lessons = data.get("total_lessons")
        if completed_lessons is not None:
            int(completed_lessons)
        if total_lessons is not None:
            int(total_lessons)
    except (TypeError, ValueError):
        return jsonify({"status": "fail", "message": "Progress values must be integers."}), 400

    item = ProgressModel.upsert_progress(
        user_id=g.current_user_id,
        module=module,
        completed_lessons=completed_lessons,
        total_lessons=total_lessons,
        extra=data.get("extra"),
    )
    UserModel.update_streak(g.current_user_id)
    return jsonify({"status": "success", "item": item})
=======
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

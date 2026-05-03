from datetime import datetime, timezone

from flask import Blueprint, g, request, current_app
from utils.response import success, error
from bson import ObjectId
from bson.errors import InvalidId

from database.db import get_db
from models.guest_session_model import delete_guest_sessions_for_user
from models.history_model import HistoryModel
from models.history_model import delete_history_for_user
from models.progress_model import ProgressModel
from models.refresh_token_model import delete_refresh_tokens_for_user
from models.user_model import UserModel
from utils.auth import auth_required, require_role


dashboard_bp = Blueprint("dashboard", __name__)


def _user_object_id(user_id):
    try:
        return ObjectId(user_id)
    except (InvalidId, TypeError):
        return None


def _utcnow():
    return datetime.now(timezone.utc)


@dashboard_bp.route("/history", methods=["GET"])
@auth_required
def get_history():
    favorites_only = request.args.get("favorites", "false").lower() == "true"
    try:
        limit = max(1, min(int(request.args.get("limit", 100)), 500))
    except ValueError:
        limit = 100
    try:
        items = HistoryModel.list_history(g.current_user_id, favorites_only=favorites_only, limit=limit)
        return success({"items": items})
    except Exception:
        current_app.logger.exception("Failed to list history")
        return error("Failed to fetch history", 500)


@dashboard_bp.route("/history", methods=["POST"])
@auth_required
def create_history():
    payload = request.get_json(silent=True) or {}
    try:
        item = HistoryModel.create_history(g.current_user_id, payload)
        UserModel.update_streak(g.current_user_id)
        return success({"item": item}, status_code=201)
    except Exception:
        current_app.logger.exception("Failed to create history")
        return error("Failed to create history", 500)


@dashboard_bp.route("/history/<history_id>/favorite", methods=["PATCH"])
@auth_required
def update_favorite(history_id):
    payload = request.get_json(silent=True) or {}
    is_favorite = payload.get("is_favorite", True)
    try:
        item = HistoryModel.toggle_favorite(history_id, g.current_user_id, is_favorite)
        if not item:
            return error("History item not found.", 404)
        return success({"item": item})
    except Exception:
        current_app.logger.exception("Failed to toggle favorite")
        return error("Failed to update favorite", 500)


@dashboard_bp.route("/history/<history_id>", methods=["DELETE"])
@auth_required
def delete_history(history_id):
    try:
        deleted = HistoryModel.delete_history(history_id, g.current_user_id)
        if not deleted:
            return error("History item not found.", 404)
        return success()
    except Exception:
        current_app.logger.exception("Failed to delete history")
        return error("Failed to delete history", 500)


@dashboard_bp.route("/dashboard", methods=["GET"])
@dashboard_bp.route("/dashboard/stats", methods=["GET"])
@auth_required
def dashboard_stats():
    history_stats = HistoryModel.get_stats(g.current_user_id)
    progress_summary = ProgressModel.get_summary(g.current_user_id)
    user = UserModel.find_by_id(g.current_user_id)

    try:
        return success({
            "stats": {
                **history_stats,
                **progress_summary,
                "streak_count": user.get("streak_count", 0) if user else 0,
            }
        })
    except Exception:
        current_app.logger.exception("Failed to get dashboard stats")
        return error("Failed to fetch dashboard stats", 500)


@dashboard_bp.route("/progress", methods=["GET"])
@auth_required
def get_progress():
    try:
        items = ProgressModel.list_progress(g.current_user_id)
        summary = ProgressModel.get_summary(g.current_user_id)
        return success({"items": items, "summary": summary})
    except Exception:
        current_app.logger.exception("Failed to get progress")
        return error("Failed to fetch progress", 500)


@dashboard_bp.route("/progress", methods=["POST"])
@auth_required
def upsert_progress():
    data = request.get_json(silent=True) or {}
    module = data.get("module")
    if not module:
        return error("Module is required.", 400)

    try:
        completed_lessons = data.get("completed_lessons")
        total_lessons = data.get("total_lessons")
        if completed_lessons is not None:
            int(completed_lessons)
        if total_lessons is not None:
            int(total_lessons)
    except (TypeError, ValueError):
        return error("Progress values must be integers.", 400)

    item = ProgressModel.upsert_progress(
        user_id=g.current_user_id,
        module=module,
        completed_lessons=completed_lessons,
        total_lessons=total_lessons,
        extra=data.get("extra"),
    )
    try:
        UserModel.update_streak(g.current_user_id)
        return success({"item": item})
    except Exception:
        current_app.logger.exception("Failed to upsert progress")
        return error("Failed to upsert progress", 500)


@dashboard_bp.route("/admin/stats", methods=["GET"])
@auth_required
@require_role("admin")
def admin_stats():
    mongo = get_db()
    total_users = mongo["users"].count_documents({"is_guest": {"$ne": True}})
    total_history = mongo["history"].count_documents({})
    total_active_sessions = mongo["refresh_tokens"].count_documents(
        {
            "is_revoked": False,
            "expires_at": {"$gt": _utcnow()},
        }
    )
    total_guest_sessions = mongo["guest_sessions"].count_documents({})

    try:
        return success({
            "stats": {
                "total_users": total_users,
                "total_history_entries": total_history,
                "total_active_sessions": total_active_sessions,
                "total_guest_sessions": total_guest_sessions,
            }
        })
    except Exception:
        current_app.logger.exception("Failed to fetch admin stats")
        return error("Failed to fetch admin stats", 500)


@dashboard_bp.route("/admin/users", methods=["GET"])
@auth_required
@require_role("admin")
def admin_list_users():
    mongo = get_db()
    users = list(
        mongo["users"]
        .find({"is_guest": {"$ne": True}}, {"email": 1, "role": 1, "created_at": 1, "is_guest": 1})
        .sort("created_at", -1)
    )

    items = []
    for user in users:
        items.append(
            {
                "id": str(user["_id"]),
                "email": user.get("email"),
                "role": user.get("role") or ("guest" if user.get("is_guest") else "user"),
                "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
            }
        )

    try:
        return success({"users": items})
    except Exception:
        current_app.logger.exception("Failed to list users")
        return error("Failed to list users", 500)


@dashboard_bp.route("/admin/users/<user_id>/role", methods=["PATCH"])
@auth_required
@require_role("admin")
def admin_update_user_role(user_id):
    data = request.get_json(silent=True) or {}
    next_role = (data.get("role") or "").strip().lower()

    if next_role not in {"user", "admin"}:
        return error("Role must be 'user' or 'admin'.", 400)

    mongo = get_db()
    target_user = UserModel.find_by_id(user_id)
    object_id = _user_object_id(user_id)
    if not target_user:
        return error("User not found.", 404)
    if not object_id:
        return error("Invalid user id.", 400)
    if target_user.get("is_guest"):
        return error("Guest users cannot be assigned admin roles.", 400)

    mongo["users"].update_one({"_id": object_id}, {"$set": {"role": next_role}})
    updated_user = UserModel.find_by_id(user_id)

    try:
        return success({
            "user": {
                "id": updated_user["id"],
                "email": updated_user.get("email"),
                "role": updated_user.get("role"),
                "created_at": updated_user.get("created_at"),
            }
        })
    except Exception:
        current_app.logger.exception("Failed to update user role")
        return error("Failed to update user role", 500)


@dashboard_bp.route("/admin/users/<user_id>", methods=["DELETE"])
@auth_required
@require_role("admin")
def admin_delete_user(user_id):
    if user_id == g.current_user_id:
        return error("You cannot delete your own admin account.", 400)

    mongo = get_db()
    target_user = UserModel.find_by_id(user_id)
    object_id = _user_object_id(user_id)
    if not target_user:
        return error("User not found.", 404)
    if not object_id:
        return error("Invalid user id.", 400)
    if target_user.get("is_guest"):
        return error("Guest users cannot be deleted from this view.", 400)

    delete_refresh_tokens_for_user(user_id)
    delete_history_for_user(user_id)
    delete_guest_sessions_for_user(user_id)
    mongo["progress"].delete_many({"user_id": user_id})
    mongo["learning_progress"].delete_many({"user_id": user_id})
    mongo["streak_tracking"].delete_many({"user_id": user_id})
    mongo["users"].delete_one({"_id": object_id})

    try:
        return success()
    except Exception:
        current_app.logger.exception("Failed to delete user")
        return error("Failed to delete user", 500)

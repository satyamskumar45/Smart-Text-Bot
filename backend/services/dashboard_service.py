from models.guest_session_model import get_guest_session
from models.history_model import get_history_by_user
from models.progress_model import ProgressModel
from models.user_model import UserModel


def build_dashboard_summary(user_id=None, guest_session_id=None):
    if user_id:
        history = get_history_by_user(user_id=user_id)
        total_translations = sum(1 for item in history if item["module_type"] == "translation")
        total_summaries = sum(1 for item in history if item["module_type"] == "summary")
        total_writing = sum(1 for item in history if item["module_type"] in ["writing_assistant", "context_engine"])
        learning_entries = [item for item in history if item["module_type"] == "learning_assistant"]
        favorites = [item for item in history if item["favorite"]]
        user = UserModel.find_by_id(str(user_id))
        progress_summary = ProgressModel.get_summary(str(user_id))

        return {
            "recent_activity": history[:8],
            "summary": {
                "total_translations": total_translations,
                "saved_summaries": total_summaries,
                "total_summaries": total_summaries,
                "writing_improvements": total_writing,
                "learning_sessions": len(learning_entries),
                "learning_streak": (user or {}).get("streak_count", 0),
                "best_streak": (user or {}).get("streak_count", 0),
                "xp": progress_summary.get("completed_lessons", 0),
                "level": progress_summary.get("modules_tracked", 1) or 1,
                "completed_quizzes": progress_summary.get("completed_lessons", 0),
                "vocabulary_mastered": progress_summary.get("total_lessons", 0),
                "favorites_count": len(favorites),
            },
            "favorites": favorites[:6],
            "usage_breakdown": _build_usage_breakdown(history),
            "guest_mode": False,
        }

    if guest_session_id:
        guest = get_guest_session(guest_session_id)
        if not guest:
            return None

        usage_counts = guest.get("usage_counts", {})
        recent_activity = get_history_by_user(guest_session_id=guest_session_id)[:6]
        return {
            "recent_activity": recent_activity,
            "summary": {
                "total_translations": usage_counts.get("translations", 0),
                "saved_summaries": usage_counts.get("summaries", 0),
                "total_summaries": usage_counts.get("summaries", 0),
                "writing_improvements": usage_counts.get("writing", 0),
                "learning_sessions": usage_counts.get("language_quest", 0),
                "learning_streak": 0,
                "best_streak": 0,
                "xp": 0,
                "level": 0,
                "completed_quizzes": 0,
                "vocabulary_mastered": 0,
                "favorites_count": sum(1 for item in recent_activity if item["favorite"]),
            },
            "favorites": [item for item in recent_activity if item["favorite"]][:6],
            "usage_breakdown": usage_counts,
            "guest_mode": True,
        }

    return None


def _build_usage_breakdown(history):
    breakdown = {}
    for item in history:
        module_type = item.get("module_type") or "unknown"
        breakdown[module_type] = breakdown.get(module_type, 0) + 1
    return breakdown

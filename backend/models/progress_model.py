from datetime import datetime, timezone

from database.db import get_db
from database.serializers import serialize


def _utcnow():
    return datetime.now(timezone.utc)


class ProgressModel:
    @classmethod
    def upsert_progress(cls, user_id, module, completed_lessons, total_lessons, extra=None):
        db = get_db()
        collection = db["progress"]
        now = _utcnow()
        total_lessons = max(int(total_lessons or 0), 0)
        completed_lessons = min(max(int(completed_lessons or 0), 0), total_lessons or 0)
        progress_percent = int((completed_lessons / total_lessons) * 100) if total_lessons else 0

        collection.update_one(
            {"user_id": user_id, "module": module},
            {
                "$set": {
                    "completed_lessons": completed_lessons,
                    "total_lessons": total_lessons,
                    "progress_percent": progress_percent,
                    "updated_at": now,
                    "last_activity_date": now.date().isoformat(),
                    "extra": extra or {},
                },
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
        )

        document = collection.find_one({"user_id": user_id, "module": module})
        return serialize(document)

    @classmethod
    def list_progress(cls, user_id):
        db = get_db()
        cursor = db["progress"].find({"user_id": user_id}).sort("updated_at", -1)
        return [serialize(item) for item in cursor]

    @classmethod
    def get_summary(cls, user_id):
        db = get_db()
        items = list(db["progress"].find({"user_id": user_id}))
        if not items:
            return {
                "modules_tracked": 0,
                "average_completion": 0,
                "completed_lessons": 0,
                "total_lessons": 0,
            }

        completed = sum(item.get("completed_lessons", 0) for item in items)
        total = sum(item.get("total_lessons", 0) for item in items)
        average_completion = int(sum(item.get("progress_percent", 0) for item in items) / len(items))

        return {
            "modules_tracked": len(items),
            "average_completion": average_completion,
            "completed_lessons": completed,
            "total_lessons": total,
        }

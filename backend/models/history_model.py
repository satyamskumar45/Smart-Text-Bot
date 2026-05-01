from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from database.db import get_db
from database.serializers import serialize


def _utcnow():
    return datetime.now(timezone.utc)


class HistoryModel:
    @classmethod
    def create_history(cls, user_id, payload):
        db = get_db()
        collection = db["history"]
        now = _utcnow()
        document = {
            "user_id": user_id,
            "feature": payload.get("feature", "general"),
            "input_text": payload.get("input_text") or payload.get("text") or payload.get("message"),
            "output_text": payload.get("output_text") or payload.get("response"),
            "is_favorite": bool(payload.get("is_favorite", False)),
            "metadata": payload.get("metadata", {}),
            "created_at": now,
            "updated_at": now,
        }
        result = collection.insert_one(document)
        return serialize(collection.find_one({"_id": result.inserted_id}))

    @classmethod
    def list_history(cls, user_id, favorites_only=False, limit=100):
        db = get_db()
        collection = db["history"]
        query = {"user_id": user_id}
        if favorites_only:
            query["is_favorite"] = True

        cursor = collection.find(query).sort("created_at", -1).limit(limit)
        return [serialize(item) for item in cursor]

    @classmethod
    def toggle_favorite(cls, history_id, user_id, is_favorite):
        db = get_db()
        collection = db["history"]
        object_id = _safe_object_id(history_id)
        if not object_id:
            return None

        collection.update_one(
            {"_id": object_id, "user_id": user_id},
            {"$set": {"is_favorite": bool(is_favorite), "updated_at": _utcnow()}},
        )
        history = collection.find_one({"_id": object_id, "user_id": user_id})
        return serialize(history)

    @classmethod
    def delete_history(cls, history_id, user_id):
        db = get_db()
        collection = db["history"]
        object_id = _safe_object_id(history_id)
        if not object_id:
            return False

        result = collection.delete_one({"_id": object_id, "user_id": user_id})
        return result.deleted_count > 0

    @classmethod
    def get_stats(cls, user_id):
        db = get_db()
        collection = db["history"]
        items = list(collection.find({"user_id": user_id}))
        feature_usage = {}
        favorite_count = 0
        for item in items:
            feature = item.get("feature", "general")
            feature_usage[feature] = feature_usage.get(feature, 0) + 1
            if item.get("is_favorite"):
                favorite_count += 1

        return {
            "history_count": len(items),
            "favorite_count": favorite_count,
            "feature_usage": feature_usage,
        }


def _safe_object_id(value):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None

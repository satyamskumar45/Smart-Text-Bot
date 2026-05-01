<<<<<<< HEAD
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
=======
from datetime import datetime
import json
from database.db import get_db


def create_history_entry(user_id=None, guest_session_id=None, module_type=None, input_text=None, output_text=None, metadata=None, status='complete', favorite=False):
    if not (user_id or guest_session_id):
        raise ValueError('user_id or guest_session_id is required')

    if not module_type:
        raise ValueError('module_type is required')

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO history (user_id, guest_session_id, module_type, input_text, output_text, metadata, favorite, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            user_id,
            guest_session_id,
            module_type,
            input_text,
            output_text,
            metadata or '{}',
            int(favorite),
            status,
            datetime.utcnow(),
            datetime.utcnow(),
        ),
    )
    history_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return history_id


def get_history_by_user(user_id=None, guest_session_id=None, module_type=None, only_favorites=False):
    if not (user_id or guest_session_id):
        return []

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    query = "SELECT id, user_id, guest_session_id, module_type, input_text, output_text, metadata, favorite, status, created_at FROM history WHERE "
    conditions = []
    params = []

    if user_id:
        conditions.append("user_id = %s")
        params.append(user_id)
    else:
        conditions.append("guest_session_id = %s")
        params.append(guest_session_id)

    if module_type:
        conditions.append("module_type = %s")
        params.append(module_type)

    if only_favorites:
        conditions.append("favorite = 1")

    query += " AND ".join(conditions)
    query += " ORDER BY created_at DESC LIMIT 200"

    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    for row in rows:
        try:
            row['metadata'] = json.loads(row.get('metadata') or '{}')
        except Exception:
            row['metadata'] = {}
    return rows


def get_history_entry_owned(history_id, user_id=None, guest_session_id=None):
    if not (user_id or guest_session_id):
        return None

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    if user_id:
        cur.execute("SELECT id FROM history WHERE id = %s AND user_id = %s LIMIT 1", (history_id, user_id))
    else:
        cur.execute("SELECT id FROM history WHERE id = %s AND guest_session_id = %s LIMIT 1", (history_id, guest_session_id))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def set_history_favorite(history_id, favorite=True, user_id=None, guest_session_id=None):
    if not get_history_entry_owned(history_id, user_id=user_id, guest_session_id=guest_session_id):
        return False

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE history SET favorite = %s, updated_at = %s WHERE id = %s", (int(favorite), datetime.utcnow(), history_id))
    conn.commit()
    cur.close()
    conn.close()
    return True


def attach_guest_history_to_user(guest_session_id, user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE history SET user_id = %s, guest_session_id = NULL WHERE guest_session_id = %s",
        (user_id, guest_session_id),
    )
    conn.commit()
    cur.close()
    conn.close()
    return True
>>>>>>> 7a39e76952f1835cf7031449b83138e654424a73

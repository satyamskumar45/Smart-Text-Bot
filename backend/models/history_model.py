import json
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
        history_id = create_history_entry(
            user_id=user_id,
            guest_session_id=payload.get("guest_session_id"),
            module_type=payload.get("module_type") or payload.get("feature", "general"),
            input_text=payload.get("input_text") or payload.get("text") or payload.get("message") or payload.get("input"),
            output_text=payload.get("output_text") or payload.get("response") or payload.get("output"),
            metadata=payload.get("metadata"),
            status=payload.get("status", "complete"),
            favorite=payload.get("is_favorite", payload.get("favorite", False)),
        )
        return _serialize_history_document(_find_owned_history(history_id, user_id=user_id))

    @classmethod
    def list_history(cls, user_id, favorites_only=False, limit=100):
        return get_history_by_user(user_id=user_id, only_favorites=favorites_only, limit=limit)

    @classmethod
    def toggle_favorite(cls, history_id, user_id, is_favorite):
        updated = set_history_favorite(history_id, is_favorite, user_id=user_id)
        if not updated:
            return None
        return _serialize_history_document(_find_owned_history(history_id, user_id=user_id))

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
        items = get_history_by_user(user_id=user_id, limit=1000)
        feature_usage = {}
        favorite_count = 0
        for item in items:
            feature = item.get("feature") or item.get("module_type") or "general"
            feature_usage[feature] = feature_usage.get(feature, 0) + 1
            if item.get("is_favorite") or item.get("favorite"):
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


def _coerce_metadata(metadata):
    if isinstance(metadata, dict):
        return metadata
    if isinstance(metadata, str) and metadata.strip():
        try:
            return json.loads(metadata)
        except json.JSONDecodeError:
            return {"raw": metadata}
    return {}


def _serialize_history_document(document):
    if not document:
        return None

    item = serialize(document)
    metadata = _coerce_metadata(item.get("metadata"))
    item["metadata"] = metadata

    feature = item.get("feature") or item.get("module_type") or "general"
    item["feature"] = feature
    item["module_type"] = item.get("module_type") or feature
    item["input_text"] = item.get("input_text") or ""
    item["output_text"] = item.get("output_text") or ""
    item["input"] = item["input_text"]
    item["output"] = item["output_text"]
    item["favorite"] = bool(item.get("favorite", item.get("is_favorite", False)))
    item["is_favorite"] = item["favorite"]
    item["status"] = item.get("status", "complete")
    return item


def _history_query(user_id=None, guest_session_id=None, module_type=None, only_favorites=False):
    query = {}
    if user_id:
        query["user_id"] = user_id
    elif guest_session_id:
        query["guest_session_id"] = guest_session_id

    if module_type:
        query["module_type"] = module_type

    if only_favorites:
        query["$or"] = [{"favorite": True}, {"is_favorite": True}]

    return query


def _find_owned_history(history_id, user_id=None, guest_session_id=None):
    db = get_db()
    object_id = _safe_object_id(history_id)
    if not object_id:
        return None

    query = {"_id": object_id}
    if user_id:
        query["user_id"] = user_id
    elif guest_session_id:
        query["guest_session_id"] = guest_session_id

    return db["history"].find_one(query)


def create_history_entry(
    user_id=None,
    guest_session_id=None,
    module_type=None,
    input_text=None,
    output_text=None,
    metadata=None,
    status="complete",
    favorite=False,
):
    db = get_db()
    collection = db["history"]
    now = _utcnow()
    metadata_dict = _coerce_metadata(metadata)
    feature = module_type or metadata_dict.get("feature") or "general"
    document = {
        "user_id": user_id,
        "guest_session_id": guest_session_id,
        "feature": feature,
        "module_type": feature,
        "input_text": input_text or "",
        "output_text": output_text or "",
        "metadata": metadata_dict,
        "status": status,
        "favorite": bool(favorite),
        "is_favorite": bool(favorite),
        "created_at": now,
        "updated_at": now,
    }
    result = collection.insert_one(document)
    return str(result.inserted_id)


def get_history_by_user(user_id=None, guest_session_id=None, module_type=None, only_favorites=False, limit=200):
    db = get_db()
    query = _history_query(
        user_id=user_id,
        guest_session_id=guest_session_id,
        module_type=module_type,
        only_favorites=only_favorites,
    )
    cursor = db["history"].find(query).sort("created_at", -1).limit(limit)
    return [_serialize_history_document(item) for item in cursor]


def get_history_entry_owned(history_id, user_id=None, guest_session_id=None):
    history = _find_owned_history(history_id, user_id=user_id, guest_session_id=guest_session_id)
    if not history:
        return None
    return {"id": str(history["_id"])}


def set_history_favorite(history_id, favorite=True, user_id=None, guest_session_id=None):
    db = get_db()
    object_id = _safe_object_id(history_id)
    if not object_id:
        return False

    query = {"_id": object_id}
    if user_id:
        query["user_id"] = user_id
    elif guest_session_id:
        query["guest_session_id"] = guest_session_id
    else:
        return False

    result = db["history"].update_one(
        query,
        {
            "$set": {
                "favorite": bool(favorite),
                "is_favorite": bool(favorite),
                "updated_at": _utcnow(),
            }
        },
    )
    return result.matched_count > 0


def attach_guest_history_to_user(guest_session_id, user_id):
    db = get_db()
    db["history"].update_many(
        {"guest_session_id": guest_session_id},
        {
            "$set": {"user_id": user_id, "updated_at": _utcnow()},
            "$unset": {"guest_session_id": ""},
        },
    )
    return True


def delete_history_for_user(user_id):
    db = get_db()
    result = db["history"].delete_many({"user_id": user_id})
    return result.deleted_count

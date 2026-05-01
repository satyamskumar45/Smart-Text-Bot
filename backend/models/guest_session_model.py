from datetime import datetime, timezone
from uuid import uuid4

from database.db import get_db
from database.serializers import serialize


def _utcnow():
    return datetime.now(timezone.utc)


class GuestSessionModel:
    @classmethod
    def create_session(cls, metadata=None):
        db = get_db()
        collection = db["guest_sessions"]
        now = _utcnow()
        document = {
            "session_id": str(uuid4()),
            "metadata": metadata or {},
            "usage_counts": {},
            "is_active": True,
            "created_at": now,
            "last_active_at": now,
        }
        result = collection.insert_one(document)
        return serialize(collection.find_one({"_id": result.inserted_id}))

    @classmethod
    def find_by_session_id(cls, session_id):
        db = get_db()
        document = db["guest_sessions"].find_one({"session_id": session_id})
        if not document:
            return None
        document.setdefault("usage_counts", {})
        document.setdefault("is_active", True)
        return serialize(document)

    @classmethod
    def touch_session(cls, session_id):
        db = get_db()
        db["guest_sessions"].update_one(
            {"session_id": session_id},
            {"$set": {"last_active_at": _utcnow()}},
        )
        return cls.find_by_session_id(session_id)

    @classmethod
    def delete_session(cls, session_id):
        db = get_db()
        result = db["guest_sessions"].delete_one({"session_id": session_id})
        return result.deleted_count > 0


def create_guest_session(metadata=None):
    session = GuestSessionModel.create_session(metadata=metadata)
    return session["session_id"]


def get_guest_session(session_id):
    return GuestSessionModel.find_by_session_id(session_id)


def update_guest_usage(session_id, module_type):
    db = get_db()
    now = _utcnow()
    db["guest_sessions"].update_one(
        {"session_id": session_id},
        {
            "$inc": {f"usage_counts.{module_type}": 1},
            "$set": {"last_active_at": now},
        },
    )
    return get_guest_session(session_id)


def deactivate_guest_session(session_id):
    db = get_db()
    db["guest_sessions"].update_one(
        {"session_id": session_id},
        {"$set": {"is_active": False, "last_active_at": _utcnow()}},
    )
    return True


def attach_guest_history_to_user(guest_session_id, user_id):
    db = get_db()
    db["history"].update_many(
        {"guest_session_id": guest_session_id},
        {
            "$set": {
                "user_id": user_id,
                "updated_at": _utcnow(),
            },
            "$unset": {"guest_session_id": ""},
        },
    )
    return True


def convert_guest_to_user(session_id, user_id):
    db = get_db()
    db["guest_sessions"].update_one(
        {"session_id": session_id},
        {
            "$set": {
                "linked_user_id": user_id,
                "is_active": False,
                "last_active_at": _utcnow(),
            }
        },
    )
    attach_guest_history_to_user(session_id, user_id)
    return True


def delete_guest_sessions_for_user(user_id):
    db = get_db()
    result = db["guest_sessions"].delete_many({"linked_user_id": user_id})
    return result.deleted_count

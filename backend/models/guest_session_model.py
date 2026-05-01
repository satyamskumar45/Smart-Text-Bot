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
            "created_at": now,
            "last_active_at": now,
        }
        result = collection.insert_one(document)
        return serialize(collection.find_one({"_id": result.inserted_id}))

    @classmethod
    def find_by_session_id(cls, session_id):
        db = get_db()
        return serialize(db["guest_sessions"].find_one({"session_id": session_id}))

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

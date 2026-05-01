<<<<<<< HEAD
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
=======
from datetime import datetime, timedelta
import uuid
import json
from database.db import get_db


def create_guest_session():
    session_id = uuid.uuid4().hex
    now = datetime.utcnow()
    expires_at = now + timedelta(hours=24)
    usage_counts = json.dumps({
        'translations': 0,
        'summaries': 0,
        'grammar': 0,
        'writing': 0,
        'language_quest': 0,
        'sentiment': 0,
        'pipeline': 0,
    })

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO guest_sessions (session_id, usage_counts, created_at, expires_at, is_active) VALUES (%s, %s, %s, %s, TRUE)",
        (session_id, usage_counts, now, expires_at),
    )
    conn.commit()
    cur.close()
    conn.close()
    return session_id


def get_guest_session(session_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id, session_id, usage_counts, converted_to_user_id, created_at, expires_at, is_active, last_used_at FROM guest_sessions WHERE session_id = %s AND is_active = TRUE", (session_id,))
    session = cur.fetchone()
    cur.close()
    conn.close()
    if not session:
        return None
    try:
        session['usage_counts'] = json.loads(session['usage_counts'] or '{}')
    except Exception:
        session['usage_counts'] = {}
    return session


def update_guest_usage(session_id, module_type):
    guest = get_guest_session(session_id)
    if not guest:
        return False

    usage_counts = guest['usage_counts']
    usage_counts[module_type] = usage_counts.get(module_type, 0) + 1
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE guest_sessions SET usage_counts = %s, last_used_at = %s WHERE session_id = %s",
        (json.dumps(usage_counts), datetime.utcnow(), session_id),
    )
    conn.commit()
    cur.close()
    conn.close()
    return usage_counts


def convert_guest_to_user(session_id, user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE guest_sessions SET converted_to_user_id = %s, is_active = FALSE WHERE session_id = %s",
        (user_id, session_id),
    )
    conn.commit()
    attach_guest_history_to_user(session_id, user_id)
    cur.close()
    conn.close()
    return True


def deactivate_guest_session(session_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE guest_sessions SET is_active = FALSE WHERE session_id = %s", (session_id,))
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

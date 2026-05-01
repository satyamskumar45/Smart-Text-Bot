from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError

from database.db import get_db
from database.serializers import serialize


def _utcnow():
    return datetime.now(timezone.utc)


class UserModel:
    @classmethod
    def create_user(cls, email, password_hash, name=None, is_guest=False, guest_session_id=None):
        db = get_db()
        collection = db["users"]
        now = _utcnow()
        document = {
            "email": email.lower() if email else None,
            "password": password_hash,
            "name": name,
            "is_guest": is_guest,
            "guest_session_id": guest_session_id,
            "created_at": now,
            "updated_at": now,
            "last_login_at": None,
            "streak_count": 0,
            "streak_last_date": None,
        }
        try:
            result = collection.insert_one(document)
        except DuplicateKeyError:
            return None

        created = collection.find_one({"_id": result.inserted_id})
        created.pop("password", None)
        return serialize(created)

    @classmethod
    def find_by_email(cls, email, include_password=False):
        db = get_db()
        collection = db["users"]
        if not email:
            return None
        user = collection.find_one({"email": email.lower()})
        if not user:
            return None
        if include_password:
            return user
        user.pop("password", None)
        return serialize(user)

    @classmethod
    def find_by_id(cls, user_id, include_password=False):
        db = get_db()
        collection = db["users"]
        user = collection.find_one({"_id": _safe_object_id(user_id)}) if _looks_like_object_id(user_id) else None
        if not user:
            user = collection.find_one({"guest_session_id": user_id})
        if not user:
            return None
        if include_password:
            return user
        user.pop("password", None)
        return serialize(user)

    @classmethod
    def touch_login(cls, user_id):
        db = get_db()
        collection = db["users"]
        now = _utcnow()
        collection.update_one(
            {"_id": _safe_object_id(user_id)},
            {"$set": {"last_login_at": now, "updated_at": now}},
        )

    @classmethod
    def update_streak(cls, user_id):
        db = get_db()
        collection = db["users"]
        now = _utcnow()
        today = now.date().isoformat()
        user = collection.find_one({"_id": _safe_object_id(user_id)})
        if not user:
            return None

        previous = user.get("streak_last_date")
        streak_count = user.get("streak_count", 0)

        if previous == today:
            pass
        else:
            if previous:
                previous_date = datetime.fromisoformat(previous).date()
                delta_days = (now.date() - previous_date).days
                streak_count = streak_count + 1 if delta_days == 1 else 1
            else:
                streak_count = 1

            collection.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "streak_count": streak_count,
                        "streak_last_date": today,
                        "updated_at": now,
                    }
                },
            )

        updated = collection.find_one({"_id": user["_id"]})
        updated.pop("password", None)
        return serialize(updated)


def _looks_like_object_id(value):
    return isinstance(value, str) and len(value) == 24


def _safe_object_id(value):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None
=======
from datetime import datetime
from database.db import get_db


def get_user_by_email(email):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, email, password_hash, display_name, role, is_active, created_at, updated_at FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, email, display_name, role, is_active, created_at, updated_at FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


def create_user(email, password_hash, display_name=None):
    now = datetime.utcnow()
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (email, password_hash, display_name, role, is_active, created_at, updated_at) VALUES (%s, %s, %s, 'user', TRUE, %s, %s)",
        (email, password_hash, display_name or '', now, now),
    )
    user_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return user_id


def update_user_last_active(user_id):
    now = datetime.utcnow()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET updated_at = %s WHERE id = %s", (now, user_id))
    conn.commit()
    cur.close()
    conn.close()
    return True
>>>>>>> 7a39e76952f1835cf7031449b83138e654424a73

from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError

from database.db import get_db
from database.serializers import serialize


def _utcnow():
    return datetime.now(timezone.utc)


def _normalize_user_role(user):
    if not user:
        return None
    user["role"] = user.get("role") or ("guest" if user.get("is_guest") else "user")
    return user


class UserModel:
    @classmethod
    def create_user(cls, email, password_hash, name=None, is_guest=False, guest_session_id=None, role=None):
        db = get_db()
        collection = db["users"]
        now = _utcnow()
        normalized_role = "guest" if is_guest else (role or "user")
        document = {
            "email": email.lower() if email else None,
            "password": password_hash,
            "name": name,
            "role": normalized_role,
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
        return _normalize_user_role(serialize(created))

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
            return _normalize_user_role(user)
        user.pop("password", None)
        return _normalize_user_role(serialize(user))

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
            return _normalize_user_role(user)
        user.pop("password", None)
        return _normalize_user_role(serialize(user))

    @classmethod
    def touch_login(cls, user_id):
        db = get_db()
        collection = db["users"]
        now = _utcnow()
        object_id = _safe_object_id(user_id)
        if not object_id:
            return
        collection.update_one(
            {"_id": object_id},
            {"$set": {"last_login_at": now, "updated_at": now}},
        )

    @classmethod
    def update_streak(cls, user_id):
        db = get_db()
        collection = db["users"]
        now = _utcnow()
        today = now.date().isoformat()
        object_id = _safe_object_id(user_id)
        if not object_id:
            return None

        user = collection.find_one({"_id": object_id})
        if not user:
            return None

        previous = user.get("streak_last_date")
        streak_count = user.get("streak_count", 0)

        if previous != today:
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
        return _normalize_user_role(serialize(updated))


def _looks_like_object_id(value):
    return isinstance(value, str) and len(value) == 24


def _safe_object_id(value):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


def _legacy_user_payload(user):
    if not user:
        return None
    role = user.get("role") or ("guest" if user.get("is_guest") else "user")
    return {
        "id": user["id"],
        "email": user.get("email"),
        "password_hash": user.get("password"),
        "display_name": user.get("name") or "",
        "role": role,
        "is_active": True,
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at"),
    }


def get_user_by_email(email):
    return _legacy_user_payload(UserModel.find_by_email(email, include_password=True))


def get_user_by_id(user_id):
    return _legacy_user_payload(UserModel.find_by_id(str(user_id), include_password=True))


def create_user(email, password_hash, display_name=None):
    user = UserModel.create_user(email=email, password_hash=password_hash, name=display_name, role="user")
    return user["id"] if user else None


def update_user_last_active(user_id):
    UserModel.touch_login(str(user_id))
    return True

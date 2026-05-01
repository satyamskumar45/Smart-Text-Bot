from datetime import datetime, timezone

from database.db import get_db
from database.serializers import serialize


def _utcnow():
    return datetime.now(timezone.utc)


class RefreshTokenModel:
    @classmethod
    def create_token(cls, user_id, token, expires_at):
        db = get_db()
        collection = db["refresh_tokens"]
        now = _utcnow()
        document = {
            "user_id": user_id,
            "token": token,
            "expires_at": expires_at,
            "created_at": now,
            "updated_at": now,
            "is_revoked": False,
        }
        result = collection.insert_one(document)
        return serialize(collection.find_one({"_id": result.inserted_id}))

    @classmethod
    def find_token(cls, token):
        db = get_db()
        return db["refresh_tokens"].find_one({"token": token})

    @classmethod
    def revoke_token(cls, token):
        db = get_db()
        now = _utcnow()
        db["refresh_tokens"].update_one(
            {"token": token},
            {"$set": {"is_revoked": True, "updated_at": now, "revoked_at": now}},
        )

    @classmethod
    def delete_token(cls, token):
        db = get_db()
        result = db["refresh_tokens"].delete_one({"token": token})
        return result.deleted_count > 0


def store_refresh_token(user_id, token, expires_at, user_agent=None, ip_address=None):
    db = get_db()
    collection = db["refresh_tokens"]
    now = _utcnow()
    collection.insert_one(
        {
            "user_id": user_id,
            "token": token,
            "expires_at": expires_at,
            "user_agent": user_agent or "",
            "ip_address": ip_address or "",
            "created_at": now,
            "updated_at": now,
            "is_revoked": False,
        }
    )
    return True


def find_refresh_token(token):
    record = RefreshTokenModel.find_token(token)
    if not record:
        return None
    return {
        "id": str(record["_id"]),
        "user_id": record.get("user_id"),
        "expires_at": record.get("expires_at"),
        "revoked": bool(record.get("is_revoked")),
    }


def revoke_refresh_token(token):
    RefreshTokenModel.revoke_token(token)
    return True


def revoke_refresh_tokens_for_user(user_id):
    db = get_db()
    db["refresh_tokens"].update_many(
        {"user_id": user_id},
        {"$set": {"is_revoked": True, "updated_at": _utcnow()}},
    )
    return True


def purge_expired_tokens():
    db = get_db()
    result = db["refresh_tokens"].delete_many({"expires_at": {"$lt": _utcnow()}})
    return result.deleted_count

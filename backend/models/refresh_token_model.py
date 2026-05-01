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

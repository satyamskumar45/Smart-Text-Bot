
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
=======
import hashlib
from datetime import datetime
from database.db import get_db


def _hash_token(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def store_refresh_token(user_id, token, expires_at, user_agent=None, ip_address=None):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO refresh_tokens (user_id, token_hash, expires_at, user_agent, ip_address, revoked, created_at) VALUES (%s, %s, %s, %s, %s, FALSE, %s)",
        (user_id, _hash_token(token), expires_at, user_agent or '', ip_address or '', datetime.utcnow()),
    )
    conn.commit()
    cur.close()
    conn.close()
    return True


def find_refresh_token(token):
    token_hash = _hash_token(token)
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id, user_id, expires_at, revoked FROM refresh_tokens WHERE token_hash = %s LIMIT 1",
        (token_hash,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def revoke_refresh_token(token):
    token_hash = _hash_token(token)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE refresh_tokens SET revoked = TRUE, revoked_at = %s WHERE token_hash = %s", (datetime.utcnow(), token_hash))
    conn.commit()
    cur.close()
    conn.close()
    return True


def revoke_refresh_tokens_for_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE refresh_tokens SET revoked = TRUE, revoked_at = %s WHERE user_id = %s", (datetime.utcnow(), user_id))
    conn.commit()
    cur.close()
    conn.close()
    return True


def purge_expired_tokens():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM refresh_tokens WHERE expires_at < %s", (datetime.utcnow(),))
    conn.commit()
    cur.close()
    conn.close()
    return True
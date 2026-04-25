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

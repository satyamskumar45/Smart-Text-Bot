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

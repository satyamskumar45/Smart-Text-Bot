from datetime import datetime
import json
from database.db import get_db


def create_history_entry(user_id=None, guest_session_id=None, module_type=None, input_text=None, output_text=None, metadata=None, status='complete', favorite=False):
    if not (user_id or guest_session_id):
        raise ValueError('user_id or guest_session_id is required')

    if not module_type:
        raise ValueError('module_type is required')

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO history (user_id, guest_session_id, module_type, input_text, output_text, metadata, favorite, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            user_id,
            guest_session_id,
            module_type,
            input_text,
            output_text,
            metadata or '{}',
            int(favorite),
            status,
            datetime.utcnow(),
            datetime.utcnow(),
        ),
    )
    history_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return history_id


def get_history_by_user(user_id=None, guest_session_id=None, module_type=None, only_favorites=False):
    if not (user_id or guest_session_id):
        return []

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    query = "SELECT id, user_id, guest_session_id, module_type, input_text, output_text, metadata, favorite, status, created_at FROM history WHERE "
    conditions = []
    params = []

    if user_id:
        conditions.append("user_id = %s")
        params.append(user_id)
    else:
        conditions.append("guest_session_id = %s")
        params.append(guest_session_id)

    if module_type:
        conditions.append("module_type = %s")
        params.append(module_type)

    if only_favorites:
        conditions.append("favorite = 1")

    query += " AND ".join(conditions)
    query += " ORDER BY created_at DESC LIMIT 200"

    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    for row in rows:
        try:
            row['metadata'] = json.loads(row.get('metadata') or '{}')
        except Exception:
            row['metadata'] = {}
    return rows


def get_history_entry_owned(history_id, user_id=None, guest_session_id=None):
    if not (user_id or guest_session_id):
        return None

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    if user_id:
        cur.execute("SELECT id FROM history WHERE id = %s AND user_id = %s LIMIT 1", (history_id, user_id))
    else:
        cur.execute("SELECT id FROM history WHERE id = %s AND guest_session_id = %s LIMIT 1", (history_id, guest_session_id))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def set_history_favorite(history_id, favorite=True, user_id=None, guest_session_id=None):
    if not get_history_entry_owned(history_id, user_id=user_id, guest_session_id=guest_session_id):
        return False

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE history SET favorite = %s, updated_at = %s WHERE id = %s", (int(favorite), datetime.utcnow(), history_id))
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

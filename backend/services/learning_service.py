from datetime import datetime, timedelta
import json

from database.db import get_db
from models.history_model import get_history_by_user
from services.history_service import save_history_entry


VALID_ACTIVITY_TYPES = {'vocabulary', 'quiz', 'practice', 'phrase'}
LEVEL_THRESHOLDS = [0, 100, 250, 500, 900, 1400]


def get_learning_snapshot(user_id=None, guest_session_id=None):
    history = get_history_by_user(
        user_id=user_id,
        guest_session_id=guest_session_id,
        module_type='learning_assistant',
    )
    snapshot = {
        'xp': 0,
        'level': 1,
        'completed_quizzes': 0,
        'vocabulary_count': 0,
        'current_streak': 0,
        'best_streak': 0,
        'last_activity_date': None,
        'recent_activity': history[:12],
        'per_language': {},
    }

    if user_id:
        snapshot.update(_load_learning_progress(user_id))
        snapshot.update(_load_streak(user_id))

    for item in history:
        metadata = item.get('metadata') or {}
        language = metadata.get('language', 'general')
        per_language = snapshot['per_language'].setdefault(language, {
            'quiz_completed': 0,
            'vocabulary_mastered': 0,
            'practice_sessions': 0,
            'phrases_saved': 0,
        })
        activity_type = metadata.get('activity_type')
        if activity_type == 'quiz':
            per_language['quiz_completed'] += 1
        elif activity_type == 'vocabulary':
            per_language['vocabulary_mastered'] += 1
        elif activity_type == 'practice':
            per_language['practice_sessions'] += 1
        elif activity_type == 'phrase':
            per_language['phrases_saved'] += 1

    return snapshot


def record_learning_activity(
    *,
    activity_type,
    language,
    input_text,
    output_text,
    user_id=None,
    guest_session_id=None,
    xp_delta=0,
    favorite=False,
    metadata=None,
):
    if activity_type not in VALID_ACTIVITY_TYPES:
        raise ValueError(f"Invalid activity_type: {activity_type}")

    payload = {
        'activity_type': activity_type,
        'language': language,
        **(metadata or {}),
    }

    history_id = save_history_entry(
        user_id=user_id,
        guest_session_id=guest_session_id,
        module_type='learning_assistant',
        input_text=input_text,
        output_text=output_text,
        metadata=json.dumps(payload),
        favorite=favorite,
    )

    progress = None
    if user_id:
        progress = _apply_progress_update(user_id, activity_type, int(xp_delta or 0))

    return history_id, progress


def _apply_progress_update(user_id, activity_type, xp_delta):
    progress = _load_learning_progress(user_id)
    progress['xp'] = int(progress.get('xp') or 0) + xp_delta
    progress['level'] = _level_for_xp(progress['xp'])
    if activity_type == 'quiz':
        progress['completed_quizzes'] = int(progress.get('completed_quizzes') or 0) + 1
    if activity_type == 'vocabulary':
        progress['vocabulary_count'] = int(progress.get('vocabulary_count') or 0) + 1

    _save_learning_progress(user_id, progress)
    streak = _advance_streak(user_id)

    return {
        'xp': progress['xp'],
        'level': progress['level'],
        'completed_quizzes': progress['completed_quizzes'],
        'vocabulary_count': progress['vocabulary_count'],
        'current_streak': streak['current_streak'],
        'best_streak': streak['best_streak'],
        'last_activity_date': streak['last_activity_date'],
    }


def _level_for_xp(xp):
    level = 1
    for index, threshold in enumerate(LEVEL_THRESHOLDS, start=1):
        if xp >= threshold:
            level = index
    return level


def _load_learning_progress(user_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id, level, xp, completed_quizzes, vocabulary_count FROM learning_progress WHERE user_id = %s ORDER BY updated_at DESC LIMIT 1",
        (user_id,),
    )
    row = cur.fetchone() or {}
    cur.close()
    conn.close()
    return {
        'id': row.get('id'),
        'xp': row.get('xp', 0) or 0,
        'level': row.get('level', 1) or 1,
        'completed_quizzes': row.get('completed_quizzes', 0) or 0,
        'vocabulary_count': row.get('vocabulary_count', 0) or 0,
    }


def _save_learning_progress(user_id, progress):
    now = datetime.utcnow()
    conn = get_db()
    cur = conn.cursor()
    if progress.get('id'):
        cur.execute(
            "UPDATE learning_progress SET level = %s, xp = %s, completed_quizzes = %s, vocabulary_count = %s, updated_at = %s WHERE id = %s",
            (
                progress['level'],
                progress['xp'],
                progress['completed_quizzes'],
                progress['vocabulary_count'],
                now,
                progress['id'],
            ),
        )
    else:
        cur.execute(
            "INSERT INTO learning_progress (user_id, level, xp, completed_quizzes, vocabulary_count, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                user_id,
                progress['level'],
                progress['xp'],
                progress['completed_quizzes'],
                progress['vocabulary_count'],
                now,
            ),
        )
    conn.commit()
    cur.close()
    conn.close()


def _load_streak(user_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id, current_streak, best_streak, last_activity_date FROM streak_tracking WHERE user_id = %s ORDER BY updated_at DESC LIMIT 1",
        (user_id,),
    )
    row = cur.fetchone() or {}
    cur.close()
    conn.close()
    return {
        'id': row.get('id'),
        'current_streak': row.get('current_streak', 0) or 0,
        'best_streak': row.get('best_streak', 0) or 0,
        'last_activity_date': row.get('last_activity_date'),
    }


def _advance_streak(user_id):
    streak = _load_streak(user_id)
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    last_activity = streak.get('last_activity_date')

    if last_activity == today:
        return {
            'current_streak': streak['current_streak'],
            'best_streak': streak['best_streak'],
            'last_activity_date': last_activity,
        }

    if last_activity == yesterday:
        current_streak = int(streak.get('current_streak') or 0) + 1
    else:
        current_streak = 1

    best_streak = max(current_streak, int(streak.get('best_streak') or 0))
    now = datetime.utcnow()
    conn = get_db()
    cur = conn.cursor()
    if streak.get('id'):
        cur.execute(
            "UPDATE streak_tracking SET current_streak = %s, best_streak = %s, last_activity_date = %s, updated_at = %s WHERE id = %s",
            (current_streak, best_streak, today, now, streak['id']),
        )
    else:
        cur.execute(
            "INSERT INTO streak_tracking (user_id, current_streak, best_streak, last_activity_date, updated_at) VALUES (%s, %s, %s, %s, %s)",
            (user_id, current_streak, best_streak, today, now),
        )
    conn.commit()
    cur.close()
    conn.close()
    return {
        'current_streak': current_streak,
        'best_streak': best_streak,
        'last_activity_date': today,
    }

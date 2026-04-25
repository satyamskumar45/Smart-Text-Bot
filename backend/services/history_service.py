from models.history_model import create_history_entry, get_history_by_user, set_history_favorite


def save_history_entry(user_id=None, guest_session_id=None, module_type=None, input_text=None, output_text=None, metadata=None, status='complete', favorite=False):
    return create_history_entry(
        user_id=user_id,
        guest_session_id=guest_session_id,
        module_type=module_type,
        input_text=input_text,
        output_text=output_text,
        metadata=metadata,
        status=status,
        favorite=favorite,
    )


def get_history(user_id=None, guest_session_id=None, module_type=None, only_favorites=False):
    return get_history_by_user(
        user_id=user_id,
        guest_session_id=guest_session_id,
        module_type=module_type,
        only_favorites=only_favorites,
    )


def toggle_favorite(history_id, favorite=True, user_id=None, guest_session_id=None):
    return set_history_favorite(
        history_id,
        favorite,
        user_id=user_id,
        guest_session_id=guest_session_id,
    )

import secrets
from datetime import datetime, timedelta
from config.settings import Settings
from models.user_model import create_user, get_user_by_email, get_user_by_id, update_user_last_active
from models.guest_session_model import create_guest_session, convert_guest_to_user, update_guest_usage
from models.refresh_token_model import store_refresh_token, find_refresh_token, revoke_refresh_token
from utils.password_helper import hash_password, check_password
from utils.jwt_helper import create_access_token
from validators.auth_validator import validate_login_payload, validate_signup_payload


def _serialize_user(user):
    return {
        'id': user['id'],
        'email': user['email'],
        'display_name': user['display_name'] or 'Learner',
        'role': user['role'],
    }


def _build_refresh_token(user_id, user_agent=None, ip_address=None, remember=False):
    token = secrets.token_urlsafe(48)
    expires_at = datetime.utcnow() + timedelta(days=Settings.REMEMBER_ME_EXPIRES_DAYS if remember else Settings.REFRESH_TOKEN_EXPIRES_DAYS)
    store_refresh_token(user_id, token, expires_at, user_agent=user_agent, ip_address=ip_address)
    return token, expires_at


def register_user(email, password, display_name=None, guest_session_id=None, remember=False, user_agent=None, ip_address=None):
    validated = validate_signup_payload(email, password)
    existing = get_user_by_email(validated['email'])
    if existing:
        raise ValueError('Email already registered')

    password_hash = hash_password(validated['password'])
    user_id = create_user(validated['email'], password_hash, display_name)

    if guest_session_id:
        convert_guest_to_user(guest_session_id, user_id)

    access_token = create_access_token({'sub': str(user_id), 'role': 'user'})
    refresh_token, refresh_expires = _build_refresh_token(user_id, user_agent=user_agent, ip_address=ip_address, remember=remember)

    return {
        'user': _serialize_user({
            'id': user_id,
            'email': validated['email'],
            'display_name': display_name,
            'role': 'user',
        }),
        'access_token': access_token,
        'refresh_token': refresh_token,
        'refresh_expires': refresh_expires,
    }


def authenticate_user(email, password, remember=False, user_agent=None, ip_address=None):
    validated = validate_login_payload(email, password)
    user = get_user_by_email(validated['email'])
    if not user or not user.get('is_active'):
        return None

    if not check_password(validated['password'], user['password_hash']):
        return None

    update_user_last_active(user['id'])
    access_token = create_access_token({'sub': str(user['id']), 'role': user['role']})
    refresh_token, refresh_expires = _build_refresh_token(user['id'], user_agent=user_agent, ip_address=ip_address, remember=remember)

    return {
        'user': _serialize_user(user),
        'access_token': access_token,
        'refresh_token': refresh_token,
        'refresh_expires': refresh_expires,
    }


def get_user_session(refresh_token):
    if not refresh_token:
        return None

    record = find_refresh_token(refresh_token)
    if not record or record.get('revoked') or record.get('expires_at') is None:
        return None

    if record['expires_at'] < datetime.utcnow():
        revoke_refresh_token(refresh_token)
        return None

    user = get_user_by_id(record['user_id'])
    if not user or not user.get('is_active'):
        revoke_refresh_token(refresh_token)
        return None

    return {
        'user': _serialize_user(user),
        'access_token': create_access_token({'sub': str(user['id']), 'role': user['role']}),
    }


def refresh_user_session(refresh_token):
    session_payload = get_user_session(refresh_token)
    if not session_payload:
        return None

    revoke_refresh_token(refresh_token)
    new_refresh_token, refresh_expires = _build_refresh_token(session_payload['user']['id'])

    return {
        'user': session_payload['user'],
        'access_token': session_payload['access_token'],
        'refresh_token': new_refresh_token,
        'refresh_expires': refresh_expires,
    }


def logout_user(refresh_token):
    if refresh_token:
        revoke_refresh_token(refresh_token)
    return True


def create_guest_profile():
    session_id = create_guest_session()
    access_token = create_access_token({'sub': session_id, 'role': 'guest', 'guest': True})
    return {
        'session_id': session_id,
        'access_token': access_token,
        'user': {
            'role': 'guest',
            'display_name': 'Guest Learner',
        },
        'role': 'guest',
    }


def create_guest_access_token(session_id):
    return create_access_token({'sub': session_id, 'role': 'guest', 'guest': True})


def track_guest_usage(session_id, module_type):
    return update_guest_usage(session_id, module_type)

from functools import wraps
from flask import request, jsonify, g
from utils.jwt_helper import decode_access_token
from models.guest_session_model import get_guest_session
from models.user_model import get_user_by_id
from utils.response import error


def _load_guest_from_cookie():
    session_id = request.cookies.get('guest_session_id')
    if not session_id:
        return None
    guest = get_guest_session(session_id)
    if not guest:
        return None
    return {
        'role': 'guest',
        'guest_session_id': guest['session_id'],
        'usage_counts': guest['usage_counts'],
    }


def jwt_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()

        if token:
            try:
                payload = decode_access_token(token)
            except ValueError as exc:
                return error(str(exc), 401)

            if payload.get('role') == 'user':
                user = get_user_by_id(payload.get('sub'))
                if not user:
                    return error('User account not found', 401)
                g.current_user = {
                    'id': user['id'],
                    'email': user['email'],
                    'display_name': user['display_name'],
                    'role': user['role'],
                }
                return view(*args, **kwargs)
            elif payload.get('role') == 'guest':
                guest = _load_guest_from_cookie()
                if not guest or payload.get('sub') != guest['guest_session_id']:
                    return error('Guest session invalid or expired', 401)
                g.current_user = guest
                return view(*args, **kwargs)

            return error('Unauthorized user type', 401)

        return error('Authentication required', 401)

    return wrapped


def optional_auth(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()

        if token:
            try:
                payload = decode_access_token(token)
            except ValueError:
                token = None
                payload = None

        if token and payload and payload.get('role') == 'user':
            user = get_user_by_id(payload.get('sub'))
            if user:
                g.current_user = {
                    'id': user['id'],
                    'email': user['email'],
                    'display_name': user['display_name'],
                    'role': user['role'],
                }
                return view(*args, **kwargs)

        guest = _load_guest_from_cookie()
        if guest and payload and payload.get('role') == 'guest' and payload.get('sub') == guest['guest_session_id']:
            g.current_user = guest
            return view(*args, **kwargs)
        if guest and not token:
            g.current_user = guest
            return view(*args, **kwargs)

        g.current_user = None
        return view(*args, **kwargs)

    return wrapped

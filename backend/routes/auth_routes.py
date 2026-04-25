from datetime import datetime
from flask import Blueprint, request, make_response
from services.auth_service import authenticate_user, register_user, refresh_user_session, logout_user, create_guest_profile, create_guest_access_token
from models.guest_session_model import get_guest_session
from utils.response import success, error
from config.settings import Settings

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def _attach_refresh_cookie(response, refresh_token, expires_at):
    age = int((expires_at - datetime.utcnow()).total_seconds())
    same_site = 'None' if Settings.JWT_COOKIE_SECURE else 'Lax'
    response.set_cookie(
        key=Settings.JWT_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=Settings.JWT_COOKIE_SECURE,
        samesite=same_site,
        max_age=age,
        path='/',
    )
    return response


def _clear_refresh_cookie(response):
    same_site = 'None' if Settings.JWT_COOKIE_SECURE else 'Lax'
    response.set_cookie(
        key=Settings.JWT_COOKIE_NAME,
        value='',
        httponly=True,
        secure=Settings.JWT_COOKIE_SECURE,
        samesite=same_site,
        expires=0,
        path='/',
    )
    return response


@auth_bp.route('/signup', methods=['POST'])
def signup():
    payload = request.json or {}
    try:
        guest_session_id = request.cookies.get('guest_session_id')
        remember = bool(payload.get('remember', False))
        auth_payload = register_user(
            payload.get('email'),
            payload.get('password'),
            display_name=payload.get('display_name'),
            guest_session_id=guest_session_id,
            remember=remember,
            user_agent=request.headers.get('User-Agent', ''),
            ip_address=request.remote_addr,
        )
        response = make_response(success({'user': auth_payload['user'], 'access_token': auth_payload['access_token']}))
        _attach_refresh_cookie(response, auth_payload['refresh_token'], auth_payload['refresh_expires'])
        return response
    except ValueError as exc:
        print(f"[AUTH SIGNUP] validation error: {exc}")
        return error(str(exc), 400)
    except Exception as exc:
        print(f"[AUTH SIGNUP] unexpected error: {exc}")
        return error(str(exc), 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    payload = request.json or {}
    try:
        remember = bool(payload.get('remember', False))
        auth_payload = authenticate_user(
            payload.get('email'),
            payload.get('password'),
            remember=remember,
            user_agent=request.headers.get('User-Agent', ''),
            ip_address=request.remote_addr,
        )
        if not auth_payload:
            return error('Invalid email or password', 401)

        response = make_response(success({'user': auth_payload['user'], 'access_token': auth_payload['access_token']}))
        _attach_refresh_cookie(response, auth_payload['refresh_token'], auth_payload['refresh_expires'])
        return response
    except ValueError as exc:
        print(f"[AUTH LOGIN] validation error: {exc}")
        return error(str(exc), 400)
    except Exception as exc:
        print(f"[AUTH LOGIN] unexpected error: {exc}")
        return error(str(exc), 500)


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    refresh_token = request.cookies.get(Settings.JWT_COOKIE_NAME)
    try:
        auth_payload = refresh_user_session(refresh_token)
        if not auth_payload:
            response = make_response(error('Refresh token invalid or expired', 401))
            _clear_refresh_cookie(response)
            return response

        response = make_response(success({'user': auth_payload['user'], 'access_token': auth_payload['access_token']}))
        _attach_refresh_cookie(response, auth_payload['refresh_token'], auth_payload['refresh_expires'])
        return response
    except Exception as exc:
        print(f"[AUTH REFRESH] unexpected error: {exc}")
        response = make_response(error('Unable to refresh session', 500))
        _clear_refresh_cookie(response)
        return response


@auth_bp.route('/session', methods=['GET'])
def session():
    refresh_token = request.cookies.get(Settings.JWT_COOKIE_NAME)
    auth_payload = refresh_user_session(refresh_token)
    if auth_payload:
        response = make_response(success({'user': auth_payload['user'], 'access_token': auth_payload['access_token']}))
        _attach_refresh_cookie(response, auth_payload['refresh_token'], auth_payload['refresh_expires'])
        return response

    guest_session_id = request.cookies.get('guest_session_id')
    if guest_session_id:
        guest = get_guest_session(guest_session_id)
        if guest:
            access_token = create_guest_access_token(guest_session_id)
            return success({
                'user': {
                    'role': 'guest',
                    'display_name': 'Guest Learner',
                },
                'access_token': access_token,
            })

    return error('No active session', 401)


@auth_bp.route('/logout', methods=['POST'])
def logout():
    refresh_token = request.cookies.get(Settings.JWT_COOKIE_NAME)
    logout_user(refresh_token)
    response = make_response(success({'message': 'Logged out successfully'}))
    _clear_refresh_cookie(response)
    return response


@auth_bp.route('/guest', methods=['POST'])
def guest():
    payload = request.json or {}
    guest_profile = create_guest_profile()
    same_site = 'None' if Settings.JWT_COOKIE_SECURE else 'Lax'
    response = make_response(success({'guest_session_id': guest_profile['session_id'], 'access_token': guest_profile['access_token'], 'role': 'guest'}))
    response.set_cookie(
        key='guest_session_id',
        value=guest_profile['session_id'],
        httponly=True,
        secure=Settings.JWT_COOKIE_SECURE,
        samesite=same_site,
        max_age=Settings.GUEST_SESSION_LIFETIME_HOURS * 3600,
        path='/',
    )
    return response

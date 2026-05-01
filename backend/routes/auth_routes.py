from flask import Blueprint, g, jsonify, request
import bcrypt
import jwt
import re

from models.guest_session_model import GuestSessionModel
from models.refresh_token_model import RefreshTokenModel
from models.user_model import UserModel
from utils.auth import auth_required, create_access_token, create_refresh_token, decode_token, get_bearer_token


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_email(email):
    return bool(email and EMAIL_RE.match(email))


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = data.get("name")

    if not email or not password:
        return jsonify({"status": "fail", "message": "Email and password are required."}), 400
    if not isinstance(password, str):
        return jsonify({"status": "fail", "message": "Password must be a string."}), 400
    if not _validate_email(email):
        return jsonify({"status": "fail", "message": "Invalid email format."}), 400

    if UserModel.find_by_email(email):
        return jsonify({"status": "fail", "message": "User already exists."}), 409

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = UserModel.create_user(email=email, password_hash=hashed, name=name)
    if not user:
        return jsonify({"status": "fail", "message": "User already exists."}), 409

    access_token, _ = create_access_token(user["id"])
    refresh_token, refresh_expires_at = create_refresh_token(user["id"])
    RefreshTokenModel.create_token(user["id"], refresh_token, refresh_expires_at)

    return jsonify(
        {
            "status": "created",
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"status": "fail", "message": "Email and password are required."}), 400
    if not isinstance(password, str):
        return jsonify({"status": "fail", "message": "Password must be a string."}), 400
    if not _validate_email(email):
        return jsonify({"status": "fail", "message": "Invalid email format."}), 400

    user = UserModel.find_by_email(email, include_password=True)
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return jsonify({"status": "fail"}), 401

    UserModel.touch_login(str(user["_id"]))
    public_user = UserModel.update_streak(str(user["_id"]))
    access_token, _ = create_access_token(str(user["_id"]))
    refresh_token, refresh_expires_at = create_refresh_token(str(user["_id"]))
    RefreshTokenModel.create_token(str(user["_id"]), refresh_token, refresh_expires_at)

    return jsonify(
        {
            "status": "success",
            "user": public_user,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json(silent=True) or {}
    refresh_token = data.get("refresh_token") or get_bearer_token()
    if not refresh_token:
        return jsonify({"status": "fail", "message": "Missing refresh token."}), 400
    if not isinstance(refresh_token, str):
        return jsonify({"status": "fail", "message": "Refresh token must be a string."}), 400

    stored_token = RefreshTokenModel.find_token(refresh_token)
    if not stored_token or stored_token.get("is_revoked"):
        return jsonify({"status": "fail", "message": "Refresh token is invalid."}), 401

    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except jwt.PyJWTError:
        RefreshTokenModel.revoke_token(refresh_token)
        return jsonify({"status": "fail", "message": "Refresh token expired or invalid."}), 401

    RefreshTokenModel.revoke_token(refresh_token)
    access_token, _ = create_access_token(payload["sub"])
    next_refresh_token, refresh_expires_at = create_refresh_token(payload["sub"])
    RefreshTokenModel.create_token(payload["sub"], next_refresh_token, refresh_expires_at)

    return jsonify(
        {
            "status": "success",
            "access_token": access_token,
            "refresh_token": next_refresh_token,
        }
    )


@auth_bp.route("/guest", methods=["POST"])
def guest_login():
    data = request.get_json(silent=True) or {}
    metadata = data.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        return jsonify({"status": "fail", "message": "Metadata must be an object."}), 400
    guest_session = GuestSessionModel.create_session(metadata=metadata)
    guest_email = f"guest-{guest_session['session_id']}@guest.smarttextbot.local"
    user = UserModel.create_user(
        email=guest_email,
        password_hash="",
        name="Guest User",
        is_guest=True,
        guest_session_id=guest_session["session_id"],
    )
    if not user:
        return jsonify({"status": "fail", "message": "Unable to create guest user."}), 500

    access_token, _ = create_access_token(user["id"])
    refresh_token, refresh_expires_at = create_refresh_token(user["id"])
    RefreshTokenModel.create_token(user["id"], refresh_token, refresh_expires_at)

    return jsonify(
        {
            "status": "success",
            "user": user,
            "guest_session": guest_session,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )


@auth_bp.route("/logout", methods=["POST"])
def logout():
    data = request.get_json(silent=True) or {}
    refresh_token = data.get("refresh_token")
    if refresh_token is not None and not isinstance(refresh_token, str):
        return jsonify({"status": "fail", "message": "Refresh token must be a string."}), 400
    if refresh_token:
        RefreshTokenModel.revoke_token(refresh_token)
    return jsonify({"status": "success"})


@auth_bp.route("/me", methods=["GET"])
@auth_required
def me():
    return jsonify({"status": "success", "user": g.current_user})
=======
from datetime import datetime
from flask import Blueprint, request, make_response
from services.auth_service import authenticate_user, register_user, refresh_user_session, logout_user, create_guest_profile, create_guest_access_token, get_user_session
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
    auth_payload = get_user_session(refresh_token)
    if auth_payload:
        return success({'user': auth_payload['user'], 'access_token': auth_payload['access_token']})

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
    response.set_cookie(
        key='guest_session_id',
        value='',
        httponly=True,
        secure=Settings.JWT_COOKIE_SECURE,
        samesite='None' if Settings.JWT_COOKIE_SECURE else 'Lax',
        expires=0,
        path='/',
    )
    return response


@auth_bp.route('/guest', methods=['POST'])
def guest():
    guest_profile = create_guest_profile()
    same_site = 'None' if Settings.JWT_COOKIE_SECURE else 'Lax'
    response = make_response(success({
        'guest_session_id': guest_profile['session_id'],
        'access_token': guest_profile['access_token'],
        'user': guest_profile['user'],
        'role': 'guest',
    }))
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
>>>>>>> 7a39e76952f1835cf7031449b83138e654424a73

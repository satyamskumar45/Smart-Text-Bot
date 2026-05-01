from functools import wraps

from flask import g, request

from models.guest_session_model import get_guest_session
from models.user_model import get_user_by_id
from utils.jwt_helper import decode_access_token
from utils.response import error


def _load_guest_from_cookie():
    session_id = request.cookies.get("guest_session_id")
    if not session_id:
        return None
    guest = get_guest_session(session_id)
    if not guest:
        return None
    return {
        "role": "guest",
        "guest_session_id": guest["session_id"],
        "usage_counts": guest.get("usage_counts", {}),
    }


def _load_principal_from_token(token):
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        return None, exc

    if payload.get("role") == "user":
        user = get_user_by_id(payload.get("sub"))
        if not user:
            return None, ValueError("User account not found")
        return {
            "id": user["id"],
            "email": user["email"],
            "display_name": user["display_name"],
            "role": user["role"],
        }, None

    if payload.get("role") == "guest":
        guest = _load_guest_from_cookie()
        if not guest or payload.get("sub") != guest["guest_session_id"]:
            return None, ValueError("Guest session invalid or expired")
        return guest, None

    return None, ValueError("Unauthorized user type")


def jwt_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()

        if token:
            principal, auth_error = _load_principal_from_token(token)
            if principal:
                g.current_user = principal
                return view(*args, **kwargs)
            if not _load_guest_from_cookie():
                return error(str(auth_error), 401)

        guest = _load_guest_from_cookie()
        if guest:
            g.current_user = guest
            return view(*args, **kwargs)

        return error("Authentication required", 401)

    return wrapped


def optional_auth(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()

        if token:
            principal, auth_error = _load_principal_from_token(token)
            if principal:
                g.current_user = principal
                return view(*args, **kwargs)
            if auth_error and "User account not found" in str(auth_error):
                g.current_user = None
                return view(*args, **kwargs)

        guest = _load_guest_from_cookie()
        if guest:
            g.current_user = guest
            return view(*args, **kwargs)

        g.current_user = None
        return view(*args, **kwargs)

    return wrapped

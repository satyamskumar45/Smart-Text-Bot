from functools import wraps

import jwt
from flask import g

from models.user_model import UserModel
from utils.auth import decode_token, get_bearer_token
from utils.response import error


def _load_user_from_token():
    token = get_bearer_token()
    if not token:
        return None, None

    try:
        payload = decode_token(token, expected_type="access")
    except jwt.PyJWTError as exc:
        return None, exc

    user = UserModel.find_by_id(payload.get("sub"))
    if not user:
        return None, ValueError("User account not found")

    return user, None


def jwt_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user, auth_error = _load_user_from_token()
        if not user:
            return error(str(auth_error or "Authentication required"), 401)

        g.current_user = user
        return view(*args, **kwargs)

    return wrapped


def optional_auth(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user, _auth_error = _load_user_from_token()
        g.current_user = user
        return view(*args, **kwargs)

    return wrapped

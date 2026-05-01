import os
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import g, jsonify, request

from models.user_model import UserModel


JWT_ALGORITHM = "HS256"
ACCESS_TTL_MINUTES = int(os.getenv("JWT_ACCESS_TTL_MINUTES", "15"))
REFRESH_TTL_DAYS = int(os.getenv("JWT_REFRESH_TTL_DAYS", "30"))


def _utcnow():
    return datetime.now(timezone.utc)


def _get_jwt_secret():
    secret = os.getenv("JWT_SECRET_KEY")
    if not secret:
        raise RuntimeError("JWT_SECRET_KEY environment variable is required.")
    return secret


def _build_user_claims(user_or_id, email=None, role=None):
    if isinstance(user_or_id, dict):
        user_id = user_or_id.get("id") or user_or_id.get("_id") or user_or_id.get("sub")
        user_email = user_or_id.get("email")
        user_role = user_or_id.get("role") or ("guest" if user_or_id.get("is_guest") else "user")
    else:
        user_id = user_or_id
        user_email = email
        user_role = role or "user"

    return {
        "sub": str(user_id),
        "user_id": str(user_id),
        "email": user_email,
        "role": user_role,
    }


def create_access_token(user_or_id, email=None, role=None):
    expires_at = _utcnow() + timedelta(minutes=ACCESS_TTL_MINUTES)
    claims = _build_user_claims(user_or_id, email=email, role=role)
    token = jwt.encode(
        {**claims, "type": "access", "exp": expires_at, "iat": _utcnow(), "jti": str(uuid4())},
        _get_jwt_secret(),
        algorithm=JWT_ALGORITHM,
    )
    return token, expires_at


def create_refresh_token(user_or_id, email=None, role=None):
    expires_at = _utcnow() + timedelta(days=REFRESH_TTL_DAYS)
    claims = _build_user_claims(user_or_id, email=email, role=role)
    token = jwt.encode(
        {**claims, "type": "refresh", "exp": expires_at, "iat": _utcnow(), "jti": str(uuid4())},
        _get_jwt_secret(),
        algorithm=JWT_ALGORITHM,
    )
    return token, expires_at


def decode_token(token, expected_type=None):
    payload = jwt.decode(token, _get_jwt_secret(), algorithms=[JWT_ALGORITHM])
    if expected_type and payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("Unexpected token type.")
    return payload


def get_bearer_token():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    return header.split(" ", 1)[1].strip()


def auth_required(route_handler):
    @wraps(route_handler)
    def wrapper(*args, **kwargs):
        token = get_bearer_token()
        if not token:
            return jsonify({"status": "fail", "message": "Missing access token."}), 401

        try:
            payload = decode_token(token, expected_type="access")
        except jwt.PyJWTError:
            return jsonify({"status": "fail", "message": "Invalid or expired access token."}), 401

        user = UserModel.find_by_id(payload["sub"])
        if not user:
            return jsonify({"status": "fail", "message": "User not found."}), 401

        g.current_user_id = user["id"]
        g.current_user = user
        return route_handler(*args, **kwargs)

    return wrapper


def require_role(expected_role):
    def decorator(route_handler):
        @wraps(route_handler)
        def wrapper(*args, **kwargs):
            current_user = getattr(g, "current_user", None)
            if not current_user:
                return jsonify({"status": "fail", "message": "Authentication required."}), 401

            current_role = current_user.get("role") or ("guest" if current_user.get("is_guest") else "user")
            if current_role != expected_role:
                return jsonify({"status": "fail", "message": "Forbidden."}), 403

            return route_handler(*args, **kwargs)

        return wrapper

    return decorator

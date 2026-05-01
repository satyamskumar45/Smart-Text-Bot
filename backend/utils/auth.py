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


def create_access_token(user_id):
    expires_at = _utcnow() + timedelta(minutes=ACCESS_TTL_MINUTES)
    token = jwt.encode(
        {"sub": user_id, "type": "access", "exp": expires_at, "iat": _utcnow(), "jti": str(uuid4())},
        _get_jwt_secret(),
        algorithm=JWT_ALGORITHM,
    )
    return token, expires_at


def create_refresh_token(user_id):
    expires_at = _utcnow() + timedelta(days=REFRESH_TTL_DAYS)
    token = jwt.encode(
        {"sub": user_id, "type": "refresh", "exp": expires_at, "iat": _utcnow(), "jti": str(uuid4())},
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

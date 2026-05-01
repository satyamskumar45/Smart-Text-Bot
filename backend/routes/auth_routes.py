import re
import logging

import bcrypt
import jwt
from flask import Blueprint, g, jsonify, request

from models.guest_session_model import GuestSessionModel
from models.refresh_token_model import RefreshTokenModel
from models.user_model import UserModel, serialize_user
from utils.auth import auth_required, create_access_token, create_refresh_token, decode_token, get_bearer_token


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

logger = logging.getLogger(__name__)

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

    try:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    except Exception:
        logger.exception("Error hashing password for email=%s", email)
        return jsonify({"status": "error", "message": "Internal server error."}), 500

    try:
        user = UserModel.create_user(email=email, password_hash=hashed, name=name, role="user")
    except Exception:
        logger.exception("Unexpected error creating user for email=%s", email)
        return jsonify({"status": "error", "message": "Internal server error."}), 500

    if not user:
        return jsonify({"status": "fail", "message": "User already exists."}), 409

    # Generate tokens and persist refresh token. Catch any JWT/env/db issues explicitly
    try:
        access_token, _ = create_access_token(user)
        refresh_token, refresh_expires_at = create_refresh_token(user)
        # PyJWT older versions may return bytes
        if isinstance(access_token, bytes):
            access_token = access_token.decode("utf-8")
        if isinstance(refresh_token, bytes):
            refresh_token = refresh_token.decode("utf-8")
        RefreshTokenModel.create_token(user["id"], refresh_token, refresh_expires_at)
    except RuntimeError as rexc:
        # likely missing JWT_SECRET_KEY
        logger.exception("JWT configuration error while creating tokens for user=%s: %s", user.get("id"), rexc)
        return jsonify({"status": "error", "message": "Authentication configuration error."}), 500
    except jwt.PyJWTError as jexc:
        logger.exception("JWT error while creating tokens for user=%s: %s", user.get("id"), jexc)
        return jsonify({"status": "error", "message": "Token generation failed."}), 500
    except Exception:
        logger.exception("Error storing refresh token for user=%s", user.get("id"))
        return jsonify({"status": "error", "message": "Internal server error."}), 500

    return jsonify(
        {
            "status": "created",
            "user": serialize_user(user),
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
    access_token, _ = create_access_token(public_user)
    refresh_token, refresh_expires_at = create_refresh_token(public_user)
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
    user = UserModel.find_by_id(payload["sub"])
    if not user:
        return jsonify({"status": "fail", "message": "User not found."}), 401

    access_token, _ = create_access_token(user)
    next_refresh_token, refresh_expires_at = create_refresh_token(user)
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
        role="guest",
    )
    if not user:
        return jsonify({"status": "fail", "message": "Unable to create guest user."}), 500

    try:
        access_token, _ = create_access_token(user)
        refresh_token, refresh_expires_at = create_refresh_token(user)
        if isinstance(access_token, bytes):
            access_token = access_token.decode("utf-8")
        if isinstance(refresh_token, bytes):
            refresh_token = refresh_token.decode("utf-8")
        RefreshTokenModel.create_token(user["id"], refresh_token, refresh_expires_at)
    except Exception:
        logger.exception("Error creating guest tokens for session=%s", guest_session.get("session_id"))
        return jsonify({"status": "error", "message": "Internal server error."}), 500

    return jsonify(
        {
            "status": "success",
            "user": serialize_user(user),
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

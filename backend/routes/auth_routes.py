import re
import logging
import traceback

import bcrypt
import jwt
from flask import Blueprint, g, jsonify, request, current_app

from models.guest_session_model import GuestSessionModel
from models.refresh_token_model import RefreshTokenModel
from models.user_model import UserModel, serialize_user
from utils.auth import auth_required, create_access_token, create_refresh_token, decode_token, get_bearer_token


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
logger = logging.getLogger(__name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_email(email):
    return bool(email and EMAIL_RE.match(email))


# ================= SIGNUP =================
@auth_bp.route("/signup", methods=["POST"])
def signup():
    try:
        current_app.logger.info("Signup endpoint called")

        data = request.get_json(silent=True) or {}

        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        name = data.get("name")

        # ✅ Validation
        if not email or not password:
            return jsonify({"status": "fail", "message": "Email and password are required."}), 400

        if not isinstance(password, str):
            return jsonify({"status": "fail", "message": "Password must be a string."}), 400

        if not _validate_email(email):
            return jsonify({"status": "fail", "message": "Invalid email format."}), 400

        # ✅ Check existing user
        existing_user = UserModel.find_by_email(email)
        if existing_user is not None:
            return jsonify({"status": "fail", "message": "User already exists."}), 409

        # ✅ Hash password
        try:
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        except Exception as e:
            current_app.logger.exception("Password hashing failed")
            return jsonify({"status": "error", "message": str(e)}), 500

        # ✅ Create user
        try:
            user = UserModel.create_user(
                email=email,
                password_hash=hashed,
                name=name,
                role="user"
            )
        except Exception as e:
            current_app.logger.exception("User creation failed")
            return jsonify({"status": "error", "message": str(e)}), 500

        if not user:
            return jsonify({"status": "fail", "message": "User already exists."}), 409

        # ✅ SAFE USER ID EXTRACTION (FIXED BUG)
        user_id = str(user.get("_id") or user.get("id"))

        # ✅ Generate tokens
        try:
            access_token, _ = create_access_token(user)
            refresh_token, refresh_expires_at = create_refresh_token(user)

            if isinstance(access_token, bytes):
                access_token = access_token.decode("utf-8")

            if isinstance(refresh_token, bytes):
                refresh_token = refresh_token.decode("utf-8")

            # 🔥 FIXED LINE
            RefreshTokenModel.create_token(user_id, refresh_token, refresh_expires_at)

        except Exception as e:
            current_app.logger.exception("Token creation failed")
            return jsonify({"status": "error", "message": str(e)}), 500

        # ✅ Final response
        response = {
            "status": "created",
            "message": "User created successfully",
            "user": serialize_user(user),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

        current_app.logger.info(f"User created: {user_id}")

        return jsonify(response), 201

    except Exception as e:
        current_app.logger.exception("Unhandled signup error")
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)  # 🔥 now shows real error
        }), 500


# ================= LOGIN =================
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(silent=True) or {}

        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        if not email or not password:
            return jsonify({"status": "fail", "message": "Email and password are required."}), 400

        if not _validate_email(email):
            return jsonify({"status": "fail", "message": "Invalid email format."}), 400

        user = UserModel.find_by_email(email, include_password=True)

        if not user:
            return jsonify({"status": "fail", "message": "Invalid credentials"}), 401

        if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            return jsonify({"status": "fail", "message": "Invalid credentials"}), 401

        user_id = str(user.get("_id") or user.get("id"))

        access_token, _ = create_access_token(user)
        refresh_token, refresh_expires_at = create_refresh_token(user)

        RefreshTokenModel.create_token(user_id, refresh_token, refresh_expires_at)

        return jsonify({
            "status": "success",
            "user": serialize_user(user),
            "access_token": access_token,
            "refresh_token": refresh_token,
        })

    except Exception as e:
        current_app.logger.exception("Login error")
        return jsonify({"status": "error", "message": str(e)}), 500


# ================= ME =================
@auth_bp.route("/me", methods=["GET"])
@auth_required
def me():
    return jsonify({
        "status": "success",
        "user": g.current_user
    })
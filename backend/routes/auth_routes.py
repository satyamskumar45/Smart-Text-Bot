import logging

from flask import Blueprint, g, request, current_app

from services.auth_service import register_user, authenticate_user, logout_user
from utils.response import success_response, error_response
from utils.auth import auth_required, get_bearer_token


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
logger = logging.getLogger(__name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    try:
        payload = request.get_json(silent=True) or {}
        result = register_user(
            email=payload.get("email"),
            password=payload.get("password"),
            display_name=payload.get("name"),
            guest_session_id=payload.get("guest_session_id"),
            remember=bool(payload.get("remember")),
            user_agent=request.headers.get("User-Agent"),
            ip_address=request.remote_addr,
        )
        return success_response(data=result, message="User created", status_code=201)
    except ValueError as ve:
        current_app.logger.info("Signup validation/error: %s", ve)
        return error_response(message=str(ve), status_code=400)
    except Exception:
        current_app.logger.exception("Unhandled signup error")
        return error_response(message="Internal server error", status_code=500)


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        payload = request.get_json(silent=True) or {}
        remember = bool(payload.get("remember"))
        result = authenticate_user(
            email=payload.get("email"),
            password=payload.get("password"),
            remember=remember,
            user_agent=request.headers.get("User-Agent"),
            ip_address=request.remote_addr,
        )
        if not result:
            current_app.logger.info("Login failed: no result returned for email=%s", payload.get("email"))
            return error_response(message="Invalid credentials", status_code=401)

        return success_response(data=result, message="Login successful", status_code=200)
    except ValueError as ve:
        # Map known validation/value errors to appropriate status codes
        msg = str(ve) or "Invalid request"
        lower = msg.lower()
        current_app.logger.info("Login validation/error: %s", msg)

        if "not found" in lower or "no user" in lower:
            return error_response(message=msg, status_code=404)
        if "invalid" in lower or "password" in lower or "credentials" in lower:
            return error_response(message="Invalid credentials", status_code=401)
        if "inactive" in lower:
            return error_response(message=msg, status_code=403)

        return error_response(message=msg, status_code=400)
    except Exception:
        current_app.logger.exception("Login error")
        return error_response(message="Internal server error", status_code=500)


@auth_bp.route("/me", methods=["GET"])
@auth_required
def me():
    return success_response(data={"user": g.current_user}, message="Current user", status_code=200)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    try:
        data = request.get_json(silent=True) or {}
        refresh_token = data.get("refresh_token") or request.cookies.get("refresh_token") or get_bearer_token()
        logout_user(refresh_token)
        return success_response(message="Logged out", status_code=200)
    except Exception:
        current_app.logger.exception("Logout error")
        return error_response(message="Internal server error", status_code=500)
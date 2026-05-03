
from flask import Blueprint, request, current_app
from services.chatbot_service import translate as translate_service
from utils.response import success, error

translate_bp = Blueprint("translate", __name__)


@translate_bp.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json(silent=True) or {}
        text = data.get("text")
        target = data.get("target")
        translated = translate_service(text, target)
        return success({"translation": translated}, status_code=200)
    except ValueError as ve:
        current_app.logger.info("Translate validation error: %s", ve)
        return error(message=str(ve), status_code=400)
    except Exception as exc:
        current_app.logger.exception("Translate error")
        return error(message="Translation failed", status_code=500)

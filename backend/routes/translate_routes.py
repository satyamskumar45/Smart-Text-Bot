
from flask import Blueprint, request, current_app
from services.chatbot_service import translate as translate_service
from utils.response import success_response, error_response

translate_bp = Blueprint("translate", __name__)


@translate_bp.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json(silent=True) or {}
        text = (data.get("text") or "").strip()
        source = (data.get("source") or data.get("source_lang") or "auto").strip()
        target = (data.get("target") or data.get("target_lang") or "").strip()
        tone = (data.get("tone") or "").strip().lower()
        include_variants = bool(data.get("include_variants"))

        if not text:
            current_app.logger.info("Translate called without text")
            return error_response(message="'text' is required", status_code=400)

        if not target:
            current_app.logger.info("Translate called without target language")
            return error_response(message="'target' language is required", status_code=400)

        translated = translate_service(text, target, source=source, tone=tone)
        response_data = {"translation": translated}

        if include_variants:
            response_data["variants"] = {
                "formal": translate_service(text, target, source=source, tone="formal"),
                "informal": translate_service(text, target, source=source, tone="informal conversational"),
                "simple": translate_service(text, target, source=source, tone="simple beginner-friendly"),
            }

        return success_response(data=response_data, message="Translation successful", status_code=200)

    except ValueError as ve:
        current_app.logger.info("Translate validation error: %s", ve)
        return error_response(message=str(ve), status_code=400)
    except RuntimeError as re:
        # Likely configuration issue (e.g., missing API key)
        current_app.logger.exception("Translate runtime error: %s", re)
        return error_response(message="Translation service misconfigured", status_code=500)
    except Exception as exc:
        current_app.logger.exception("Translate error")
        return error_response(message="Translation failed", status_code=500)

from flask import Blueprint, request, current_app
from utils.response import success, error
from services.grammar_service import correct_text

grammar_bp = Blueprint("grammar", __name__)


@grammar_bp.route("/grammar", methods=["POST"])
def grammar():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return error("text is required", 400)

    try:
        corrected = correct_text(text)
        return success({"corrected": corrected}, status_code=200)
    except ValueError as ve:
        return error(str(ve), 400)
    except Exception:
        current_app.logger.exception("Grammar correction failed")
        return error("Grammar correction failed", 500)

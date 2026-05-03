
from flask import Blueprint, request, current_app
from utils.response import success_response, error_response

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        msg = (data.get("message") or "").strip()
        if not msg:
            return error_response(message="message is required", status_code=400)
        # placeholder reply until service integration
        reply = f"You said: {msg}"
        return success_response(data={"reply": reply}, status_code=200)
    except Exception:
        current_app.logger.exception("Chat endpoint error")
        return error_response(message="Internal server error", status_code=500)

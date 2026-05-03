
from flask import Blueprint, request, current_app
from services.groq_service import complete
from utils.response import success_response, error_response

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        msg = (data.get("message") or "").strip()
        if not msg:
            return error_response(message="message is required", status_code=400)
        system = (
            "You are a friendly language-learning coach. Give short, practical answers. "
            "If the user asks for practice, include one mini exercise and one model answer."
        )
        try:
            reply = complete(system, msg, temperature=0.6)
        except RuntimeError:
            reply = (
                "Try this mini practice: translate 'I am learning every day' into your target language. "
                "Then compare your answer with a dictionary or the Translate tool."
            )
        return success_response(data={"reply": reply}, status_code=200)
    except Exception:
        current_app.logger.exception("Chat endpoint error")
        return error_response(message="Internal server error", status_code=500)

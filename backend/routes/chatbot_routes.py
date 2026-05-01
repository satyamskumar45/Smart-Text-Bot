from flask import Blueprint, request, jsonify

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    msg = data.get("message", "")
    if not msg:
        return jsonify({"status": "fail", "message": "message is required"}), 400
    return jsonify({"status": "success", "reply": f"You said: {msg}"})

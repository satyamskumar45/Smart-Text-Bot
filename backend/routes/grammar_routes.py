from flask import Blueprint, request, jsonify

grammar_bp = Blueprint("grammar", __name__)


@grammar_bp.route("/grammar", methods=["POST"])
def grammar():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"status": "fail", "message": "text is required"}), 400

    try:
        import language_tool_python
        tool = language_tool_python.LanguageTool("en-US")
        matches = tool.check(text)
        corrected = language_tool_python.utils.correct(text, matches)
        return jsonify({"status": "success", "corrected": corrected})
    except Exception as exc:
        return jsonify({"status": "fail", "message": str(exc)}), 500

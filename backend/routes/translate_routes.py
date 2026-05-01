from flask import Blueprint, request, jsonify

translate_bp = Blueprint("translate", __name__)


@translate_bp.route("/translate", methods=["POST"])
def translate():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    target = data.get("target", "")
    if not text or not target:
        return jsonify({"status": "fail", "message": "text and target are required"}), 400

    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source="auto", target=target).translate(text)
        return jsonify({"status": "success", "translation": translated})
    except Exception as exc:
        return jsonify({"status": "fail", "message": str(exc)}), 500

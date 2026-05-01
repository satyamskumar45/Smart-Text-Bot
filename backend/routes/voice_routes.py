import os
import tempfile
import uuid

from flask import Blueprint, request, jsonify, send_file

voice_bp = Blueprint("voice", __name__)


@voice_bp.route("/tts", methods=["POST"])
def tts():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"status": "fail", "message": "text is required"}), 400

    try:
        from gtts import gTTS
        tmp_path = os.path.join(tempfile.gettempdir(), f"speech_{uuid.uuid4()}.mp3")
        gTTS(text).save(tmp_path)
        return send_file(tmp_path, mimetype="audio/mpeg", as_attachment=True,
                         download_name="speech.mp3")
    except Exception as exc:
        return jsonify({"status": "fail", "message": str(exc)}), 500

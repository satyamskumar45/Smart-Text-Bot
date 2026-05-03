
from flask import Blueprint, request, current_app, send_file
from utils.response import success, error
from services.voice_service import create_tts_file

voice_bp = Blueprint("voice", __name__)


@voice_bp.route("/tts", methods=["POST"])
def tts():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return error("text is required", 400)

    try:
        tmp_path = create_tts_file(text)
        return send_file(tmp_path, mimetype="audio/mpeg", as_attachment=True, download_name="speech.mp3")
    except ValueError as ve:
        return error(str(ve), 400)
    except Exception as exc:
        current_app.logger.exception("TTS generation failed")
        return error("TTS generation failed", 500)

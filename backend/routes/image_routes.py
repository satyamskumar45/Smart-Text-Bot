from flask import Blueprint, request, current_app
from services.chatbot_service import image_scan as image_service
from utils.response import success, error


image_bp = Blueprint("image", __name__)


@image_bp.route("/image-scan", methods=["POST"])
def image_scan():
    if "image" not in request.files:
        return error("No image uploaded", 400)

    try:
        uploaded = request.files.get("image")
        content = uploaded.read()
        result = image_service(content, filename=uploaded.filename)
        return success(result)
    except Exception:
        current_app.logger.exception("Image scan failed")
        return error("Image processing failed", 500)

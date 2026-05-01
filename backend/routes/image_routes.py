from flask import Blueprint, request

from utils.response import error, success


image_bp = Blueprint("image", __name__)


@image_bp.route("/image-scan", methods=["POST"])
def image_scan():
    if "image" not in request.files:
        return error("No image uploaded", 400)

    return success(
        {
            "text": "Image processing is currently unavailable for this deployment.",
        }
    )

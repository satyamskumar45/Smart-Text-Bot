from flask import Blueprint, request, jsonify
from services.groq_service import complete_json

image_bp = Blueprint('image', __name__)

@image_bp.route('/image-scan', methods=['POST'])
def image_scan():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    try:
        return jsonify({
            'text': 'Image processing is currently disabled (TinyLlama does not support vision yet).'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
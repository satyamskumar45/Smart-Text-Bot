"""
Standardized Response Format for all API endpoints.

All responses follow this structure:
- Success: {"success": true, "data": {...}, "error": null}
- Error: {"success": false, "data": null, "error": "message"}
"""

from flask import jsonify


def success(data, status_code=200):
    """Return a successful response."""
    return jsonify({
        'success': True,
        'data': data,
        'error': None
    }), status_code


def error(message, status_code=400):
    """Return an error response."""
    return jsonify({
        'success': False,
        'data': None,
        'error': message,
        'message': message,
    }), status_code

from flask import jsonify


def success_response(data=None, message="", status_code=200):
    payload = {"success": True, "data": data or {}, "message": message}
    return jsonify(payload), status_code


def error_response(message="An error occurred", status_code=400, data=None):
    payload = {"success": False, "data": data or {}, "message": message}
    return jsonify(payload), status_code


# Backwards-compatible aliases used across the repo
def success(data=None, message="", status_code=200):
    return success_response(data=data, message=message, status_code=status_code)


def error(message="An error occurred", status_code=400, data=None):
    return error_response(message=message, status_code=status_code, data=data)
from flask import jsonify


def success(data=None, status_code=200):
    if isinstance(data, dict):
        payload = {"status": "success", **data}
    elif data is None:
        payload = {"status": "success"}
    else:
        payload = {"status": "success", "data": data}

    return jsonify(payload), status_code


def error(message, status_code=400):
    return jsonify({"status": "fail", "message": str(message)}), status_code

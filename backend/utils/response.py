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

from flask import jsonify


def success(data=None, message: str | None = None, status_code: int = 200):
    body = {"success": True, "message": message or "OK", "data": data}
    return jsonify(body), status_code


def error(message: str, status_code: int = 400, detail=None):
    body = {"success": False, "message": message, "data": None}
    if detail is not None:
        body["detail"] = detail
    return jsonify(body), status_code

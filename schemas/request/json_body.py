from flask import request

from core.exceptions.app_exceptions import ValidationError


def get_json_body(required: bool = True) -> dict:
    payload = request.get_json(silent=True)
    if payload is None:
        if required:
            raise ValidationError("JSON body is required")
        return {}
    if not isinstance(payload, dict):
        raise ValidationError("JSON body must be an object")
    return payload

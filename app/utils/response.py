from flask import jsonify
from datetime import datetime, timezone
import uuid


def api_response(data=None, message='success', code=200, status_code=200):
    response = {
        'code': code,
        'message': message,
        'data': data,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'request_id': str(uuid.uuid4())
    }
    return jsonify(response), status_code


def success(data=None, message='success'):
    return api_response(data=data, message=message, code=200, status_code=200)


def created(data=None, message='created'):
    return api_response(data=data, message=message, code=201, status_code=201)


def error(message='error', code=400, status_code=400):
    return api_response(data=None, message=message, code=code, status_code=status_code)

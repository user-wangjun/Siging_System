from flask import Flask
from app.utils.response import error


class APIException(Exception):
    def __init__(self, message='API Error', code=400, status_code=400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(APIException):
    def __init__(self, message='Validation Error'):
        super().__init__(message=message, code=400, status_code=400)


class AuthenticationError(APIException):
    def __init__(self, message='Authentication Failed'):
        super().__init__(message=message, code=401, status_code=401)


class AuthorizationError(APIException):
    def __init__(self, message='Permission Denied'):
        super().__init__(message=message, code=403, status_code=403)


class NotFoundError(APIException):
    def __init__(self, message='Resource Not Found'):
        super().__init__(message=message, code=404, status_code=404)


class ConflictError(APIException):
    def __init__(self, message='Resource Conflict'):
        super().__init__(message=message, code=409, status_code=409)


class RateLimitError(APIException):
    def __init__(self, message='Too Many Requests'):
        super().__init__(message=message, code=429, status_code=429)


def register_error_handlers(app: Flask):
    @app.errorhandler(APIException)
    def handle_api_exception(e: APIException):
        return error(message=e.message, code=e.code, status_code=e.status_code)

    @app.errorhandler(404)
    def handle_not_found(e):
        return error(message='Resource not found', code=404, status_code=404)

    @app.errorhandler(500)
    def handle_server_error(e):
        return error(message='Internal server error', code=500, status_code=500)

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        return error(message=str(e), code=500, status_code=500)

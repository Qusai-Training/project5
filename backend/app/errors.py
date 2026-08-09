from flask import jsonify
from werkzeug.exceptions import HTTPException

class APIError(Exception):
    """Base Custom API Exception Class"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["error"] = self.message
        rv["message"] = self.message
        rv["status"] = self.status_code
        return rv

class UnauthorizedError(APIError):
    def __init__(self, message="Authentication token required or invalid"):
        super().__init__(message, status_code=401)

class NotFoundError(APIError):
    def __init__(self, message="Requested resource was not found"):
        super().__init__(message, status_code=404)

class ValidationError(APIError):
    def __init__(self, message="Invalid input parameters"):
        super().__init__(message, status_code=422)


def register_error_handlers(app):
    """Registers global error handlers for Flask app"""

    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        response = jsonify({
            "error": error.description,
            "message": error.description,
            "status": error.code
        })
        response.status_code = error.code
        return response

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        app.logger.error(f"Unhandled Exception: {str(error)}")
        response = jsonify({
            "error": "Internal Server Error",
            "status": 500
        })
        response.status_code = 500
        return response
from flask import Blueprint, request, jsonify
from app.services.auth_service import decode_jwt
from app.services import user_service
from app.errors import UnauthorizedError

user_bp = Blueprint("users", __name__, url_prefix="/api/users")

def get_authenticated_user_id():
    """Helper to extract and verify JWT token from request headers."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedError("Authorization bearer token is missing")

    token = auth_header.split(" ")[1]
    payload = decode_jwt(token)
    return payload["user_id"]

@user_bp.route("/me", methods=["GET"])
def get_current_user_profile():
    """Endpoint: GET /api/users/me - Returns active authenticated user data."""
    user_id = get_authenticated_user_id()
    user_data = user_service.get_user_by_id(user_id)
    return jsonify(user_data), 200
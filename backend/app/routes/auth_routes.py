from flask import Blueprint, request, jsonify
from app.services import auth_service
from app.services.auth_service import decode_jwt
from app.errors import ValidationError, UnauthorizedError

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def get_authenticated_user_id():
    """Helper to extract and verify JWT token from request headers."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedError("Authorization bearer token is missing")

    token = auth_header.split(" ")[1]
    payload = decode_jwt(token)
    return payload["user_id"]


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    result = auth_service.register_user(
        username=(data.get("username") or "").strip(),
        email=(data.get("email") or "").strip(),
        password=data.get("password") or "",
        phone=data.get("phone"),
        age=data.get("age"),
        major=data.get("major"),
        skills=data.get("skills") or data.get("skill_ids") or []
    )
    return jsonify(result), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    identifier = data.get("email") or data.get("username") or ""
    password = data.get("password") or ""

    if not identifier or not password:
        raise ValidationError("Email/username and password are required")

    result = auth_service.authenticate_user(identifier, password)
    return jsonify(result), 200


@auth_bp.route("/change-password", methods=["POST"])
def change_password():
    user_id = get_authenticated_user_id()
    data = request.get_json() or {}

    result = auth_service.change_password(
        user_id,
        old_password=data.get("old_password") or data.get("current_password"),
        new_password=data.get("new_password")
    )
    return jsonify(result), 200

from flask import Blueprint, request, jsonify
from app.services import auth_service
from app.errors import ValidationError

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    if not data.get("username") or not data.get("password") or not data.get("email"):
        raise ValidationError("Username, email, and password are required")

    result = auth_service.register_user(
        username=data.get("username"),
        email=data.get("email"),
        password=data.get("password"),
        phone=data.get("phone"),
        age=data.get("age"),
        major=data.get("major"),
        skill_ids=data.get("skill_ids")
    )
    return jsonify(result), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    if not data.get("username") or not data.get("password"):
        raise ValidationError("Username and password are required")

    result = auth_service.authenticate_user(data.get("username"), data.get("password"))
    return jsonify(result), 200
from flask import Blueprint, request, jsonify
from app.services.auth_service import decode_jwt
from app.services import skill_service
from app.errors import UnauthorizedError

skill_bp = Blueprint("skills", __name__, url_prefix="/api")


def get_current_user_id():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedError("Missing or invalid authorization token")

    token = auth_header.split(" ")[1]
    payload = decode_jwt(token)
    return payload["user_id"]


@skill_bp.route("/skills", methods=["GET"])
def list_skills():
    return jsonify(skill_service.get_all_skills()), 200


@skill_bp.route("/user/skills", methods=["GET"])
def get_user_skills():
    user_id = get_current_user_id()
    return jsonify(skill_service.get_user_skills(user_id)), 200


@skill_bp.route("/user/skills", methods=["POST"])
def add_user_skills():
    user_id = get_current_user_id()
    data = request.get_json() or {}
    skill_ids = data.get("skills") or data.get("skill_ids") or []
    skill_service.add_user_skills(user_id, skill_ids)
    return jsonify(skill_service.get_user_skills(user_id)), 200

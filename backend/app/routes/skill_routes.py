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

@skill_bp.route("/user/skills", methods=["GET"])
def get_user_skills():
    user_id = get_current_user_id()
    user_skills_data = skill_service.get_user_skills(user_id)
    return jsonify(user_skills_data), 200
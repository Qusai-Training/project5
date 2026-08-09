from flask import Blueprint, request, jsonify
from app.services import course_service
from app.services.auth_service import decode_jwt
from app.errors import UnauthorizedError

course_bp = Blueprint("courses", __name__, url_prefix="/api")

def get_current_user_id():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedError("Authorization bearer token is missing")
    token = auth_header.split(" ")[1]
    payload = decode_jwt(token)
    return payload["user_id"]

# GET /api/courses[cite: 2]
@course_bp.route("/courses", methods=["GET"])
def get_courses():
    search = request.args.get("search", type=str)
    skill = request.args.get("skill", type=str)
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=6, type=int)

    courses_list = course_service.get_courses_list(search_term=search, skill_filter=skill, page=page, limit=limit)
    return jsonify({"courses": courses_list, "page": page, "limit": limit}), 200

# GET /api/courses/<course_id>[cite: 2]
@course_bp.route("/courses/<int:course_id>", methods=["GET"])
def get_course_detail(course_id):
    course = course_service.get_course_by_id(course_id)
    return jsonify(course), 200

# POST /api/recommend[cite: 2]
@course_bp.route("/recommend", methods=["POST"])
def get_recommendations():
    user_id = get_current_user_id()
    data = request.get_json() or {}
    limit = data.get("limit", 5)

    recommended = course_service.generate_recommendations(user_id, limit=limit)
    return jsonify({"recommendations": recommended, "limit": limit}), 200
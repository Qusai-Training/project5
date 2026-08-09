from flask import Blueprint, request, jsonify
from app.services import course_service
from app.services.auth_service import decode_jwt
from app.errors import UnauthorizedError

course_bp = Blueprint("courses", __name__, url_prefix="/api")


def get_current_user_id(required=False):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        if required:
            raise UnauthorizedError("Authorization bearer token is missing")
        return None

    token = auth_header.split(" ")[1]
    try:
        payload = decode_jwt(token)
    except UnauthorizedError:
        if required:
            raise
        return None
    return payload.get("user_id")


@course_bp.route("/courses", methods=["GET"])
def get_courses():
    search = request.args.get("q") or request.args.get("search")
    skill = request.args.get("skill") or request.args.get("skill_id")
    instructor = request.args.get("instructor")
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=6, type=int)
    sort_by = request.args.get("sort")
    user_id = get_current_user_id(required=False)

    result = course_service.get_courses_list(
        search_term=search,
        skill_filter=skill,
        instructor=instructor,
        sort_by=sort_by,
        page=page,
        limit=limit,
        user_id=user_id
    )
    return jsonify(result), 200


@course_bp.route("/courses/<int:course_id>", methods=["GET"])
def get_course_detail(course_id):
    user_id = get_current_user_id(required=False)
    course = course_service.get_course_by_id(course_id, user_id=user_id)
    return jsonify(course), 200


@course_bp.route("/courses", methods=["POST"])
def create_course():
    get_current_user_id(required=True)
    data = request.get_json() or {}

    course = course_service.create_course(
        title=data.get("title"),
        description=data.get("description"),
        instructor=data.get("instructor"),
        skill_requirements=data.get("skill_requirements")
    )
    return jsonify(course), 201


@course_bp.route("/courses/<int:course_id>/enroll", methods=["POST"])
def enroll_course(course_id):
    user_id = get_current_user_id(required=True)
    course = course_service.enroll_user(user_id, course_id)
    return jsonify({
        "message": "Successfully enrolled in course",
        "enrolled": True,
        "course": course
    }), 200


@course_bp.route("/recommend", methods=["POST"])
def get_recommendations():
    user_id = get_current_user_id(required=True)
    data = request.get_json() or {}
    limit = data.get("limit", 5)

    recommended = course_service.generate_recommendations(user_id, limit=limit)
    return jsonify(recommended), 200

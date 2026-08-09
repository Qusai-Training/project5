import hashlib
import math
from sqlalchemy import select, or_, func, insert
from app.db import engine
from app.models import courses, skills, user_skills, course_vectors, user_enrollments
from app.errors import NotFoundError, APIError

EMBEDDING_DIM = 64


def _token_hash(token):
    return int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)


def _embed_text(text, dim=EMBEDDING_DIM):
    vector = [0.0] * dim
    if not text:
        return ",".join(str(x) for x in vector)

    for token in str(text).split():
        h = _token_hash(token.lower())
        idx = h % dim
        sign = 1.0 if (h // dim) % 2 == 0 else -1.0
        vector[idx] += sign

    norm = math.sqrt(sum(x * x for x in vector)) or 1.0
    return ",".join(str(round(x / norm, 6)) for x in vector)


def _parse_embedding(value):
    if not value:
        return []
    try:
        cleaned = str(value).replace("[", "").replace("]", "")
        return [float(x) for x in cleaned.split(",") if x.strip()]
    except ValueError:
        return []


def _cosine_similarity(vec_a, vec_b):
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a)) or 1.0
    norm_b = math.sqrt(sum(b * b for b in vec_b)) or 1.0
    return dot / (norm_a * norm_b)


def _parse_skill_requirements(value):
    if not value:
        return []
    if isinstance(value, list):
        return [str(s).strip().lower() for s in value if str(s).strip()]
    return [s.strip().lower() for s in str(value).split(",") if s.strip()]


def _skill_match_score(user_skills_list, requirements):
    reqs = _parse_skill_requirements(requirements)
    if not reqs:
        return 0.5
    matches = [r for r in reqs if r in user_skills_list]
    return round(len(matches) / len(reqs), 3)


def _get_user_skill_names(user_id):
    query = select(skills.c.name).select_from(
        user_skills.join(skills, user_skills.c.skill_id == skills.c.id)
    ).where(user_skills.c.user_id == user_id)

    with engine.connect() as conn:
        return [row.name.lower() for row in conn.execute(query).fetchall()]


def _resolve_skill_name(skill_filter):
    if str(skill_filter).isdigit():
        with engine.connect() as conn:
            row = conn.execute(
                select(skills.c.name).where(skills.c.id == int(skill_filter))
            ).fetchone()
        if row:
            return row.name
    return skill_filter


def get_courses_list(search_term=None, skill_filter=None, instructor=None,
                     sort_by=None, page=1, limit=6, user_id=None):
    page = max(int(page or 1), 1)
    limit = min(max(int(limit or 6), 1), 100)
    offset = (page - 1) * limit

    filters = []
    if search_term:
        pattern = f"%{search_term}%"
        filters.append(
            or_(
                courses.c.title.ilike(pattern),
                courses.c.description.ilike(pattern)
            )
        )
    if skill_filter:
        skill_name = _resolve_skill_name(skill_filter)
        filters.append(courses.c.skill_requirements.ilike(f"%{skill_name}%"))
    if instructor:
        filters.append(courses.c.instructor.ilike(f"%{instructor}%"))

    count_query = select(func.count()).select_from(courses)
    query = select(courses)
    if filters:
        count_query = count_query.where(*filters)
        query = query.where(*filters)

    with engine.connect() as conn:
        total = conn.execute(count_query).scalar() or 0

        if sort_by == "title":
            query = query.order_by(courses.c.title.asc())
        elif sort_by == "relevance":
            pass
        else:
            query = query.order_by(courses.c.created_at.desc())

        rows = conn.execute(query.limit(limit).offset(offset)).fetchall()

    user_skill_names = _get_user_skill_names(user_id) if user_id else []

    courses_list = []
    for row in rows:
        item = {
            "id": row.id,
            "title": row.title,
            "instructor": row.instructor,
            "description": row.description,
            "skill_requirements": row.skill_requirements
        }
        if user_skill_names:
            item["match_score"] = _skill_match_score(user_skill_names, row.skill_requirements)
        courses_list.append(item)

    if sort_by == "relevance" and user_skill_names:
        courses_list.sort(key=lambda c: c.get("match_score", 0), reverse=True)

    return {
        "courses": courses_list,
        "page": page,
        "limit": limit,
        "total": total,
        "has_more": offset + len(courses_list) < total
    }


def _find_related_courses(conn, course, limit=3):
    vector_row = conn.execute(
        select(course_vectors.c.embedding_vector).where(course_vectors.c.course_id == course.id)
    ).fetchone()
    current_vec = _parse_embedding(vector_row[0]) if vector_row else []

    current_reqs = set(_parse_skill_requirements(course.skill_requirements))
    other_rows = conn.execute(select(courses).where(courses.c.id != course.id)).fetchall()

    scored = []
    for other in other_rows:
        if current_vec:
            other_vec_row = conn.execute(
                select(course_vectors.c.embedding_vector).where(course_vectors.c.course_id == other.id)
            ).fetchone()
            other_vec = _parse_embedding(other_vec_row[0]) if other_vec_row else []
            similarity = _cosine_similarity(current_vec, other_vec)
        else:
            overlap = current_reqs & set(_parse_skill_requirements(other.skill_requirements))
            denominator = max(len(current_reqs), 1)
            similarity = len(overlap) / denominator
        scored.append((similarity, other))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [
        {
            "id": other.id,
            "title": other.title,
            "instructor": other.instructor,
            "skill_requirements": other.skill_requirements,
            "similarity": round(similarity, 3)
        }
        for similarity, other in scored[:limit]
    ]


def get_course_by_id(course_id, user_id=None):
    with engine.connect() as conn:
        course = conn.execute(
            select(courses).where(courses.c.id == course_id)
        ).fetchone()
        if not course:
            raise NotFoundError(f"Course with ID {course_id} not found")

        related = _find_related_courses(conn, course)

        user_skill_names = _get_user_skill_names(user_id) if user_id else []

        enrolled = False
        if user_id:
            enrolled_row = conn.execute(
                select(user_enrollments.c.id).where(
                    user_enrollments.c.user_id == user_id,
                    user_enrollments.c.course_id == course_id
                )
            ).fetchone()
            enrolled = enrolled_row is not None

        return {
            "id": course.id,
            "title": course.title,
            "instructor": course.instructor,
            "description": course.description,
            "skill_requirements": course.skill_requirements,
            "created_at": course.created_at.isoformat() if course.created_at else None,
            "match_score": _skill_match_score(user_skill_names, course.skill_requirements) if user_skill_names else None,
            "enrolled": enrolled,
            "related_courses": related
        }


def create_course(title, description=None, instructor=None, skill_requirements=None):
    if not title or not str(title).strip():
        raise APIError("Course title is required", status_code=400)
    if not instructor or not str(instructor).strip():
        raise APIError("Course instructor is required", status_code=400)

    vector_text = f"{title} {description or ''} {skill_requirements or ''}"

    with engine.connect() as conn:
        result = conn.execute(
            insert(courses).values(
                title=str(title).strip(),
                description=description,
                instructor=str(instructor).strip(),
                skill_requirements=skill_requirements
            ).returning(courses.c.id)
        )
        course_id = result.fetchone()[0]

        conn.execute(
            insert(course_vectors).values(
                course_id=course_id,
                embedding_vector=_embed_text(vector_text, EMBEDDING_DIM)
            )
        )
        conn.commit()

    return get_course_by_id(course_id)


def enroll_user(user_id, course_id):
    with engine.connect() as conn:
        course = conn.execute(
            select(courses.c.id).where(courses.c.id == course_id)
        ).fetchone()
        if not course:
            raise NotFoundError(f"Course with ID {course_id} not found")

        existing = conn.execute(
            select(user_enrollments.c.id).where(
                user_enrollments.c.user_id == user_id,
                user_enrollments.c.course_id == course_id
            )
        ).fetchone()

        if not existing:
            conn.execute(
                insert(user_enrollments).values(user_id=user_id, course_id=course_id)
            )
            conn.commit()

    return get_course_by_id(course_id, user_id=user_id)


def get_enrolled_courses(user_id):
    query = select(courses).select_from(
        user_enrollments.join(courses, user_enrollments.c.course_id == courses.c.id)
    ).where(user_enrollments.c.user_id == user_id)

    with engine.connect() as conn:
        rows = conn.execute(query).fetchall()

    return [
        {
            "id": row.id,
            "title": row.title,
            "instructor": row.instructor,
            "description": row.description,
            "skill_requirements": row.skill_requirements
        }
        for row in rows
    ]


def generate_recommendations(user_id, limit=5):
    user_skill_names = _get_user_skill_names(user_id)
    user_embedding = _parse_embedding(
        _embed_text(" ".join(user_skill_names), EMBEDDING_DIM)
    ) if user_skill_names else []

    with engine.connect() as conn:
        all_courses = conn.execute(select(courses)).fetchall()
        vector_rows = conn.execute(
            select(course_vectors.c.course_id, course_vectors.c.embedding_vector)
        ).fetchall()
        vectors_by_course = {row.course_id: _parse_embedding(row.embedding_vector) for row in vector_rows}

        recommendations = []
        for course in all_courses:
            reqs = _parse_skill_requirements(course.skill_requirements)
            matches = [r for r in reqs if r in user_skill_names]

            text_score = _skill_match_score(user_skill_names, course.skill_requirements)

            course_vec = vectors_by_course.get(course.id, [])
            if user_embedding and course_vec:
                embedding_score = max(0.0, _cosine_similarity(user_embedding, course_vec))
            else:
                embedding_score = text_score

            match_score = round(text_score * 0.6 + embedding_score * 0.4, 3)

            explanation = (
                f"Matches {len(matches)} of your skills ({', '.join(matches)})."
                if matches
                else "Recommended based on related skill areas and course embeddings."
            )

            recommendations.append({
                "id": course.id,
                "title": course.title,
                "instructor": course.instructor,
                "description": course.description,
                "skill_requirements": course.skill_requirements,
                "match_score": match_score,
                "explanation": explanation
            })

    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    return recommendations[:limit]

from sqlalchemy import select, or_
from app.db import engine
from app.models import courses, skills, user_skills
from app.errors import NotFoundError

def get_courses_list(search_term=None, skill_filter=None, page=1, limit=6):
    offset = (page - 1) * limit
    query = select(courses)

    if search_term:
        query = query.where(
            or_(
                courses.c.title.ilike(f"%{search_term}%"),
                courses.c.description.ilike(f"%{search_term}%")
            )
        )

    if skill_filter:
        query = query.where(courses.c.skill_requirements.ilike(f"%{skill_filter}%"))

    query = query.limit(limit).offset(offset)

    with engine.connect() as conn:
        result = conn.execute(query).fetchall()
        return [
            {
                "id": r.id,
                "title": r.title,
                "instructor": r.instructor,
                "description": r.description,
                "skill_requirements": r.skill_requirements
            }
            for r in result
        ]

def get_course_by_id(course_id):
    query = select(courses).where(courses.c.id == course_id)
    with engine.connect() as conn:
        course = conn.execute(query).fetchone()
        if not course:
            raise NotFoundError(f"Course with ID {course_id} not found")
        
        return {
            "id": course.id,
            "title": course.title,
            "instructor": course.instructor,
            "description": course.description,
            "skill_requirements": course.skill_requirements,
            "created_at": course.created_at.isoformat() if course.created_at else None
        }

def generate_recommendations(user_id, limit=5):
    """Calculates course recommendations and match scores based on user skills."""
    # Fetch user skill names
    user_skills_query = select(skills.c.name).select_from(
        user_skills.join(skills, user_skills.c.skill_id == skills.c.id)
    ).where(user_skills.c.user_id == user_id)

    all_courses_query = select(courses)

    with engine.connect() as conn:
        u_skills = [row.name.lower() for row in conn.execute(user_skills_query).fetchall()]
        all_courses = conn.execute(all_courses_query).fetchall()

        recommendations = []
        for c in all_courses:
            reqs = [req.strip().lower() for req in (c.skill_requirements or "").split(",") if req.strip()]
            matches = [req for req in reqs if req in u_skills]
            
            # Calculate match percentage score
            match_score = int((len(matches) / max(len(reqs), 1)) * 100) if reqs else 50

            explanation = (
                f"Matches {len(matches)} of your registered skills ({', '.join(matches)})."
                if matches else "Recommended based on overall career pathways."
            )

            recommendations.append({
                "id": c.id,
                "title": c.title,
                "instructor": c.instructor,
                "description": c.description,
                "skill_requirements": c.skill_requirements,
                "match_score": max(match_score, 40),
                "explanation": explanation
            })

        # Sort by match_score descending
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        return recommendations[:limit]
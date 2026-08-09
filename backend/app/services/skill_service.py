from sqlalchemy import select
from app.db import engine
from app.models import skills, user_skills

def get_user_skills(user_id):
    # Core SQLAlchemy Join Statement
    query = select(
        skills.c.id,
        skills.c.name,
        skills.c.category,
        user_skills.c.proficiency,
        user_skills.c.is_new
    ).select_from(
        user_skills.join(skills, user_skills.c.skill_id == skills.c.id)
    ).where(user_skills.c.user_id == user_id)

    with engine.connect() as conn:
        result = conn.execute(query).fetchall()

        skills_list = []
        for row in result:
            skills_list.append({
                "id": row.id,
                "name": row.name,
                "category": row.category,
                "proficiency": row.proficiency,
                "is_new": row.is_new
            })

        return skills_list
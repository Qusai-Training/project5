from sqlalchemy import select, insert
from app.db import engine
from app.models import skills, user_skills


def get_all_skills():
    with engine.connect() as conn:
        rows = conn.execute(select(skills).order_by(skills.c.name)).fetchall()
        return [
            {
                "id": row.id,
                "name": row.name,
                "description": row.description or ""
            }
            for row in rows
        ]


def get_user_skills(user_id):
    query = select(
        skills.c.id,
        skills.c.name,
        skills.c.description,
        user_skills.c.proficiency_level
    ).select_from(
        user_skills.join(skills, user_skills.c.skill_id == skills.c.id)
    ).where(user_skills.c.user_id == user_id)

    with engine.connect() as conn:
        result = conn.execute(query).fetchall()
        return [
            {
                "id": row.id,
                "name": row.name,
                "description": row.description or "",
                "proficiency": row.proficiency_level or 0
            }
            for row in result
        ]


def add_user_skills(user_id, skill_ids):
    skill_ids = skill_ids or []
    with engine.connect() as conn:
        existing = {
            row[0]
            for row in conn.execute(
                select(user_skills.c.skill_id).where(user_skills.c.user_id == user_id)
            ).fetchall()
        }

        to_add = []
        for sid in skill_ids:
            try:
                sid = int(sid)
            except (TypeError, ValueError):
                continue
            if sid not in existing:
                to_add.append(sid)

        if to_add:
            conn.execute(insert(user_skills), [
                {"user_id": user_id, "skill_id": sid, "proficiency_level": 50}
                for sid in to_add
            ])
            conn.commit()

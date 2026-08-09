from sqlalchemy import select, insert
from app.db import engine
from app.models import skills

SEED_SKILLS = [
    {"name": "Python", "category": "Backend"},
    {"name": "PostgreSQL", "category": "Database"},
    {"name": "Flask & REST API", "category": "Backend"},
    {"name": "JavaScript", "category": "Frontend"},
    {"name": "Vector Databases", "category": "AI / ML"},
    {"name": "FastAPI", "category": "Backend"},
    {"name": "Machine Learning", "category": "AI / ML"},
    {"name": "Docker", "category": "DevOps"}
]

def seed():
    """Seeds standard skills catalog into PostgreSQL using Core queries."""
    with engine.connect() as conn:
        existing = conn.execute(select(skills)).fetchall()
        if existing:
            print("ℹ️ Skills table already contains data. Skipping seed.")
            return

        stmt = insert(skills).values(SEED_SKILLS)
        conn.execute(stmt)
        conn.commit()
        print("✅ Successfully seeded initial skills into PostgreSQL!")

if __name__ == "__main__":
    seed()
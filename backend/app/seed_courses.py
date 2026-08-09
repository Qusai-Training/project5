from sqlalchemy import select, insert
from app.db import engine
from app.models import courses

SEED_COURSES = [
    {
        "title": "Python for High-Performance Backend Systems",
        "instructor": "Dr. Sarah Jenkins",
        "description": "Master advanced Python features, async programming, REST architecture, and database integrations.",
        "skill_requirements": "Python, REST API"
    },
    {
        "title": "PostgreSQL Core Optimization & Schema Migrations",
        "instructor": "Alex Rivera",
        "description": "Learn deep SQL optimization, index management, transaction controls, and Alembic migration scripts.",
        "skill_requirements": "PostgreSQL, SQL"
    },
    {
        "title": "Building Web Applications with Vanilla JS & Modern CSS",
        "instructor": "Marcus Vance",
        "description": "Design dynamic responsive client applications using standard HTML, flexbox/grid CSS, and Fetch API.",
        "skill_requirements": "JavaScript, CSS, HTML"
    },
    {
        "title": "Vector Databases & AI Semantic Search Workflows",
        "instructor": "Elena Rostova",
        "description": "Understand embeddings, vector distance metrics, similarity queries, and modern AI stack pipelines.",
        "skill_requirements": "Vector Databases, AI / ML"
    },
    {
        "title": "FastAPI & Microservices Architecture",
        "instructor": "David Chen",
        "description": "Construct high-throughput API services using Pydantic models, async endpoints, and Docker deployment.",
        "skill_requirements": "FastAPI, Python, Docker"
    }
]

def seed():
    """Seeds default courses into the PostgreSQL database using Core queries."""
    with engine.connect() as conn:
        existing = conn.execute(select(courses)).fetchall()
        if existing:
            print("ℹ️ Courses table already contains data. Skipping seed.")
            return

        stmt = insert(courses).values(SEED_COURSES)
        conn.execute(stmt)
        conn.commit()
        print("✅ Successfully seeded initial courses into PostgreSQL!")

if __name__ == "__main__":
    seed()
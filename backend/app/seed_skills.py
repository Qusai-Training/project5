import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, insert
from app.db import engine
from app.models import skills

SEED_SKILLS = [
    {"name": "Python", "description": "High-level programming language used for backend, data science, and AI."},
    {"name": "PostgreSQL", "description": "Advanced open-source relational database management system."},
    {"name": "Flask & REST API", "description": "Lightweight Python web framework for building RESTful APIs."},
    {"name": "JavaScript", "description": "Programming language for client-side web applications."},
    {"name": "Vector Databases", "description": "Specialized databases for semantic search and AI embeddings."},
    {"name": "FastAPI", "description": "High-performance Python framework for building modern APIs."},
    {"name": "Machine Learning", "description": "Algorithms and statistical models that learn from data."},
    {"name": "Docker", "description": "Containerization platform for packaging and deploying applications."}
]


def seed():
    """Seeds standard skills catalog into PostgreSQL using Core queries."""
    with engine.connect() as conn:
        existing = conn.execute(select(skills)).fetchall()
        if existing:
            print("Skills table already contains data. Skipping seed.")
            return

        conn.execute(insert(skills), SEED_SKILLS)
        conn.commit()
        print("Successfully seeded initial skills into PostgreSQL!")


if __name__ == "__main__":
    seed()

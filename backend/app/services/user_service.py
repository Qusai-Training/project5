"""
Database Initialization Script for pgAdmin 4 Verification
Run: python init_db.py
"""
from sqlalchemy import select, insert
from app.db import engine, metadata
from app.models import users, skills, courses, course_vectors

def initialize_database():
    print("⏳ Creating PostgreSQL tables...")
    metadata.create_all(engine)
    print("✅ All tables created successfully!")

    with engine.connect() as conn:
        # Seed Skills if empty
        existing_skills = conn.execute(select(skills)).fetchall()
        if not existing_skills:
            conn.execute(insert(skills), [
                {"name": "Python", "description": "High-level programming language for backend and data science."},
                {"name": "PostgreSQL", "description": "Advanced open-source relational database management system."},
                {"name": "JavaScript", "description": "Programming language for client-side web applications."},
                {"name": "FastAPI", "description": "High-performance framework for building APIs with Python."},
                {"name": "Vector Databases", "description": "Specialized database systems for semantic search & AI embeddings."}
            ])
            print("🌱 Seeded initial Skills.")

        # Seed Courses if empty
        existing_courses = conn.execute(select(courses)).fetchall()
        if not existing_courses:
            conn.execute(insert(courses), [
                {
                    "title": "Python for High-Performance Backend Systems",
                    "instructor": "Dr. Sarah Jenkins",
                    "description": "Master advanced Python features, async programming, REST architecture, and database integrations.",
                    "skill_requirements": "Python, JavaScript"
                },
                {
                    "title": "PostgreSQL Core Optimization & Schema Migrations",
                    "instructor": "Alex Rivera",
                    "description": "Learn deep SQL optimization, index management, transaction controls, and Alembic migration scripts.",
                    "skill_requirements": "PostgreSQL, Python"
                },
                {
                    "title": "Vector Databases & AI Semantic Search Workflows",
                    "instructor": "Elena Rostova",
                    "description": "Understand embeddings, vector distance metrics, similarity queries, and modern AI stack pipelines.",
                    "skill_requirements": "Vector Databases, Python"
                }
            ])
            print("🌱 Seeded initial Courses.")

        conn.commit()
    print("🚀 Database readiness check complete! Check pgAdmin 4 to verify table structure.")

if __name__ == "__main__":
    initialize_database()
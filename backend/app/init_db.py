"""
Database Initialization Script for pgAdmin 4 Verification
Run: python -m app.init_db  (from backend/) or: python init_db.py  (from backend/app/)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, insert
from app.db import engine, metadata
from app.models import skills, courses, course_vectors
from app.services.course_service import _embed_text, EMBEDDING_DIM

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
        "skill_requirements": "PostgreSQL, Python"
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
        "skill_requirements": "Vector Databases, Machine Learning"
    },
    {
        "title": "FastAPI & Microservices Architecture",
        "instructor": "David Chen",
        "description": "Construct high-throughput API services using Pydantic models, async endpoints, and Docker deployment.",
        "skill_requirements": "FastAPI, Python, Docker"
    },
    {
        "title": "Data Science & Analytics with Python",
        "instructor": "Priya Natarajan",
        "description": "Practical data cleaning, analysis, and visualization workflows using pandas, numpy, and matplotlib.",
        "skill_requirements": "Python, Machine Learning"
    },
    {
        "title": "Flask API Design & Authentication Patterns",
        "instructor": "Jonas Weber",
        "description": "Build production-ready REST APIs with JWT auth, role-based access, and structured error handling in Flask.",
        "skill_requirements": "Flask & REST API, Python"
    },
    {
        "title": "Modern JavaScript: ES6+, Async Patterns & Fetch",
        "instructor": "Aisha Bello",
        "description": "Master modern JavaScript syntax, promises, async/await, and interacting with REST APIs from the browser.",
        "skill_requirements": "JavaScript, HTML"
    },
    {
        "title": "Docker & Containerized Deployment for Web Apps",
        "instructor": "Miguel Santos",
        "description": "Containerize web applications, manage multi-container setups, and deploy services reliably with Docker.",
        "skill_requirements": "Docker, FastAPI"
    },
    {
        "title": "Semantic Search & RAG with Vector Databases",
        "instructor": "Elena Rostova",
        "description": "Build retrieval-augmented generation pipelines using embeddings, vector stores, and hybrid search.",
        "skill_requirements": "Vector Databases, Machine Learning, Python"
    },
    {
        "title": "Machine Learning Foundations: From Data to Models",
        "instructor": "Dr. Sarah Jenkins",
        "description": "Core ML concepts: feature engineering, model selection, evaluation metrics, and bias handling.",
        "skill_requirements": "Python, Machine Learning"
    },
    {
        "title": "PostgreSQL Performance Tuning & Query Planning",
        "instructor": "Alex Rivera",
        "description": "Optimize slow queries with indexes, EXPLAIN analysis, connection pooling, and schema design best practices.",
        "skill_requirements": "PostgreSQL, SQL"
    },
    {
        "title": "Web Security Essentials for Backend Developers",
        "instructor": "Fatima Al-Sayed",
        "description": "Protect your APIs against injection, auth bypasses, and data leaks with secure coding practices.",
        "skill_requirements": "Flask & REST API, JavaScript"
    },
    {
        "title": "Building Single Page Applications with Vanilla JS",
        "instructor": "Marcus Vance",
        "description": "Architect client-side SPAs with routing, state management, and REST consumption using plain JavaScript.",
        "skill_requirements": "JavaScript, HTML, CSS"
    },
    {
        "title": "High-Performance Async Python & Concurrency",
        "instructor": "David Chen",
        "description": "Leverage asyncio, threading, and multiprocessing to build fast, concurrent Python services.",
        "skill_requirements": "Python, FastAPI"
    }
]


def initialize_database():
    print("Creating PostgreSQL tables...")
    metadata.create_all(engine)
    print("All tables created successfully!")

    with engine.connect() as conn:
        existing_skills = conn.execute(select(skills)).fetchall()
        if not existing_skills:
            conn.execute(insert(skills), SEED_SKILLS)
            print("Seeded initial Skills.")

        existing_courses = conn.execute(select(courses)).fetchall()
        if not existing_courses:
            conn.execute(insert(courses), SEED_COURSES)
            print("Seeded initial Courses.")

        existing_vectors = conn.execute(select(course_vectors)).fetchall()
        if not existing_vectors:
            course_rows = conn.execute(select(courses)).fetchall()
            conn.execute(insert(course_vectors), [
                {
                    "course_id": course.id,
                    "embedding_vector": _embed_text(
                        f"{course.title} {course.description} {course.skill_requirements}",
                        EMBEDDING_DIM
                    )
                }
                for course in course_rows
            ])
            print("Seeded Course embedding vectors.")

        conn.commit()

    print("Database readiness check complete! Check pgAdmin 4 to verify table structure.")


if __name__ == "__main__":
    initialize_database()

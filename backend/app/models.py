from sqlalchemy import Table, Column, Integer, String, Text, DateTime, ForeignKey, func
from app.db import metadata

# Users Table
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String(80), unique=True, nullable=False),
    Column("email", String(120), unique=True, nullable=False),
    Column("password_hash", String(255), nullable=False),
    Column("phone", String(30), nullable=True),
    Column("age", Integer, nullable=True),
    Column("major", String(100), nullable=True),
    Column("membership_status", String(20), server_default="active", nullable=False),
    Column("membership_expires_at", DateTime, nullable=True),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now())
)

# Skills Table
skills = Table(
    "skills",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), unique=True, nullable=False),
    Column("description", Text, nullable=True),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now())
)

# User_Skills Table[cite: 2]
user_skills = Table(
    "user_skills",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("skill_id", Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
    Column("proficiency_level", Integer, default=50),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now())
)

# Courses Table[cite: 2]
courses = Table(
    "courses",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String(200), nullable=False),
    Column("description", Text, nullable=True),
    Column("instructor", String(100), nullable=False),
    Column("skill_requirements", String(255), nullable=True),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now())
)

# Course_Vectors Table[cite: 2]
course_vectors = Table(
    "course_vectors",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("course_id", Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
    Column("embedding_vector", Text, nullable=True),  # Stores vector array or comma-separated embedding strings
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now())
)

# User_Enrollments Table
user_enrollments = Table(
    "user_enrollments",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("course_id", Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now())
)
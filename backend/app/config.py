import os

class Config:
    """Central configuration class loading from environment variables."""
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:0000@localhost:5432/project5"
    )
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
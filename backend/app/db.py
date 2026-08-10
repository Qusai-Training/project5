import os
from sqlalchemy import create_engine, MetaData

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:123456@localhost:5432/project5"
)

# Core Engine and Shared MetaData
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
metadata = MetaData()
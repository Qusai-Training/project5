import os
import datetime
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select, insert
from app.db import engine
from app.models import users, user_skills
from app.errors import APIError, UnauthorizedError

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")

def generate_jwt(user_id, username):
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_jwt(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token has expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid token")

def register_user(username, email, password, phone=None, age=None, major=None, skill_ids=None):
    query = select(users).where((users.c.username == username) | (users.c.email == email))
    
    with engine.connect() as conn:
        existing = conn.execute(query).fetchone()
        if existing:
            raise APIError("Username or email already exists", status_code=400)

        hashed_password = generate_password_hash(password)
        
        insert_stmt = insert(users).values(
            username=username,
            email=email,
            password_hash=hashed_password,
            phone=phone,
            age=age,
            major=major
        ).returning(users.c.id, users.c.username)

        result = conn.execute(insert_stmt)
        new_user = result.fetchone()

        # Insert user selected skills if provided
        if skill_ids and isinstance(skill_ids, list):
            skill_inserts = [
                {"user_id": new_user.id, "skill_id": sid, "proficiency_level": 70}
                for sid in skill_ids
            ]
            conn.execute(insert(user_skills), skill_inserts)

        conn.commit()

        token = generate_jwt(new_user.id, new_user.username)
        return {"token": token, "username": new_user.username, "user_id": new_user.id}

def authenticate_user(username, password):
    query = select(users).where(users.c.username == username)
    
    with engine.connect() as conn:
        user = conn.execute(query).fetchone()
        if not user or not check_password_hash(user.password_hash, password):
            raise UnauthorizedError("Invalid username or password")

        token = generate_jwt(user.id, user.username)
        return {"token": token, "username": user.username, "user_id": user.id}
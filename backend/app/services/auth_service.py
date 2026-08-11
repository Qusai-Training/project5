import os
import re
import datetime
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select, insert, or_, update
from app.db import engine
from app.models import users, user_skills
from app.errors import APIError, UnauthorizedError

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_registration(username, email, password, phone, age):
    if not username or not str(username).strip():
        raise APIError("Username is required", status_code=400)
    if not email or not EMAIL_REGEX.match(str(email).strip()):
        raise APIError("Please provide a valid email address (must contain @ and .)", status_code=400)
    if not password or len(str(password)) < 6:
        raise APIError("Password must be at least 6 characters long", status_code=400)
    if phone is not None and str(phone).strip() != "":
        phone_str = str(phone).strip()
        if not re.fullmatch(r"^\+962\d{9}$", phone_str):
            raise APIError("Phone number must start with +962 followed by exactly 9 digits", status_code=400)
    if age is not None and str(age).strip() != "":
        try:
            age_value = int(age)
        except (TypeError, ValueError):
            raise APIError("Age must be a number", status_code=400)
        if age_value < 0 or age_value > 120:
            raise APIError("Age must be between 0 and 120", status_code=400)


def generate_jwt(user_id, username):
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_jwt(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token has expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid token")


def _user_payload(row):
    return {
        "id": row.id,
        "username": row.username,
        "email": row.email
    }


def register_user(username, email, password, phone=None, age=None, major=None, skills=None):
    _validate_registration(username, email, password, phone, age)

    skills = skills or []
    query = select(users).where(
        or_(users.c.username == username, users.c.email == email)
    )

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
        ).returning(users.c.id, users.c.username, users.c.email)

        new_user = conn.execute(insert_stmt).fetchone()

        if skills:
            skill_inserts = []
            for sid in skills:
                try:
                    skill_inserts.append({
                        "user_id": new_user.id,
                        "skill_id": int(sid),
                        "proficiency_level": 50
                    })
                except (TypeError, ValueError):
                    continue
            if skill_inserts:
                conn.execute(insert(user_skills), skill_inserts)

        conn.commit()

        token = generate_jwt(new_user.id, new_user.username)
        return {"user": _user_payload(new_user), "token": token}


def authenticate_user(identifier, password):
    query = select(users).where(
        or_(users.c.username == identifier, users.c.email == identifier)
    )

    with engine.connect() as conn:
        user = conn.execute(query).fetchone()
        if not user or not check_password_hash(user.password_hash, password):
            raise UnauthorizedError("Invalid username/email or password")

        token = generate_jwt(user.id, user.username)
        return {"user": _user_payload(user), "token": token}


def change_password(user_id, old_password, new_password):
    if not old_password:
        raise APIError("Current password is required", status_code=400)
    if not new_password or len(str(new_password)) < 6:
        raise APIError("New password must be at least 6 characters long", status_code=400)
    if old_password == new_password:
        raise APIError("New password must be different from the current password", status_code=400)

    with engine.connect() as conn:
        user = conn.execute(select(users).where(users.c.id == user_id)).fetchone()
        if not user:
            raise UnauthorizedError("User not found")

        if not check_password_hash(user.password_hash, old_password):
            raise APIError("Current password is incorrect", status_code=400)

        conn.execute(
            update(users)
            .where(users.c.id == user_id)
            .values(password_hash=generate_password_hash(new_password))
        )
        conn.commit()

    return {"message": "Password changed successfully"}
import datetime
from sqlalchemy import select, update
from app.db import engine
from app.models import users
from app.errors import NotFoundError
from app.services.skill_service import get_user_skills
from app.services.course_service import get_enrolled_courses

MEMBERSHIP_DURATION_DAYS = 365


def _utcnow_naive():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


def _membership_payload(user):
    status = (user.membership_status or "active").lower()
    expires_at = user.membership_expires_at

    effective = status
    if status != "cancelled":
        if expires_at and expires_at < _utcnow_naive():
            effective = "expired"
        else:
            effective = "active"

    return {
        "status": effective,
        "expires_at": expires_at.isoformat() if expires_at else None
    }


def get_user_by_id(user_id):
    with engine.connect() as conn:
        user = conn.execute(select(users).where(users.c.id == user_id)).fetchone()

    if not user:
        raise NotFoundError(f"User with ID {user_id} not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "age": user.age,
        "major": user.major,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "membership": _membership_payload(user),
        "skills": get_user_skills(user_id),
        "enrolled_courses": get_enrolled_courses(user_id)
    }


def renew_membership(user_id):
    with engine.connect() as conn:
        user = conn.execute(select(users).where(users.c.id == user_id)).fetchone()
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        now = _utcnow_naive()
        expires_at = user.membership_expires_at
        if expires_at is None or expires_at < now:
            base = now
        else:
            base = expires_at
        new_expiry = base + datetime.timedelta(days=MEMBERSHIP_DURATION_DAYS)

        conn.execute(
            update(users)
            .where(users.c.id == user_id)
            .values(membership_status="active", membership_expires_at=new_expiry)
        )
        conn.commit()

    return {
        "message": "Membership renewed successfully",
        "membership": {
            "status": "active",
            "expires_at": new_expiry.isoformat()
        }
    }


def cancel_membership(user_id):
    with engine.connect() as conn:
        user = conn.execute(select(users).where(users.c.id == user_id)).fetchone()
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        conn.execute(
            update(users)
            .where(users.c.id == user_id)
            .values(membership_status="cancelled")
        )
        conn.commit()

    return {
        "message": "Membership cancelled",
        "membership": {
            "status": "cancelled",
            "expires_at": None
        }
    }

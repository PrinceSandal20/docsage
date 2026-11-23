from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models import User


def _normalize(email: str) -> str:
    return email.strip().lower()


def create_user(db: Session, email: str, password: str) -> User:
    user = User(email=_normalize(email), hashed_password=hash_password(password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("User already exists")
    db.refresh(user)
    return user


def get_user(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == _normalize(email)))
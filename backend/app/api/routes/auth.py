from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.Dtos.auth import UserCreate, UserLogin, Token
from app.services import user_store
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        user_store.create_user(db, user_data.email, user_data.password)
    except ValueError:
        raise HTTPException(status_code=400, detail="User already exists.")

    token = create_access_token({"sub": user_data.email})
    return Token(access_token=token)


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = user_store.get_user(db, credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    token = create_access_token({"sub": credentials.email})
    return Token(access_token=token)
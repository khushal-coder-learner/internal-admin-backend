from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token
)

def authenticate_user(
    db: Session,
    *,
    email: str,
    password: str,
):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )

    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        subject=str(user.id),
        role=user.role,
    )

    refresh_token = create_refresh_token(
        subject=str(user.id),
    )

    return access_token, refresh_token

def refresh_access_token(
    db: Session,
    *,
    refresh_token: str,
):
    user_id = decode_refresh_token(refresh_token)

    user = db.get(User, user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    access_token = create_access_token(
        subject=str(user.id),
        role=user.role,
    )

    return access_token

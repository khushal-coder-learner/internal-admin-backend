from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID

from app.models.user import User
from app.core.security import hash_password
from app.schemas.user import UserUpdate

def get_current_user_profile(*, current_user: User) -> User:
    return current_user

def list_users(db: Session, *, limit: int=50, offset: int = 0):
    return db.query(User).order_by(User.created_at.desc()).limit(limit).offset(offset).all()

def create_user(
    db: Session,
    *,
    email: str,
    password: str,
    role: str,
) -> User:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=email,
        hashed_password=hash_password(password),
        role=role,
        is_active=True,
    )

    db.add(user)

    return user

def update_user(
    db: Session,
    *,
    user_id: UUID,
    data: UserUpdate,
    current_user: User,
) -> User:
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # ❗ Prevent admin from locking themselves out
    if user.id == current_user.id and data.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate yourself",
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    return user

def deactivate_user(
    db: Session,
    *,
    user_id: UUID,
    current_user: User,
):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete yourself",
        )

    db.query(User).filter(User.id == user_id).update(
    {User.is_active: False}
    )

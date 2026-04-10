from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from uuid import UUID

from app.models.user import User
from app.core.security import hash_password
from app.schemas.user import UserUpdate

def get_current_user_profile(*, current_user: User) -> User:
    return current_user

def list_users(
    db: Session,
    *,
    search: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    query = db.query(User)

    # 🔍 Filtering
    if search:
        search = search.strip().lower()
        query = query.filter(
            func.lower(User.email).like(f"{search}%")
        )

    # 🎯 filters
    if role:
        query = query.filter(User.role == role)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # 🔽 sorting (whitelist is safer)
    ALLOWED_SORTS = {"email", "created_at", "role"}
    sort_col = getattr(User, sort_by) if sort_by in ALLOWED_SORTS else User.created_at
    query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())

    # 📊 Count
    total = query.count()

    # 📄 Pagination
    items = query.limit(limit).offset(offset).all()

    return {
        "items": items,
        "total": total,
    }

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

    db.flush()

    return user

def update_user(
    db: Session,
    *,
    user_id: UUID,
    data: UserUpdate,
) -> User:
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

   

    if data.role is not None:
        user.role = data.role

    return user

def update_user_status(
        db: Session, 
        user_id: UUID,
        is_active: bool,
        current_user: User,
        ) -> User:
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
     # ❗ Prevent admin from locking themselves out
    if user.id == current_user.id and is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate yourself",
        )

    user.is_active = is_active

    return user

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.user import User
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.services.user_service import (
    get_current_user_profile,
    list_users,
    create_user,
    update_user, 
    deactivate_user
)


router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
def read_me(
    current_user: User = Depends(get_current_user),
):
    return get_current_user_profile(current_user=current_user)

@router.get(
    "",
    response_model=list[UserResponse],
    dependencies=[Depends(require_role("admin"))],
)
def read_users(
    db: Session = Depends(get_db),
):
    return list_users(db)

@router.post(
    "",
    response_model=UserResponse,
    dependencies=[Depends(require_role("admin"))],
)
def create_user_endpoint(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    return create_user(
        db=db,
        email=payload.email,
        password=payload.password,
        role=payload.role,
    )

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_role("admin"))],
)
def update_user_endpoint(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_user(
        db=db,
        user_id=user_id,
        data=payload,
        current_user=current_user,
    )

@router.delete(
    "/{user_id}",
    status_code=204,
    dependencies=[Depends(require_role("admin"))],
)
def delete_user_endpoint(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deactivate_user(
        db=db,
        user_id=user_id,
        current_user=current_user,
    )

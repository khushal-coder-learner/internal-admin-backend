from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.dependencies import get_db, get_current_user, require_permission
from app.models.user import User
from app.core.permissions import Permission
from app.schemas.user import UserResponse, MultiUserResponse, UserCreate, UserUpdate, UserStatusUpdate
from app.services.user_service import (
    get_current_user_profile,
    list_users,
    create_user,
    update_user, 
    update_user_status
)


router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
def read_me(
    current_user: User = Depends(get_current_user),
):
    return get_current_user_profile(current_user=current_user)

@router.get(
    "",
    response_model=MultiUserResponse,
    dependencies=[Depends(require_permission(Permission.USER_VIEW))],
)
def read_users(
    db: Session = Depends(get_db),
    search: str = Query(),
    role: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    limit: int =  Query(le=100),
    offset: int = Query(),
    sort_by: str = Query(),
    sort_order: str = Query()
):
    return list_users(db, search=search, role=role, is_active=is_active, limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order)

@router.post(
    "",
    response_model=UserResponse,
    dependencies=[Depends(require_permission(Permission.USER_CREATE))],
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
    dependencies=[Depends(require_permission(Permission.USER_UPDATE))],
)
def update_user_endpoint(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
):
    return update_user(
        db=db,
        user_id=user_id,
        data=payload,
    )

@router.patch(
        "/{user_id}/status",
        response_model=UserResponse,
        dependencies=[Depends(require_permission(Permission.USER_STATUS_CHANGE))],
        )
def update_user_status_endpoint(
    user_id: UUID,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_user_status(db, user_id, payload.is_active, current_user)

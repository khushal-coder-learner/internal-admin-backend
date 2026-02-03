from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest
from app.services.auth_service import authenticate_user, refresh_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    access_token, refresh_token = authenticate_user(
        db=db,
        email=payload.email,
        password=payload.password,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

@router.post("/refresh", response_model=TokenResponse)
def refresh(
    payload: RefreshRequest,
    db: Session = Depends(get_db),
):
    access_token, refresh_token = refresh_access_token(
        db=db,
        refresh_token=payload.refresh_token,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

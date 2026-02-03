import hmac
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_refresh_token
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

    store_refresh_token(
        db,
        user_id=user.id,
        refresh_token=refresh_token,
    )

    db.commit()

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
    
    db_token = db.get(RefreshToken, user_id)

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Refresh token invalid"
        )
    
    now = datetime.now(UTC)

    if db_token.revoked_at:
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    if db_token.expires_at < now:
        revoke_refresh_token(db, user_id=user_id)
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")
    
    incoming_hash = hash_refresh_token(refresh_token)

    if not hmac.compare_digest(incoming_hash, db_token.token_hash):
        revoke_refresh_token(db, user_id=user_id)
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token reuse detected")

    access_token = create_access_token(
        subject=str(user.id),
        role=user.role,
    )    
    
    new_refresh = create_refresh_token(subject=str(user_id))

    store_refresh_token(
        db,
        user_id=user_id,
        refresh_token=new_refresh,
    )

    db.commit()

    return access_token, new_refresh

def store_refresh_token(
    db: Session,
    *,
    user_id,
    refresh_token: str,
    expires_in_days: int = 30,
):
    token_hash = hash_refresh_token(refresh_token)
    expires_at = datetime.now() + timedelta(days=expires_in_days)

    existing = db.get(RefreshToken, user_id)

    if existing:
        existing.token_hash = token_hash
        existing.expires_at = expires_at
        existing.revoked_at = None
    else:
        db.add(
            RefreshToken(
                user_id=user_id,
                token_hash=token_hash,
                expires_at=expires_at,
            )
        )

def revoke_refresh_token(db: Session, *, user_id):
    token = db.get(RefreshToken, user_id)
    if token:
        token.revoked_at = datetime.utcnow()

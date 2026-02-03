from datetime import datetime, timedelta
from typing import Any
from fastapi import HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext
import hmac
import uuid
import hashlib

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain password.
    """
    return pwd_context.hash(password)

def hash_refresh_token(token: str) -> str:
    return hmac.new(
        settings.secret_key.encode(),
        token.encode(),
        hashlib.sha256,
    ).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hash.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(subject: str, role: str) -> str:
    """
    Create a JWT access token.
    """
    payload = {
        "sub": subject,
        "role": role,
        "exp": datetime.now()
        + timedelta(minutes=settings.access_token_expire_minutes),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

def decode_token(token: str) -> dict[str, Any]:
    """
    Decode JWT token and return payload.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        raise ValueError("Invalid or expired token")

def create_refresh_token(subject: str) -> str:
    payload = {
        "sub": subject,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "exp": datetime.now()
        + timedelta(days=settings.refresh_token_expire_days),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

def decode_refresh_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        return payload["sub"]

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

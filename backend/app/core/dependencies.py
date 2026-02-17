from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.permissions import Permission, ROLE_PERMISSIONS
from app.db.session import get_db
from app.models.user import User
from app.core.security import decode_token
from redis.asyncio import Redis
from app.core.redis import get_redis_client
from app.core.rate_limit import enforce_rate_limit

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user = db.get(User, user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive or invalid user",
        )

    return user


def require_permission(permission: Permission):
    def dependency(current_user: User = Depends(get_current_user)):
        allowed = ROLE_PERMISSIONS.get(current_user.role, set())

        if permission not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return dependency


def get_redis() -> Redis:
    return get_redis_client()


def rate_limit_login(limit: int = 5, window: int = 60):
    async def dependency(
        request: Request,
        redis: Redis = Depends(get_redis_client),
    ):
        if request.client:

            ip = request.client.host
            key = f"rl:login:{ip}"

            await enforce_rate_limit(
                redis,
                key=key,
                limit=limit,
                window_seconds=window,
            )

    return dependency

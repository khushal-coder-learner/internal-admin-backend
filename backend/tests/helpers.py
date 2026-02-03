from app.models.user import User
from app.core.security import hash_password
import uuid

def create_test_user(db, role="admin"):
    user = User(
        email=f"{uuid.uuid4()}@example.com",
        hashed_password=hash_password("password123"),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def login_user(
    client,
    *,
    email: str,
    password: str,
):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()

    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "token_type": data.get("token_type", "bearer"),
    }

def auth_headers(access_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}"
    }

def refresh_tokens(client, refresh_token: str):
    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()

    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
    }

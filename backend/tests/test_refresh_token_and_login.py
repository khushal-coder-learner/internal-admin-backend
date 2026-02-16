from tests.helpers import create_test_user, login_user
from app.models.refresh_token import RefreshToken
from app.core.security import hash_refresh_token

def test_login_stores_refresh_token(db, client):
    # arrange
    user = create_test_user(db)

    # act
    response = client.post("/auth/login", json={
        "email": user.email,
        "password": "password123",
    })

    # assert
    assert response.status_code == 200
    refresh_token = response.json()["refresh_token"]

    db_token = db.get(RefreshToken, user.id)
    assert db_token is not None
    assert db_token.token_hash != refresh_token
    assert db_token.revoked_at is None

def test_refresh_rotates_token(db, client):

    user = create_test_user(db)

    tokens = login_user(client, email=user.email, password="password123")

    old_refresh = tokens["refresh_token"]

    refresh_response = client.post("/auth/refresh", json={
        "refresh_token": old_refresh
    })

    new_refresh = refresh_response.json()["refresh_token"]

    assert new_refresh != old_refresh

    db_token = db.get(RefreshToken, user.id)
    assert hash_refresh_token(new_refresh) == db_token.token_hash

def test_refresh_token_replay_detected(client,db):
    
    user = create_test_user(db)

    # login
    resp = client.post(
        "/auth/login",
        json={"email": user.email, "password": "password123"},
    )
    refresh = resp.json()["refresh_token"]

    # first refresh (OK)
    resp1 = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert resp1.status_code == 200

    # second refresh with SAME token (replay)
    resp2 = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert resp2.status_code == 401
    assert "replay" in resp2.json()["detail"].lower()

def test_refresh_token_rotation_still_valid(db, client):

    user = create_test_user(db)
  
    resp = client.post(
        "/auth/login",
        json={"email": user.email, "password": "password123"},
    )
    refresh = resp.json()["refresh_token"]

    # first refresh
    resp1 = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh},
    )
    new_refresh = resp1.json()["refresh_token"]

    # refresh with rotated token
    resp2 = client.post(
        "/auth/refresh",
        json={"refresh_token": new_refresh},
    )
    assert resp2.status_code == 200


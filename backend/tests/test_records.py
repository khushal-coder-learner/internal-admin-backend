from app.core.security import create_access_token
from app.models.user import User
import uuid

def create_test_user(db, role="admin"):
    user = User(
        email=f"{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user



def test_create_and_list_records(client, db):
    user = create_test_user(db)
    token = create_access_token(str(user.id), user.role)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Create record
    response = client.post(
        "/records",
        json={"title": "Test Record"},
        headers=headers,
    )
    assert response.status_code == 200
    record = response.json()
    assert record["title"] == "Test Record"

    # List records
    response = client.get("/records", headers=headers)
    assert response.status_code == 200
    records = response.json()
    assert any(r["title"] == "Test Record" for r in records)

def test_soft_delete_record(client, db):
    user = create_test_user(db, role="admin")
    token = create_access_token(str(user.id), user.role)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Create record
    response = client.post(
        "/records",
        json={"title": "To be deleted"},
        headers=headers,
    )
    record_id = response.json()["id"]

    # Soft delete record
    response = client.delete(
        f"/records/{record_id}",
        headers=headers,
    )
    assert response.status_code == 204

    # Record should not appear in list
    response = client.get("/records", headers=headers)
    records = response.json()
    assert all(r["id"] != record_id for r in records)

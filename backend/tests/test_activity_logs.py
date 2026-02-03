from app.core.security import create_access_token
from tests.helpers import create_test_user

def test_activity_log_created_on_record_create(client, db):
    user = create_test_user(db, role="admin")
    token = create_access_token(str(user.id), user.role)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Create record
    client.post(
        "/records",
        json={"title": "Logged Record"},
        headers=headers,
    )

    # Fetch activity logs
    response = client.get("/activity-logs", headers=headers)
    assert response.status_code == 200

    logs = response.json()
    assert len(logs) == 1
    assert logs[0]["action"] == "create"
    assert logs[0]["entity_type"] == "record"

def test_activity_log_created_on_soft_delete(client, db):
    user = create_test_user(db, role="admin")
    token = create_access_token(str(user.id), user.role)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Create record
    response = client.post(
        "/records",
        json={"title": "Delete log test"},
        headers=headers,
    )
    record_id = response.json()["id"]

    # Delete record
    client.delete(
        f"/records/{record_id}",
        headers=headers,
    )

    # Fetch logs
    response = client.get("/activity-logs", headers=headers)
    logs = response.json()

    assert any(log["action"] == "delete" for log in logs)

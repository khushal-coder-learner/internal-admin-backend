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

def test_staff_can_only_see_assigned_records(client, db):
    admin = create_test_user(db, role="admin")
    staff = create_test_user(db, role="staff")

    admin_token = create_access_token(str(admin.id), admin.role)
    staff_token = create_access_token(str(staff.id), staff.role)

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    staff_headers = {"Authorization": f"Bearer {staff_token}"}

    # Admin creates two records
    r1 = client.post(
        "/records",
        json={"title": "Assigned to staff"},
        headers=admin_headers,
    ).json()

    r2 = client.post(
        "/records",
        json={"title": "Unassigned"},
        headers=admin_headers,
    ).json()

    # Admin assigns only one record to staff
    client.post(
        f"/records/{r1['id']}/assign",
        json={"user_id": str(staff.id)},
        headers=admin_headers,
    )

    # Staff lists records
    response = client.get("/records", headers=staff_headers)
    records = response.json()
    assert any(r['title'] == "Assigned to staff" for r in records)
    assert any(r['title'] != "Unassigned" for r in records)

    assert records[0]["id"] == r1["id"]

def test_staff_cannot_update_unassigned_record(client, db):
    admin = create_test_user(db, role="admin")
    staff = create_test_user(db, role="staff")

    admin_token = create_access_token(str(admin.id), admin.role)
    staff_token = create_access_token(str(staff.id), staff.role)

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    staff_headers = {"Authorization": f"Bearer {staff_token}"}

    # Admin creates record (not assigned to staff)
    record = client.post(
        "/records",
        json={"title": "Protected Record"},
        headers=admin_headers,
    ).json()

    # Staff attempts to update
    response = client.patch(
        f"/records/{record['id']}",
        json={"title": "Illegal Update"},
        headers=staff_headers,
    )

    assert response.status_code == 403

def test_staff_cannot_assign_or_delete_record(client, db):
    admin = create_test_user(db, role="admin")
    staff = create_test_user(db, role="staff")

    admin_token = create_access_token(str(admin.id), admin.role)
    staff_token = create_access_token(str(staff.id), staff.role)

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    staff_headers = {"Authorization": f"Bearer {staff_token}"}

    record = client.post(
        "/records",
        json={"title": "Admin Only Actions"},
        headers=admin_headers,
    ).json()

    # Staff tries to assign
    assign_response = client.post(
        f"/records/{record['id']}/assign",
        json={"user_id": str(staff.id)},
        headers=staff_headers,
    )
    assert assign_response.status_code == 403

    # Staff tries to delete
    delete_response = client.delete(
        f"/records/{record['id']}",
        headers=staff_headers,
    )
    assert delete_response.status_code == 403

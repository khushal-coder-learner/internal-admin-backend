from app.core.security import create_access_token
from tests.helpers import create_test_user

def test_staff_can_access_me_endpoint(client, db):
    staff = create_test_user(db, role="staff")
    token = create_access_token(str(staff.id), staff.role)

    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/users/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(staff.id)
    assert data["role"] == "staff"

def test_staff_cannot_list_users(client, db):
    staff = create_test_user(db, role="staff")
    token = create_access_token(str(staff.id), staff.role)

    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/users", headers=headers)

    assert response.status_code == 403

def test_staff_cannot_create_user(client, db):
    staff = create_test_user(db, role="staff")
    token = create_access_token(str(staff.id), staff.role)

    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/users",
        json={
            "email": "hacker@example.com",
            "password": "hack123",
            "role": "admin",
        },
        headers=headers,
    )

    assert response.status_code == 403

def test_staff_cannot_update_or_delete_user(client, db):
    admin = create_test_user(db, role="admin")
    staff = create_test_user(db, role="staff")

    admin_token = create_access_token(str(admin.id), admin.role)
    staff_token = create_access_token(str(staff.id), staff.role)

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    staff_headers = {"Authorization": f"Bearer {staff_token}"}

    # Admin creates another user
    user = client.post(
        "/users",
        json={
            "email": "victim@example.com",
            "password": "victim123",
            "role": "staff",
        },
        headers=admin_headers,
    ).json()

    # Staff tries to update
    patch_response = client.patch(
        f"/users/{user['id']}",
        json={"role": "admin"},
        headers=staff_headers,
    )
    assert patch_response.status_code == 403

    # Staff tries to delete
    delete_response = client.delete(
        f"/users/{user['id']}",
        headers=staff_headers,
    )
    assert delete_response.status_code == 403

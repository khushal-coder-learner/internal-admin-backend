from app.models.user import User
from app.core.security import hash_password
import uuid
from app.models.job import Job, JobType
from app.services.job_service import process_job

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

def create_test_job(
    db,
    *,
    user=None,
    job_type=JobType.export,
    commit=True,
    **job_kwargs,
):
    if user is None:
        user = create_test_user(db)

    job = Job(
        type=job_type,
        user_id=user.id,
        **job_kwargs,
    )

    db.add(job)

    if commit:
        db.commit()
        db.refresh(job)

    return job

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

async def create_completed_export_job(db, redis, export_type="records"):
    """
    Creates and executes an export job, returning the completed job.
    """

    job = create_test_job(
        db,
        job_type=JobType.export,
        payload={"export_type": export_type},
    )

    await process_job(db=db, redis=redis, job_id=job.id)

    db.refresh(job)

    return job

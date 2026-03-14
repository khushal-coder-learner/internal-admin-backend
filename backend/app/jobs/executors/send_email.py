from app.services.email_service import send_email
from app.models.user import User
from sqlalchemy.orm import Session


async def execute_send_email(db: Session, redis, job):

    payload = job.payload
    user_id = payload.get("user_id")

    if not user_id:
        raise ValueError("send_email job requires a 'user_id' in the payload")

    user = db.get(User, user_id)
    if not user:
        raise ValueError(f"User not found for id: {user_id}")

    await send_email(
        to=user_id,
        subject=payload["subject"],
        body=payload["body"],
    )
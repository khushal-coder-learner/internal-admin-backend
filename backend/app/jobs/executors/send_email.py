from sqlalchemy.orm import Session
from app.models.user import User
from redis.asyncio import Redis


def execute_send_email(db: Session, job, redis: Redis | None = None):
    payload = job.payload

    user_id = payload["user_id"]
    subject = payload["subject"]
    body = payload["body"]

    user = db.get(User, user_id)

    if not user:
        return

    # Fake email sender for now
    print(f"Sending email to {user.email}")
    print(subject)
    print(body)
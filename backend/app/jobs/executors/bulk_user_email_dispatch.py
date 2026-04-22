from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from redis.asyncio import Redis

from app.models.user import User
from app.services.email_service import send_email


async def execute_bulk_user_email_dispatch(db: Session, redis: Redis, job):

    payload = job.payload or {}
    subject = payload["subject"]
    body = payload["body"]

    total_recipients = db.scalar(
        select(func.count()).select_from(User).where(User.is_active.is_(True))
    ) or 0

    job.payload = {
        **payload,
        "progress": 0 if total_recipients > 0 else 100,
        "total_recipients": total_recipients,
        "processed_recipients": 0,
        "sent_count": 0,
        "failed_count": 0,
        "first_errors": [],
    }
    flag_modified(job, "payload")
    db.commit()

    if total_recipients == 0:
        return

    PAGE_SIZE = 500
    COMMIT_EVERY = 50
    ERROR_CAP = 20

    processed_since_commit = 0
    offset = 0

    while True:
        user_ids = (
            db.execute(
                select(User.id)
                .where(User.is_active.is_(True))
                .order_by(User.created_at.asc(), User.id.asc())
                .offset(offset)
                .limit(PAGE_SIZE)
            )
            .scalars()
            .all()
        )

        if not user_ids:
            break

        offset += len(user_ids)

        for user_id in user_ids:
            try:
                await send_email(
                    to=str(user_id),
                    subject=subject,
                    body=body,
                )
                job.payload["sent_count"] += 1
            except Exception as e:
                job.payload["failed_count"] += 1
                first_errors = job.payload.get("first_errors") or []
                if isinstance(first_errors, list) and len(first_errors) < ERROR_CAP:
                    first_errors.append(
                        {"user_id": str(user_id), "error": str(e)}
                    )
                    job.payload["first_errors"] = first_errors

            job.payload["processed_recipients"] += 1
            processed = job.payload["processed_recipients"]
            job.payload["progress"] = min(
                100,
                int((processed / total_recipients) * 100),
            )

            processed_since_commit += 1
            if processed_since_commit >= COMMIT_EVERY:
                flag_modified(job, "payload")
                db.commit()
                processed_since_commit = 0

    job.payload["progress"] = 100
    flag_modified(job, "payload")
    db.commit()

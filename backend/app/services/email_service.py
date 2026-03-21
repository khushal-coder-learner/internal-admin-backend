from app.core.logging import get_logger


logger = get_logger(__name__)


async def send_email(to: str, subject: str, body: str):
    logger.info(
        "Sending email placeholder invoked",
        extra={
            "email_to": to,
            "email_subject": subject,
            "email_body_length": len(body),
        },
    )

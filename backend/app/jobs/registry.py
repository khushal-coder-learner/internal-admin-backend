from app.jobs.executors.export import execute_export
from app.jobs.executors.send_email import execute_send_email
from app.jobs.executors.bulk_user_email_dispatch import execute_bulk_user_email_dispatch

from app.models.job import JobType


JOB_REGISTRY = {
    JobType.export: execute_export,
    JobType.send_email: execute_send_email,
    JobType.bulk_user_email_dispatch: execute_bulk_user_email_dispatch,
}
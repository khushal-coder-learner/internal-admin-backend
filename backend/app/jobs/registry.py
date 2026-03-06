from app.jobs.executors.export_executor import execute_export
from app.jobs.types import JobType

JOB_REGISTRY = {
    JobType.export: execute_export
}
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from logging.handlers import RotatingFileHandler

from tests.helpers import create_test_job
from app.core.logging import (
    _LOGGING_HANDLER_MARKER,
    _LOGGING_CONFIGURED_FLAG,
    configure_logging,
)
from app.jobs.executors.cleanup_exports import execute_cleanup_exports
from app.main import app
from app.models.job import Job, JobStatus, JobType
from app.services.job_service import process_job, recover_stuck_jobs


def _read_log_events(log_path: Path) -> list[dict]:
    if not log_path.exists():
        return []

    events = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def _find_event(events: list[dict], message: str, **expected_fields):
    for event in events:
        if event.get("message") != message:
            continue
        if all(event.get(key) == value for key, value in expected_fields.items()):
            return event
    raise AssertionError(f"Could not find log event '{message}' with {expected_fields}")


@pytest.fixture
def log_dir():
    path = Path("tests/.tmp") / f"logs-{uuid4()}"
    path.mkdir(parents=True, exist_ok=True)
    yield path
    root_logger = logging.getLogger()
    handlers = [
        handler
        for handler in root_logger.handlers
        if getattr(handler, _LOGGING_HANDLER_MARKER, False)
    ]
    for handler in handlers:
        root_logger.removeHandler(handler)
        handler.close()
    setattr(root_logger, _LOGGING_CONFIGURED_FLAG, False)
    for child in path.iterdir():
        if child.is_file():
            child.unlink()
    path.rmdir()


def test_configure_logging_is_idempotent_and_uses_rotating_file(log_dir):
    configure_logging(
        service="api",
        log_dir=str(log_dir),
        log_file="app.log",
        log_max_bytes=1024,
        log_backup_count=3,
        force=True,
    )
    configure_logging(
        service="api",
        log_dir=str(log_dir),
        log_file="app.log",
        log_max_bytes=1024,
        log_backup_count=3,
    )

    root_logger = logging.getLogger()
    internal_handlers = [
        handler
        for handler in root_logger.handlers
        if getattr(handler, _LOGGING_HANDLER_MARKER, False)
    ]

    assert len(internal_handlers) == 2

    file_handler = next(
        handler for handler in internal_handlers if isinstance(handler, RotatingFileHandler)
    )
    assert Path(file_handler.baseFilename).resolve() == (log_dir / "app.log").resolve()

    record = logging.makeLogRecord(
        {
            "name": "test.logger",
            "levelno": logging.INFO,
            "levelname": "INFO",
            "msg": "hello",
        }
    )
    for log_filter in file_handler.filters:
        log_filter.filter(record)

    event = json.loads(file_handler.format(record))
    assert event["service"] == "api"


def test_request_logging_records_duration_and_metadata(client, log_dir):
    log_path = log_dir / "app.log"
    configure_logging(
        service="api",
        log_dir=str(log_dir),
        log_file="app.log",
        force=True,
    )

    response = client.get("/health")

    assert response.status_code == 200

    events = _read_log_events(log_path)
    request_event = _find_event(events, "Request completed", path="/health")

    assert request_event["service"] == "api"
    assert request_event["method"] == "GET"
    assert request_event["status_code"] == 200
    assert isinstance(request_event["duration_ms"], (int, float))
    assert request_event["duration_ms"] >= 0
    assert request_event["request_id"]
    assert "authorization" not in request_event
    assert "body" not in request_event
    assert "headers" not in request_event


def test_request_failure_logging_records_exception(log_dir):
    log_path = log_dir / "app.log"
    configure_logging(
        service="api",
        log_dir=str(log_dir),
        log_file="app.log",
        force=True,
    )

    if not any(route.path == "/_test/logging-error" for route in app.routes):
        @app.get("/_test/logging-error")
        def logging_error():
            raise RuntimeError("boom")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/_test/logging-error")

    assert response.status_code == 500

    events = _read_log_events(log_path)
    error_event = _find_event(events, "Request failed", path="/_test/logging-error")

    assert error_event["service"] == "api"
    assert error_event["method"] == "GET"
    assert isinstance(error_event["duration_ms"], (int, float))
    assert "exception" in error_event


@pytest.mark.asyncio
async def test_job_failure_logs_job_id_and_retry_state(db, test_redis, monkeypatch, log_dir):
    log_path = log_dir / "worker.log"
    configure_logging(
        service="worker",
        log_dir=str(log_dir),
        log_file="worker.log",
        force=True,
    )

    job = create_test_job(
        db,
        job_type=JobType.export,
        status=JobStatus.pending,
        attempts=0,
        max_attempts=3,
        payload={"export_type": "records"},
    )

    def fake_generate(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "app.jobs.executors.export.EXPORT_GENERATORS",
        {"records": fake_generate},
    )

    await process_job(db=db, job_id=job.id, redis=test_redis)

    events = _read_log_events(log_path)
    failure_event = _find_event(events, "Job processing failed", job_id=str(job.id))
    retry_event = _find_event(events, "Job retry state updated", job_id=str(job.id))

    assert failure_event["service"] == "worker"
    assert failure_event["job_type"] == JobType.export.value
    assert "exception" in failure_event
    assert retry_event["job_status"] == JobStatus.pending.value


@pytest.mark.asyncio
async def test_recover_stuck_job_and_cleanup_logs_include_worker_context(db, test_redis, log_dir):
    log_path = log_dir / "worker.log"
    configure_logging(
        service="worker",
        log_dir=str(log_dir),
        log_file="worker.log",
        force=True,
    )

    stuck_job = create_test_job(
        db,
        job_type=JobType.export,
        status=JobStatus.processing,
        attempts=1,
        max_attempts=3,
        processing_started_at=datetime.now() - timedelta(seconds=600),
        payload={"export_type": "records"},
        commit=False,
    )
    cleanup_job = create_test_job(
        db,
        job_type=JobType.export,
        status=JobStatus.completed,
        payload={},
        updated_at=datetime.now() - timedelta(seconds=700),
        commit=False,
    )
    db.commit()
    cleanup_job_id = str(cleanup_job.id)

    await test_redis.lpush("queue:processing", stuck_job.id)

    await recover_stuck_jobs(db, test_redis)
    await execute_cleanup_exports(db=db, redis=test_redis, job=None)

    events = _read_log_events(log_path)
    recovery_event = _find_event(events, "Recovering stuck job", job_id=str(stuck_job.id))
    requeue_event = _find_event(events, "Requeued recovered job", job_id=str(stuck_job.id))
    cleanup_event = _find_event(
        events,
        "Skipping export cleanup because file path is missing",
        job_id=cleanup_job_id,
    )

    assert recovery_event["service"] == "worker"
    assert requeue_event["service"] == "worker"
    assert cleanup_event["service"] == "worker"

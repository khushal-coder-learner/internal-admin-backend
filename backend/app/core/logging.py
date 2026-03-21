import json
import logging
import sys
from datetime import date, datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, MutableMapping

from app.core.config import settings


_LOGGING_HANDLER_MARKER = "_internal_admin_logging_handler"
_LOGGING_CONFIGURED_FLAG = "_internal_admin_logging_configured"
_LOG_RECORD_DEFAULTS = {
    "service": None,
    "job_id": None,
    "request_id": None,
    "duration_ms": None,
    "client_ip": None,
    "method": None,
    "path": None,
    "status_code": None,
}
_RESERVED_LOG_RECORD_FIELDS = set(logging.makeLogRecord({}).__dict__.keys())


def _json_default(value: Any) -> str:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


class ContextAdapter(logging.LoggerAdapter):
    def process(self, msg: str, kwargs: MutableMapping[str, Any]) -> tuple[str, MutableMapping[str, Any]]:
        extra = dict(self.extra) # type: ignore
        provided_extra = kwargs.get("extra")
        if provided_extra:
            extra.update(provided_extra)
        kwargs["extra"] = extra
        return msg, kwargs


class DefaultContextFilter(logging.Filter):
    def __init__(self, service: str):
        super().__init__()
        self.service = service

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "service") or getattr(record, "service") is None:
            setattr(record, "service", self.service)

        for field, default_value in _LOG_RECORD_DEFAULTS.items():
            if not hasattr(record, field):
                setattr(record, field, default_value)

        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": getattr(record, "service", None),
        }

        for field in (
            "job_id",
            "request_id",
            "duration_ms",
            "client_ip",
            "method",
            "path",
            "status_code",
        ):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value

        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _RESERVED_LOG_RECORD_FIELDS and key not in _LOG_RECORD_DEFAULTS
        }
        if extras:
            payload.update(extras)

        if record.exc_info:
            exc_type = record.exc_info[0].__name__ if record.exc_info[0] else None
            exc_message = str(record.exc_info[1]) if record.exc_info[1] else None

            payload["error_type"] = exc_type
            payload["error_message"] = exc_message
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=_json_default, ensure_ascii=True)


def _mark_handler(handler: logging.Handler) -> logging.Handler:
    setattr(handler, _LOGGING_HANDLER_MARKER, True)
    return handler


def _remove_internal_handlers(logger: logging.Logger) -> None:
    handlers_to_remove = [
        handler
        for handler in logger.handlers
        if getattr(handler, _LOGGING_HANDLER_MARKER, False)
    ]

    for handler in handlers_to_remove:
        logger.removeHandler(handler)
        handler.close()


def _build_handler(
    *,
    handler: logging.Handler,
    formatter: logging.Formatter,
    service: str,
) -> logging.Handler:
    handler.setFormatter(formatter)
    handler.addFilter(DefaultContextFilter(service))
    return _mark_handler(handler)


def _configure_uvicorn_loggers() -> None:
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        logger.propagate = True


def configure_logging(
    *,
    service: str,
    log_level: str | None = None,
    log_dir: str | None = None,
    log_file: str | None = None,
    log_max_bytes: int | None = None,
    log_backup_count: int | None = None,
    force: bool = False,
) -> logging.Logger:
    root_logger = logging.getLogger()

    if force:
        _remove_internal_handlers(root_logger)
        setattr(root_logger, _LOGGING_CONFIGURED_FLAG, False)

    if getattr(root_logger, _LOGGING_CONFIGURED_FLAG, False):
        root_logger.setLevel((log_level or settings.log_level).upper())
        return root_logger

    level_name = (log_level or settings.log_level).upper()
    resolved_log_dir = Path(log_dir or settings.log_dir)
    resolved_log_dir.mkdir(parents=True, exist_ok=True)
    resolved_log_file = resolved_log_dir / (log_file or settings.log_file)
    formatter = JsonFormatter()

    stdout_handler = _build_handler(
        handler=logging.StreamHandler(sys.stdout),
        formatter=formatter,
        service=service,
    )
    file_handler = _build_handler(
        handler=RotatingFileHandler(
            resolved_log_file,
            maxBytes=log_max_bytes or settings.log_max_bytes,
            backupCount=log_backup_count or settings.log_backup_count,
            encoding="utf-8",
        ),
        formatter=formatter,
        service=service,
    )

    root_logger.setLevel(level_name)
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(file_handler)
    setattr(root_logger, _LOGGING_CONFIGURED_FLAG, True)

    _configure_uvicorn_loggers()

    return root_logger


def get_logger(name: str, **context: Any) -> logging.Logger | ContextAdapter:
    logger = logging.getLogger(name)
    if context:
        return ContextAdapter(logger, context)
    return logger

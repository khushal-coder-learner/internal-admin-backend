"""FastAPI Application Entrypoint"""

from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import records, activity_logs, auth, users, health
from app.api import jobs
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.redis import close_redis, init_redis


configure_logging(service="api")
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.env == "production":
        logger.info("Starting API application")
    else:
        logger.debug("Starting API application")
    await init_redis()
    yield
    if settings.env == "production":
        logger.info("Shutting downn API application")
    else:
        logger.debug("Shutting down API application")
    await close_redis()


app = FastAPI(
    title="Internal Admin Backend",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid4())
    start_time = perf_counter()
    client_ip = request.client.host if request.client else None

    try:
        response = await call_next(request)
        if response.status_code in (401, 403):
            logger.warning(
                "Unauthorized access attempt",
                extra={
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method,
                    "client_ip": client_ip,
                    "status_code": response.status_code,
                }
            )
    except Exception:
        duration_ms = round((perf_counter() - start_time) * 1000, 2)
        logger.error(
            "Request failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": client_ip,
                "duration_ms": duration_ms,
            },
            exc_info=True
        )
        raise

    duration_ms = round((perf_counter() - start_time) * 1000, 2)
    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "client_ip": client_ip,
            "duration_ms": duration_ms,
        },
    )
    return response


@app.get("/")
def home():
    return {"message": "Hello, It's an internal admin backend system."}


@app.get("/health")
def health_check():
    return {"status": "ok"}

# Include routers
app.include_router(records.router)
app.include_router(activity_logs.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(health.router)
app.include_router(jobs.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

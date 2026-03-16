"""FastAPI Application Entrypoint"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.api import records, activity_logs, auth, users, health
from app.core.redis import init_redis, close_redis
from app.core.config import settings
from app.api import jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(">>> INIT REDIS CALLED")

    await init_redis()
    yield
    # Shutdown
    print(">>> CLOSE REDIS CALLED")
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

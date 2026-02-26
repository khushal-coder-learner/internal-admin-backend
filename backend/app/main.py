"""FastAPI Application Entrypoint"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import records, activity_logs, auth, users, health, exports
from app.core.redis import init_redis, close_redis


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
app.include_router(exports.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

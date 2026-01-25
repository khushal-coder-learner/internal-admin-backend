"""FastAPI Application Entrypoint"""

from fastapi import FastAPI
from app.api import records, activity_logs, auth, users

app = FastAPI(
    title="Internal Admin Backend",
    version="0.1.0",
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

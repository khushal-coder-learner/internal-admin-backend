import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from pathlib import Path
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from redis.asyncio import Redis
from app.core.dependencies import get_redis

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings

TEST_DATABASE_URL = settings.test_database_url

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
        
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def override_get_db(db):
    def _get_db_override():
        yield db

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_redis():
    redis = Redis.from_url(
        settings.test_redis_url,
        decode_responses=True,
    )
    await redis.flushdb()
    yield redis
    await redis.flushdb()
    await redis.aclose()

@pytest.fixture(autouse=True)
def override_redis(test_redis):
    async def _get_redis_override():
        return test_redis

    app.dependency_overrides[get_redis] = _get_redis_override
    yield
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_email_service(monkeypatch):

    async def fake_send_email(*args, **kwargs):
        return

    monkeypatch.setattr(
        "app.services.email_service.send_email",
        fake_send_email,
    )

@pytest.fixture(autouse=True)
def export_dir(monkeypatch):
    export_path = Path("tests/.tmp") / f"exports-{uuid4()}"
    export_path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("EXPORT_DIR", str(export_path))
    yield export_path
    for path in export_path.iterdir():
        if path.is_file():
            path.unlink()
    export_path.rmdir()

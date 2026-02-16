import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from redis.asyncio import Redis

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings

TEST_DATABASE_URL = settings.test_database_url

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

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

@pytest_asyncio.fixture(autouse=True)
async def clear_redis():
    redis = Redis.from_url(
        "redis://localhost:6380/0",
        decode_responses=True,
    )
    await redis.flushdb()
    yield
    await redis.flushdb()
    await redis.aclose()


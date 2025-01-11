import asyncio
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
import httpx

from app.main import app
from app.core.config import settings
from app.core.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create test database engine
test_engine = create_engine(settings.get_database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_app():
    """Create a fresh app instance for each test."""
    # Create a new FastAPI app for testing
    test_app = FastAPI()
    
    # Copy routes from main app
    test_app.router = app.router
    
    async with LifespanManager(test_app):
        yield test_app

@pytest.fixture
async def async_client(test_app: FastAPI) -> AsyncClient:
    """Create an async HTTP client for testing."""
    async with AsyncClient(
        transport=httpx.ASGITransport(app=test_app),
        base_url="http://test",
        headers={"Content-Type": "application/json"}
    ) as client:
        yield client

@pytest.fixture
def test_settings():
    """Return test settings."""
    return settings

@pytest.fixture(autouse=True)
def clear_database():
    """Clear database before each test."""
    # Create test database engine
    engine = create_engine(settings.get_database_url)
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield 
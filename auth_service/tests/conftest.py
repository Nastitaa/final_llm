import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.db.base import Base
from app.main import app
from app.api import deps

@pytest.fixture(scope="function")
async def db_session():
    """In-memory база данных для каждого теста"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
    await engine.dispose()

@pytest.fixture
async def client(db_session):
    """HTTP клиент с переопределённой зависимостью get_db"""
    # Подменяем реальную сессию на тестовую
    async def override_get_db():
        yield db_session

    app.dependency_overrides[deps.get_db] = override_get_db

    from httpx import AsyncClient, ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    # Очищаем переопределения после теста
    app.dependency_overrides.clear()
import pytest
from fakeredis import aioredis
from app.infra.redis import get_redis

@pytest.fixture
async def fake_redis():
    redis = aioredis.FakeRedis(decode_responses=True)
    # Патчим get_redis в модуле handlers
    import app.bot.handlers
    original = app.bot.handlers.get_redis
    async def fake_get_redis():
        return redis
    app.bot.handlers.get_redis = fake_get_redis
    yield redis
    app.bot.handlers.get_redis = original
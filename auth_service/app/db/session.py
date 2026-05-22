from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{settings.sqlite_path}"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
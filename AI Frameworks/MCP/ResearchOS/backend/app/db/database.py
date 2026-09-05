import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from backend.app.core.config import settings
from backend.app.core.logging import logger

Base = declarative_base()

os.makedirs("data", exist_ok=True)
# Default to SQLite for immediate out-of-the-box local developer experience
# Switch to PostgreSQL when DATABASE_URL is reachable
try:
    engine = create_async_engine(settings.DATABASE_FALLBACK_SQLITE, echo=False)
except Exception:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

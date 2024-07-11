from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create the async engine
engine = create_async_engine(settings.postgres_dsn, echo=settings.ENVIRONMENT == 'local')

# Create the async session
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None, None]:
    """Get a database session"""
    async with async_session() as session:
        yield session

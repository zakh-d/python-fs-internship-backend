from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

from .models import Base

# Create the async engine
engine = create_async_engine(settings.postgres_dsn, echo=settings.ENVIRONMENT == 'local')

# Create the async session
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Initialize the database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Get a database session"""
    async with async_session() as session:
        yield session

"""
Beautelligence Video Pipeline - Database Configuration

SQLAlchemy async engine and session management.
Supports both SQLite (development) and PostgreSQL (production).
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config.settings import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


def _create_engine():
    """Create async engine with appropriate settings for the database type."""
    url = settings.database_url

    # SQLite needs different settings than PostgreSQL
    if "sqlite" in url:
        return create_async_engine(
            url,
            echo=settings.app_debug,
            connect_args={"check_same_thread": False},
        )
    else:
        # PostgreSQL with connection pooling
        return create_async_engine(
            url,
            pool_size=settings.database_pool_size,
            pool_pre_ping=True,
            echo=settings.app_debug,
        )


# Create async engine
engine = _create_engine()

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session.

    Usage:
        async with get_session() as session:
            # Use session here
            await session.execute(...)
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """Drop all database tables (use with caution!)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# db\session.py
from __future__ import annotations
from typing import Generator, AsyncGenerator
from contextlib import contextmanager, asynccontextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import SYNC_URL, ASYNC_URL

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


# --- sync ---
sync_engine = create_engine(
    SYNC_URL,
    pool_pre_ping=True,
    pool_size=10,        # минимально: число потоков + запас
    max_overflow=20,     # можно брать до 20 доп. соединений
    pool_timeout=30,     # ожидание свободного коннекта
)
SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False, class_=Session)

@contextmanager
def get_sync_session() -> Generator[Session, None, None]:
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# --- async ---
async_engine = create_async_engine(
    ASYNC_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)

@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронный контекст для ручного управления commit/rollback."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
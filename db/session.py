# db/session.py
from __future__ import annotations
from typing import Generator, AsyncGenerator
from contextlib import contextmanager, asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config import SYNC_URL, ASYNC_URL

# --- Sync engine / sessionmaker ---
sync_engine = create_engine(
    SYNC_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    future=True,
)
SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False, class_=Session)

# --- Async engine / sessionmaker ---
async_engine = create_async_engine(
    ASYNC_URL,
    pool_pre_ping=True,
    # pool_size/max_overflow работают с драйверами, где используется QueuePool;
    # для aiosqlite — игнорируются, для asyncpg — применимы.
)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)


# -------- Sync helpers --------
@contextmanager
def get_sync_session() -> Generator[Session, None, None]:
    """
    Просто сессия без автокоммита.
    Управляй транзакцией сам: session.begin()/commit()/rollback().
    """
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_sync_tx() -> Generator[Session, None, None]:
    """
    Сессия с АВТО транзакцией:
    - begin до yield
    - commit после yield
    - rollback при ошибке
    """
    with get_sync_session() as db:
        trans = db.begin()
        try:
            yield db
            trans.commit()
        except Exception:
            trans.rollback()
            raise


# -------- Async helpers --------
@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Просто async-сессия без автокоммита.
    Управляй транзакцией сам: await session.commit()/rollback().
    """
    async with AsyncSessionLocal() as session:
        yield session  # AsyncSession закрывается автоматически

@asynccontextmanager
async def get_async_tx() -> AsyncGenerator[AsyncSession, None]:
    """
    Async-сессия с АВТО транзакцией (session.begin()).
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session

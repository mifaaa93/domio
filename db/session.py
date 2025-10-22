# db\session.py
from __future__ import annotations
from typing import Generator, AsyncGenerator
from contextlib import contextmanager, asynccontextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import SYNC_URL, ASYNC_URL
import threading
import weakref

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# --- глобальный кэш движков (по thread_id) ---
_thread_engines = weakref.WeakValueDictionary()

def get_sessionmaker_for_current_thread() -> async_sessionmaker[AsyncSession]:
    """
    Возвращает sessionmaker, уникальный для каждого потока.
    Если движок ещё не создан — создаёт новый и сохраняет.
    """
    thread_id = threading.get_ident()
    if thread_id not in _thread_engines:
        engine = create_async_engine(
            ASYNC_URL,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
        SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
        _thread_engines[thread_id] = SessionLocal
    return _thread_engines[thread_id]

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

@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронный контекст для ручного управления commit/rollback."""
    AsyncSessionLocal = get_sessionmaker_for_current_thread()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
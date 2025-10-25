# app/deps.py
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_async_session

async def db_session_dep() -> AsyncIterator[AsyncSession]:
    async with get_async_session() as session:
        yield session

# вариант с автокоммитом при успехе
async def db_session_autocommit_dep() -> AsyncIterator[AsyncSession]:
    async with get_async_session() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise

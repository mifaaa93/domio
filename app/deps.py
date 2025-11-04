# app/deps.py
from typing import AsyncIterator, Annotated, Any
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_async_session
from payu.payu_client import PayUClient, init_payu
from fastapi import Request, Depends, Body
from app.validator import valid_user_from_header, MiniAppAuth


async def db_session_dep() -> AsyncIterator[AsyncSession]:
    async with get_async_session() as session:
        yield session

# вариант с автокоммитом при успехе
async def db_session_autocommit_dep() -> AsyncIterator[AsyncSession]:
    async with get_async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

def get_payu_client(request: Request) -> PayUClient:
    payu = getattr(request.app.state, "payu", None)
    if payu is None:
        payu = init_payu()
        request.app.state.payu = payu
    return payu

# Тип-алиас для удобного использования в сигнатурах
Db = Annotated[AsyncSession, Depends(db_session_dep)]
PayUClientDep = Annotated[PayUClient, Depends(get_payu_client)]
Auth = Annotated[MiniAppAuth, Depends(valid_user_from_header)]
JsonDict = Annotated[dict[str, Any], Body(...)]  # обязателен JSON в теле

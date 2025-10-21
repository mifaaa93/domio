from aiogram.fsm.storage.base import BaseStorage, StorageKey
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from db.models import FSMState
from db.session import get_async_session
from typing import Any
from aiogram.fsm.state import State


class PostgresFSMStorage(BaseStorage):
    """
    Хранилище FSM в PostgreSQL через SQLAlchemy.
    """

    async def set_state(self, key: StorageKey, state: str | State | None) -> None:
        # ✅ Преобразуем State в строку
        state_str = str(state) if state else None

        async with get_async_session() as session:
            stmt = (
                insert(FSMState)
                .values(user_id=key.user_id, chat_id=key.chat_id, state=state_str)
                .on_conflict_do_update(
                    index_elements=["user_id", "chat_id"],
                    set_={"state": state_str},
                )
            )
            await session.execute(stmt)
            await session.commit()

    async def get_state(self, key: StorageKey) -> str | None:
        async with get_async_session() as session:
            res = await session.scalar(
                select(FSMState.state).where(
                    FSMState.user_id == key.user_id,
                    FSMState.chat_id == key.chat_id,
                )
            )
            # возвращаем строку или None
            return res

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        async with get_async_session() as session:
            stmt = (
                insert(FSMState)
                .values(user_id=key.user_id, chat_id=key.chat_id, data=data)
                .on_conflict_do_update(
                    index_elements=["user_id", "chat_id"],
                    set_={"data": data},
                )
            )
            await session.execute(stmt)
            await session.commit()

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        async with get_async_session() as session:
            res = await session.scalar(
                select(FSMState.data).where(
                    FSMState.user_id == key.user_id,
                    FSMState.chat_id == key.chat_id,
                )
            )
            return res or {}

    async def clear_state(self, key: StorageKey) -> None:
        async with get_async_session() as session:
            await session.execute(
                delete(FSMState).where(
                    FSMState.user_id == key.user_id,
                    FSMState.chat_id == key.chat_id,
                )
            )
            await session.commit()

    async def close(self) -> None:
        pass

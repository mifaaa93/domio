from aiogram import BaseMiddleware
from aiogram.types import Chat, User as TgUser
from aiogram.types.update import Update
from typing import Callable, Dict, Any, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, null, func
from db.session import get_async_session
from db.models import User
import datetime



class PrivateChatOnlyMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        chat: Chat | None = data.get("event_chat")
        if not chat or chat.type != "private":
            return
        return await handler(event, data)
    

class DBSessionMiddleware(BaseMiddleware):
    """
    Создаёт новую асинхронную сессию SQLAlchemy для каждого апдейта.
    """
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        async with get_async_session() as session:
            data["session"] = session
            return await handler(event, data)


class UserActivityMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        session: AsyncSession | None = data.get("session")

        # Если нет сессии — откроем И ДЕРЖИМ до конца обработки
        if session is None:
            async with get_async_session() as session:
                data["session"] = session
                return await self._process(handler, event, data, session)
        else:
            return await self._process(handler, event, data, session)

    async def _process(self, handler, event: Update, data: dict, session: AsyncSession):
        # --- извлекаем Telegram-пользователя ---
        from_user: TgUser | None = getattr(event, "from_user", None)
        if event.message:
            from_user = event.message.from_user
        if event.callback_query:
            from_user = event.callback_query.from_user
        
        if not from_user:
            return await handler(event, data)

        user_id = from_user.id
        username = from_user.username
        first_name = from_user.first_name
        last_name = from_user.last_name
        now = datetime.datetime.now(datetime.timezone.utc)

        # --- реферал (NULL если нет такого пользователя) ---
        ref_value = null()
        if event.message and event.message.text and event.message.text.startswith("/start"):
            parts = event.message.text.split(maxsplit=1)
            if len(parts) == 2 and parts[1].isdigit():
                ref_id = int(parts[1])
                if ref_id and ref_id != user_id:
                    ref_value = select(User.id).where(User.id == ref_id).scalar_subquery()
        # --- UPSERT ---
        stmt = (
            insert(User)
            .values(
                id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                registered_at=now,
                last_active_at=now,
                is_active=True,
                referrer_id=ref_value,  # ← пишем при ПЕРВОЙ вставке
            )
            .on_conflict_do_update(
                index_elements=[User.id],
                set_={
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "last_active_at": now,
                    "is_active": True,
                   },
            )
            .returning(User)
        )

        result = await session.execute(stmt)
        user = result.scalar_one()
        await session.commit()

        data["user"] = user
        return await handler(event, data)
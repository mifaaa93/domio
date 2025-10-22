from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update, User as TgUser
from typing import Callable, Dict, Any, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from db.session import get_async_session
from db.models import User
import datetime


class PrivateChatOnlyMiddleware(BaseMiddleware):
    """
    Middleware, который пропускает только личные чаты (private).
    Все апдейты из групп, супергрупп и каналов игнорируются.
    """

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        chat_type = None

        if isinstance(event, Message):
            chat_type = event.chat.type
        elif isinstance(event, CallbackQuery):
            if event.message:
                chat_type = event.message.chat.type
        elif isinstance(event, Update):
            msg = event.message or event.edited_message or event.callback_query
            if msg:
                inner = msg.message if hasattr(msg, "message") else msg
                if getattr(inner, "chat", None):
                    chat_type = inner.chat.type

        if chat_type != "private":
            return  # просто игнорируем
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
    """
    Middleware для автообновления пользователя:
    - создаёт запись, если user не найден (UPSERT)
    - обновляет username / first_name / last_name / last_active_at
    - сохраняет referrer при первом запуске
    """

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession | None = data.get("session")
        if not session:
            async with get_async_session() as temp_sess:
                data["session"] = temp_sess
                session = temp_sess

        # --- извлекаем Telegram-пользователя ---
        from_user: TgUser | None = getattr(event, "from_user", None)
        if not from_user:
            if isinstance(event, CallbackQuery):
                from_user = event.from_user
            elif isinstance(event, Message):
                from_user = event.from_user
            elif isinstance(event, Update):
                if event.message:
                    from_user = event.message.from_user
                elif event.callback_query:
                    from_user = event.callback_query.from_user

        if not from_user:
            return await handler(event, data)

        user_id = from_user.id
        username = from_user.username
        first_name = from_user.first_name
        last_name = from_user.last_name
        now = datetime.datetime.now(datetime.timezone.utc)

        # --- извлекаем ref_id из /start ---
        ref_id = None
        if isinstance(event, Message) and event.text and event.text.startswith("/start"):
            parts = event.text.split(maxsplit=1)
            if len(parts) == 2 and parts[1].isdigit():
                ref_id = int(parts[1])

        # --- формируем UPSERT ---
        stmt = insert(User).values(
            id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            registered_at=now,
            last_active_at=now,
            is_active=True,
            referrer_id=ref_id if ref_id and ref_id != user_id else None,
        ).on_conflict_do_update(
            index_elements=[User.id],
            set_={
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "last_active_at": now,
                "is_active": True,
            },
        ).returning(User)

        result = await session.execute(stmt)
        user = result.scalar_one()
        await session.commit()

        data["user"] = user
        return await handler(event, data)
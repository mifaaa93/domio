# bot/workers.py
from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from aiogram import Bot
from aiogram.exceptions import (
    TelegramRetryAfter,
    TelegramForbiddenError,
    TelegramBadRequest,
)
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.session import get_async_session
from db.models import Listing, User, ScheduledMessage, MessageType, ChatType  # предполагается
from db.repo_async import (
    get_users_for_listing,
    claim_due_messages,
    mark_sending,
    mark_sent,
    mark_retry,
    get_saved_listing_ids,
)  # замените на ваш путь
from bot.keyboards.listing import get_under_listing_btns
from bot.texts import listing_t
from bot.utils.messages import (
    trigger_invoice,
    successful_subscription,
    successful_subscription_channel,
    successful_confirm_earn_channel,
    guides_sale,
    successful_guides_channel,
    successful_confirm_service_channel,
    )


logger = logging.getLogger("bot.worker")

# --- Настройки пайплайна рассылки листингов ---
P_CONCURRENCY = 20         # параллельных отправок
P_PER_CHAT_DELAY = 0.8     # пауза между отправками в разные чаты
P_EMPTY_SLEEP = 3          # пауза, если не нашли ни одного листинга
MAX_RETRIES = 3            # кол-во попыток на FloodWait
SCHED_CHECK_INTERVAL = 2.0   # как часто проверять очередь, сек
SCHED_BATCH_LIMIT = 50       # сколько задач за раз забирать


async def _deactivate_user(session: AsyncSession, user: User, reason: str):
    """Ставит is_active=False и коммитит."""
    if getattr(user, "is_active", None) is False:
        return
    logger.info(f"Deactivating user {user.id}: {reason}")
    user.is_active = False
    try:
        await session.commit()
    except Exception as e:
        logger.exception(f"Failed to deactivate user {user.id}: {e}")


def _is_block_or_missing_chat_error(e: TelegramBadRequest) -> bool:
    """
    Эвристика под частые тексты ошибок:
    - chat not found
    - bot was blocked by the user
    - Forbidden: bot was blocked by the user (часто летит как Forbidden, catch выше)
    - have no rights to send a message (если чат приватный и бот удалён)
    """
    msg = str(e).lower()
    patterns = [
        "chat not found",
        "bot was blocked",
        "user is deactivated",
        "have no rights to send",
        "need administrator rights",
    ]
    return any(p in msg for p in patterns)


# ==========================
# CLAIM одного листинга
# ==========================
async def claim_one_listing(session: AsyncSession) -> Listing | None:
    """
    Атомарно забирает ОДИН листинг для рассылки:
      - WHERE is_translated AND NOT is_sended
      - FOR UPDATE SKIP LOCKED
      - сразу is_sended = TRUE
      - COMMIT
    Возвращает листинг (уже помеченный) или None.
    """
    now = datetime.now(timezone.utc)

    stmt = (
        select(Listing)
        .where(Listing.is_translated.is_(True), Listing.is_sended.is_(False))
        .order_by(Listing.scraped_at.asc())
        .limit(1)
        .with_for_update(skip_locked=True)
        .options(
            selectinload(Listing.city),
            selectinload(Listing.district),
        )
    )
    res = await session.execute(stmt)
    listing = res.scalars().first()
    if not listing:
        return None

    listing.is_sended = True
    listing.updated_at = now
    await session.commit()
    await session.refresh(listing)
    return listing


# ==========================
# ОТПРАВКА С УЧЁТОМ РЕТРАЕВ
# ==========================
async def _send_message_with_retries(
    bot: Bot,
    chat_id: int | str,
    text: str,
    reply_markup=None,
    per_chat_delay: float = P_PER_CHAT_DELAY,
) -> bool:
    attempt = 0
    while True:
        try:
            await bot.send_message(chat_id, text, disable_web_page_preview=True, reply_markup=reply_markup)
            await asyncio.sleep(per_chat_delay)
            return True
        except TelegramRetryAfter as e:
            attempt += 1
            wait_for = float(getattr(e, "retry_after", 3.0))
            logger.warning(f"[send_message] FloodWait {wait_for:.1f}s (attempt {attempt}/{MAX_RETRIES}) for chat {chat_id}")
            await asyncio.sleep(max(1.0, wait_for))
            if attempt >= MAX_RETRIES:
                return False
        except (TelegramForbiddenError, TelegramBadRequest):
            # выше обработаем и деактивируем юзера
            raise
        except Exception as e:
            logger.exception(f"[send_message] Unexpected error for {chat_id}: {e}")
            return False


async def _send_photo_with_retries(
    bot: Bot,
    chat_id: int | str,
    photo: str,
    caption: str | None = None,
    reply_markup=None,
    per_chat_delay: float = P_PER_CHAT_DELAY,
) -> Message | None:
    """
    Возвращает Message при успехе (чтобы достать file_id), иначе None.
    """
    attempt = 0
    while True:
        try:
            msg = await bot.send_photo(chat_id, photo, caption=caption, reply_markup=reply_markup)
            await asyncio.sleep(per_chat_delay)
            return msg
        except TelegramRetryAfter as e:
            attempt += 1
            wait_for = float(getattr(e, "retry_after", 3.0))
            logger.warning(f"[send_photo] FloodWait {wait_for:.1f}s (attempt {attempt}/{MAX_RETRIES}) for chat {chat_id}")
            await asyncio.sleep(max(1.0, wait_for))
            if attempt >= MAX_RETRIES:
                return None
        except (TelegramForbiddenError, TelegramBadRequest):
            # пробросим дальше для деактивации
            raise
        except Exception as e:
            logger.exception(f"[send_photo] Unexpected error for {chat_id}: {e}")
            return None


# ==========================
# ОТПРАВКА ЛИСТИНГА ЮЗЕРУ
# ==========================
async def send_listing_to_user(bot: Bot, user: User, listing: Listing) -> bool:
    """
    Отправляет листинг юзеру.
    - есть tg_photo_id -> отправляем фото+caption
    - нет tg_photo_id, но есть фото-URL -> отправляем URL, берём file_id из ответа и кэшируем в listing.tg_photo_id
    - иначе шлём текстом
    - FloodWait -> ретраи
    - Forbidden/BadRequest -> деактивируем юзера
    """
    chat_id = user.id
    lang = user.language_code
    template = listing_t(lang, "listing_new_text")
    caption = template.format(
        city=listing.city.get_name_local(lang),
        price=listing.price,
        area=listing.area_m2,
        rooms=listing.rooms,
        description=listing.get_description_local(lang, 250),
    )
    # saved_ids — забираем отдельной короткой сессией
    async with get_async_session() as s:
        saved_ids = await get_saved_listing_ids(s, user)
    btns = get_under_listing_btns(listing, user, saved_ids)

    try:
        # 1) tg_photo_id уже есть
        if listing.tg_photo_id:
            msg = await _send_photo_with_retries(bot, chat_id, listing.tg_photo_id, caption=caption, reply_markup=btns)
            if msg:
                return True
            # если не удалось фото (например, file_id устарел), попробуем текстом
            return await _send_message_with_retries(bot, chat_id, caption, reply_markup=btns)

        # 2) tg_photo_id нет — попробуем взять первый URL из listing.photos
        photo_url = None
        if getattr(listing, "photos", None):
            try:
                if isinstance(listing.photos, (list, tuple)) and listing.photos:
                    # ваш формат: list[str]
                    photo_url = listing.photos[0]
            except Exception:
                photo_url = None

        if photo_url:
            msg = await _send_photo_with_retries(bot, chat_id, photo_url, caption=caption, reply_markup=btns)
            if msg and msg.photo:
                # кэшируем самого "большого" варианта фото
                try:
                    file_id = msg.photo[-1].file_id
                    async with get_async_session() as s:
                        # важно получить актуальный listing из БД (иначе другой воркер мог изменить)
                        db_listing = await s.get(Listing, listing.id)
                        if db_listing and not db_listing.tg_photo_id:
                            db_listing.tg_photo_id = file_id
                            db_listing.updated_at = datetime.now(timezone.utc)
                            await s.commit()
                except Exception as e:
                    logger.exception(f"Failed to save tg_photo_id for listing {listing.id}: {e}")
                return True
            # если с URL не вышло — отправим текстом
            return await _send_message_with_retries(bot, chat_id, caption, reply_markup=btns)

        # 3) фото нет вообще — только текст
        return await _send_message_with_retries(bot, chat_id, caption, reply_markup=btns)

    except TelegramForbiddenError as e:
        # пользователь заблокировал бота / нет прав писать
        async with get_async_session() as s:
            db_user = await s.get(User, user.id)
            if db_user:
                await _deactivate_user(s, db_user, reason=str(e))
        return False
    except TelegramBadRequest as e:
        # чат не найден / бот заблокирован / иные "постоянные" причины
        if _is_block_or_missing_chat_error(e):
            async with get_async_session() as s:
                db_user = await s.get(User, user.id)
                if db_user:
                    await _deactivate_user(s, db_user, reason=str(e))
            return False
        # прочие BadRequest (вроде неверного markup), логируем и фейлим, но юзера не трогаем
        logger.warning(f"BadRequest for {chat_id}: {e}")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error sending to {chat_id}: {e}")
        return False


# ==========================
# ОБРАБОТКА ОДНОГО ЛИСТИНГА
# ==========================
async def process_claimed_listing(bot: Bot, users: list[User], listing: Listing) -> tuple[int, int]:
    """
    Рассылает listing всем релевантным пользователям.
    """
    if not users:
        logger.info(f"[LISTING] {listing.id}: no recipients")
        return (0, 0)

    sem = asyncio.Semaphore(P_CONCURRENCY)

    async def worker(u: User):
        async with sem:
            return await send_listing_to_user(bot, u, listing)

    results = await asyncio.gather(*(worker(u) for u in users), return_exceptions=False)
    ok = sum(1 for r in results if r)
    fail = len(results) - ok
    logger.info(f"[LISTING] {listing.id}: sent={ok}, failed={fail}")
    return ok, fail


# ==========================
# ПАЙПЛАЙН (только листинги)
# ==========================
async def pipeline_new_listings_users(bot: Bot, shutdown_event: asyncio.Event):
    """
    Бесконечный цикл:
      - claim_one_listing() -> is_sended = TRUE
      - разослать
      - если нечего слать — спим P_EMPTY_SLEEP
    """
    logger.info("▶️ Pipeline:listings started")
    try:
        while not shutdown_event.is_set():
            async with get_async_session() as session:
                listing = await claim_one_listing(session)
                if not listing:
                    try:
                        await asyncio.wait_for(asyncio.sleep(P_EMPTY_SLEEP), timeout=P_EMPTY_SLEEP + 1)
                    except asyncio.CancelledError:
                        raise
                    continue

                try:
                    # получаем юзеров (и всё нужное) с отдельной сессией
                    async with get_async_session() as s:
                        users: list[User] = await get_users_for_listing(s, listing)

                    # а рассылку делаем уже без «общей» сессии
                    await process_claimed_listing(bot, users, listing)
                except Exception as e:
                    logger.exception(f"[LISTING] processing failed (id={listing.id}): {e}")
                    # не откатываем is_sended, чтобы избежать дублей
    except asyncio.CancelledError:
        logger.info("⏹ Pipeline:listings cancelled")
        raise
    finally:
        logger.info("⏹ Pipeline:listings stopped")


async def pipeline_scheduled_messages(bot: Bot, shutdown_event: asyncio.Event):
    """
    Бесконечный цикл:
      - claim_due_messages() -> список задач со статусом QUEUED и send_at<=now
      - для каждой: mark_sending -> попытка отправки -> mark_sent / mark_retry
      - если задач нет — спим SCHED_CHECK_INTERVAL
    """
    logger.info("▶️ Pipeline:scheduled started")
    try:
        while not shutdown_event.is_set():
            async with get_async_session() as session:
                # Захватываем пакет задач
                tasks = await claim_due_messages(
                    session,
                    worker_id="sched-worker",
                    limit=SCHED_BATCH_LIMIT,
                )
                if not tasks:
                    try:
                        await asyncio.wait_for(asyncio.sleep(SCHED_CHECK_INTERVAL), timeout=SCHED_CHECK_INTERVAL + 1)
                    except asyncio.CancelledError:
                        raise
                    continue

                sem = asyncio.Semaphore(P_CONCURRENCY)

                async def handle_one(m: ScheduledMessage):
                    # 1) mark_sending — отдельная короткая сессия
                    try:
                        async with get_async_session() as s:
                            await mark_sending(s, m.id)
                    except Exception as e:
                        logger.exception(f"[SCHED] mark_sending failed for {m.id}: {e}")
                        return

                    # 2) отправка — без БД-сессии
                    ok = await send_scheduled_message(bot, m)

                    # 3) finalize — отдельная короткая сессия
                    try:
                        async with get_async_session() as s:
                            if ok:
                                await mark_sent(s, m.id)
                            else:
                                await mark_retry(s, m.id, last_error="send failed")
                    except Exception as e:
                        logger.exception(f"[SCHED] finalize failed for {m.id}: {e}")

                await asyncio.gather(*(handle_one(m) for m in tasks))
    except asyncio.CancelledError:
        logger.info("⏹ Pipeline:scheduled cancelled")
        raise
    finally:
        logger.info("⏹ Pipeline:scheduled stopped")


async def send_scheduled_message(bot: Bot, msg: ScheduledMessage) -> bool:
    """
    Универсальная отправка ScheduledMessage:
      - chat_type: private / channel
      - message_type: можно ветвить поведение по типам
      - payload: словарь с данными для шаблона/кнопок/медиа
    Возвращает True при успехе (для mark_sent), иначе False (для retry/failed).
    """
    chat_id = msg.chat_id
    payload: dict[str, Any] = msg.payload
    sub_type = None
    if payload:
        sub_type = payload.get("sub_type", None)
    # Пример: разные типы сообщений
    mtype = msg.message_type
    try:
        # Можно разветвить логику по типу (пример)
        if mtype == MessageType.INVOICE and sub_type=="done":
            # юзеру и в канал про подписку
            user = msg.user
            if msg.chat_type == ChatType.PRIVATE:
                message = await successful_subscription(user=user, bot=bot, payload=payload)
            elif msg.chat_type == ChatType.CHANNEL:
                message = await successful_subscription_channel(user=user, bot=bot, payload=payload, chat_id=msg.chat_id)
            return True
        
        elif mtype == MessageType.INVOICE and sub_type=="guides":
            # юзеру и в канал про покупку гайда
            user = msg.user
            if msg.chat_type == ChatType.PRIVATE:
                message = await guides_sale(user=user, bot=bot)
            elif msg.chat_type == ChatType.CHANNEL:
                message = await successful_guides_channel(user=user, bot=bot, payload=payload, chat_id=msg.chat_id)
            return True
    
        elif mtype == MessageType.INVOICE:
            # отправляем инвойс юзеру
            user = msg.user
            message = await trigger_invoice(user=user, bot=bot)
            return True
        
        elif mtype == MessageType.REMINDER:
            # можно дополнительно форматировать text/caption
            pass
        elif mtype == MessageType.BROADCAST:
            pass
        elif mtype == MessageType.CUSTOM:
            if payload.get("from") == "confirm_earn":
                # уведомление в канал что запрошен вывод средств
                message = await successful_confirm_earn_channel(user=msg.user, bot=bot, payload=payload, chat_id=msg.chat_id)
            elif payload.get("from") == "service":
                # отправка в канал связь с по другим услугам
                message = await successful_confirm_service_channel(user=msg.user, bot=bot, payload=payload, chat_id=msg.chat_id)
            elif payload.get("from") == "agent":
                # отправка в канал связь с риелтором
                message = await successful_confirm_service_channel(user=msg.user, bot=bot, payload=payload, chat_id=msg.chat_id)
        return True
    

    except TelegramForbiddenError as e:
        # Если пользователь есть и это приватный чат — деактивируем
        if msg.chat_type == ChatType.PRIVATE and msg.user:
            async with get_async_session() as s:
                # подстрахуемся, что юзер актуальный
                user = await s.get(User, msg.user.id)
                if user:
                    await _deactivate_user(s, user, reason=str(e))
        return True
    except TelegramBadRequest as e:
        if _is_block_or_missing_chat_error(e):
            if msg.chat_type == ChatType.PRIVATE and msg.user:
                async with get_async_session() as s:
                    user = await s.get(User, msg.user.id)
                    if user:
                        await _deactivate_user(s, user, reason=str(e))
            return True
        logger.warning(f"[SCHED] BadRequest for {chat_id}: {e}")
        return False
    except Exception as e:
        logger.exception(f"[SCHED] Unexpected error for {chat_id}: {e}")
        return False


# ==========================
# ТОЧКА ВХОДА ВОРКЕРА
# ==========================
async def newsletter_worker(bot: Bot, shutdown_event: asyncio.Event) -> None:
    """
    Главный воркер: поднимает два параллельных пайплайна —
      1) рассылка новых листингов;
      2) отправка запланированных сообщений (ScheduledMessage).
    """
    logger.info("📨 Newsletter worker started")
    task_listings = asyncio.create_task(pipeline_new_listings_users(bot, shutdown_event))
    task_sched = asyncio.create_task(pipeline_scheduled_messages(bot, shutdown_event))
    try:
        await asyncio.gather(task_listings, task_sched)
    except asyncio.CancelledError:
        task_listings.cancel()
        task_sched.cancel()
        raise
    finally:
        logger.info("📨 Newsletter worker stopped")

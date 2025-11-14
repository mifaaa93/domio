# bot\bot.py

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from threading import Event
from db.fsm_storage import PostgresFSMStorage
from bot.middlewares import DBSessionMiddleware, UserActivityMiddleware, PrivateChatOnlyMiddleware, FileEchoMiddleware
from bot.handlers import start, menu, search, settings, other
from config import BOT_TOKEN
from bot.workers import newsletter_worker
import contextlib


logger = logging.getLogger("bot")


async def run_bot(stop_event: Event) -> None:
    """Асинхронный запуск бота с корректным завершением через threading.Event"""
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_is_disabled=True)
    )

    for name in ("aiogram", "aiogram.event", "aiogram.dispatcher", "aiogram.fsm"):
        aiologger = logging.getLogger(name)
        aiologger.handlers = logger.handlers
        aiologger.setLevel(logger.level)
        aiologger.propagate = False

    storage = PostgresFSMStorage()
    dp = Dispatcher(storage=storage)
    dp.update.middleware(FileEchoMiddleware())
    dp.update.middleware(PrivateChatOnlyMiddleware())
    dp.update.middleware(DBSessionMiddleware())
    dp.update.middleware(UserActivityMiddleware())

    dp.include_router(start.router)
    dp.include_router(settings.router)
    dp.include_router(menu.router)
    dp.include_router(search.router)
    dp.include_router(other.router)

    logger.info("🤖 Bot started polling...")

    # --- общий asyncio-сигнал для graceful shutdown воркеров ---
    shutdown_event = asyncio.Event()

    try:
        polling_task = asyncio.create_task(dp.start_polling(bot))
        worker_task = asyncio.create_task(newsletter_worker(bot, shutdown_event))

        loop = asyncio.get_running_loop()
        # ждём, пока stop_event будет установлен в другом потоке
        await loop.run_in_executor(None, stop_event.wait)
        logger.info("🛑 Stop event received — shutting down bot & workers...")

        # сигнализируем воркерам на остановку
        shutdown_event.set()

        # отменяем polling (он сам корректно закроет диспетчер)
        polling_task.cancel()
        # ждём задачи (воркер может ещё доправить пачку, если вы так решите)
        with contextlib.suppress(asyncio.CancelledError):
            await polling_task

        # воркер завершаем мягко
        worker_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await worker_task

    except Exception as e:
        logger.exception(f"💥 Bot crashed: {e}")
    finally:
        await bot.session.close()
        logger.info("✅ Bot stopped cleanly")

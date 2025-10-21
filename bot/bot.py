import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from threading import Event
from db.fsm_storage import PostgresFSMStorage
from bot.middlewares import DBSessionMiddleware, UserActivityMiddleware, PrivateChatOnlyMiddleware
from bot.handlers import start, menu
from config import BOT_TOKEN

logger = logging.getLogger("bot")


async def run_bot(stop_event: Event) -> None:
    """Асинхронный запуск бота с корректным завершением через threading.Event"""
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    for name in ("aiogram", "aiogram.event", "aiogram.dispatcher", "aiogram.fsm"):
        aiologger = logging.getLogger(name)
        aiologger.handlers = logger.handlers
        aiologger.setLevel(logger.level)
        aiologger.propagate = False

    storage = PostgresFSMStorage()
    dp = Dispatcher(storage=storage)

    dp.update.middleware(PrivateChatOnlyMiddleware())
    dp.update.middleware(DBSessionMiddleware())
    dp.update.middleware(UserActivityMiddleware())

    dp.include_router(start.router)
    dp.include_router(menu.router)

    logger.info("🤖 Bot started polling...")

    # Запускаем polling и параллельно ждём стоп-сигнала
    try:
        polling_task = asyncio.create_task(dp.start_polling(bot))
        loop = asyncio.get_running_loop()
        # ждём, пока stop_event будет установлен в другом потоке
        await loop.run_in_executor(None, stop_event.wait)
        logger.info("🛑 Stop event received — shutting down bot...")
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass
    except Exception as e:
        logger.exception(f"💥 Bot crashed: {e}")
    finally:
        await bot.session.close()
        logger.info("✅ Bot stopped cleanly")

# main.py
import os
import sys
import time
import logging
import traceback
import threading
import asyncio

from config import LOG_DIR
from bot.bot import run_bot  # aiogram v3 async entrypoint: async def run_bot(stop_event)
from parser.olx_parser import start_olx
from parser.otodom_parser import start_otodom
from parser.morizon_parser import start_morizone
from parser.nieruch_parser import start_nieruch
from parser.actual_cheker import check_actual_listings_sync  # если нужен асинхронный фон. чекер
from parser.translater_w import start_translation_pool
# =======================
# Логирование
# =======================
os.makedirs(LOG_DIR, exist_ok=True)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

def make_logger(name: str, filename: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(os.path.join(LOG_DIR, filename), encoding="utf-8", mode="a")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    if not logger.handlers:
        logger.addHandler(fh)
        #logger.addHandler(console_handler)
    return logger

logger = make_logger("main", "main.log")
logger.addHandler(console_handler)
logger_olx = make_logger("olx", "parser_olx.log")
logger_otodom = make_logger("otodom", "parser_otodom.log")
logger_morizon = make_logger("morizon", "parser_morizon.log")
logger_nieruch = make_logger("nieruchomosci", "parser_nieruchomosci.log")
logger_net = make_logger("net", "net.log")
logger_bot = make_logger("bot", "bot.log")
logger_act = make_logger("actual", "actual.log")
logger_trans = make_logger("translator", "translator.log")
logger_worker = make_logger("bot.worker", "worker.log")

# =======================
# Helpers: потоки
# =======================
stop_event = threading.Event()

def run_thread(target, name: str) -> threading.Thread:
    """Запускает поток и оборачивает его в безопасный wrapper."""
    def safe_wrapper():
        try:
            target()
        except Exception:
            err = traceback.format_exc()
            logger.error("Thread %s crashed:\n%s", name, err)

    t = threading.Thread(target=safe_wrapper, name=name, daemon=True)
    t.start()
    logger.info("Started thread %s", name)
    return t

def build_thread_specs() -> dict[str, callable]:
    """
    Возвращает фабрики запуска парсеров.
    Каждая фабрика возвращает уже стартованный Thread.
    """
    return {
        #"olx":     lambda: run_thread(lambda: start_olx(stop_event), "olx"),
        #"otodom":  lambda: run_thread(lambda: start_otodom(stop_event), "otodom"),
        #"morizon": lambda: run_thread(lambda: start_morizone(stop_event), "morizon"),
        #"nieruch": lambda: run_thread(lambda: start_nieruch(stop_event), "nieruch"),
        #"checker": lambda: run_thread(lambda: check_actual_listings_sync(stop_event), "checker"),
        #"translator": lambda: run_thread(lambda: start_translation_pool(stop_event), "translator"),
    }

def start_threads(thread_specs: dict[str, callable]) -> dict[str, threading.Thread]:
    """Стартует все заявленные фоновые потоки и возвращает словарь name->Thread."""
    return {name: launcher() for name, launcher in thread_specs.items()}

# =======================
# Watchdog: перезапуск упавших парсеров
# =======================
async def watchdog(threads: dict[str, threading.Thread],
                   thread_specs: dict[str, callable],
                   interval_sec: int = 10) -> None:
    """
    Периодически проверяет состояние потоков и перезапускает упавшие.
    Работает до тех пор, пока не будет установлен stop_event.
    """
    logger.info("Watchdog started (interval=%ss)", interval_sec)
    while not stop_event.is_set():
        # собираем упавшие
        dead = [name for name, t in threads.items() if not t.is_alive()]
        if dead:
            for name in dead:
                logger.warning("Thread %s is dead — restarting...", name)
                try:
                    threads[name] = thread_specs[name]()  # перезапуск
                    # небольшая пауза между рестартами, чтобы не лупило
                    await asyncio.sleep(2)
                except Exception:
                    logger.exception("Failed to restart thread %s", name)
        await asyncio.sleep(interval_sec)
    logger.info("Watchdog stopped")

# =======================
# Async main: бот в главном потоке + watchdog
# =======================
async def async_main():
    # 1) стартуем фоновые парсеры
    thread_specs = build_thread_specs()
    threads = start_threads(thread_specs)

    # 2) поднимаем watchdog как фоновую async-задачу
    wd_task = asyncio.create_task(watchdog(threads, thread_specs, interval_sec=10))

    # 3) запускаем бота (блокирующе, но в async — до сигналов/остановки)
    try:
        logger.info("Starting bot in main thread (aiogram handles signals)...")
        # если нужен ещё фон. асинхронный таск (напр. check_actual_listings):
        # checker_task = asyncio.create_task(check_actual_listings(stop_event))
        await run_bot(stop_event)
        # если run_bot завершился сам — продолжаем graceful shutdown
    except Exception:
        logger.exception("Bot crashed")
    finally:
        # 4) Остановка: выставляем стоп для потоков и watchdog
        logger.info("Stopping all background threads...")
        stop_event.set()

        # останавливаем watchdog
        wd_task.cancel()
        try:
            await wd_task
        except asyncio.CancelledError:
            pass

        # ждём остановки парсеров
        for name, t in threads.items():
            logger.info("Waiting for thread %s to finish...", name)
            t.join(timeout=10)
        # === КРИТИЧЕСКИЙ БЛОК: зачистка event-loop ===
        loop = asyncio.get_running_loop()

        # Отменяем оставшиеся таски, кроме текущей
        pending = [task for task in asyncio.all_tasks(loop) if task is not asyncio.current_task(loop)]
        if pending:
            logger.info("Cancelling %d pending task(s)...", len(pending))
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)

        # Закрываем async-генераторы
        try:
            await loop.shutdown_asyncgens()
        except Exception:
            logger.exception("shutdown_asyncgens failed")

        # ВАЖНО: закрыть default ThreadPoolExecutor (иначе висят не-daemon потоки)
        try:
            await loop.shutdown_default_executor()
        except Exception:
            logger.exception("shutdown_default_executor failed")
            
        logger.info("✅ All threads stopped. Exiting.")

# =======================
# Entrypoint
# =======================
def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        # SIGINT перехватится aiogram’ом внутри run_bot, но на всякий — graceful exit
        logger.info("Ctrl+C -> exiting")
        stop_event.set()
        time.sleep(1)
    finally:
        sys.exit(0)

if __name__ == "__main__":
    main()

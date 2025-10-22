import logging, os, time, threading, sys, asyncio, traceback
from parser.olx_parser import start_olx
from parser.otodom_parser import start_otodom
from parser.morizon_parser import start_morizone
from parser.nieruch_parser import start_nieruch
from parser.actual_cheker import check_actual_listings
from bot.bot import run_bot
from config import LOG_DIR


os.makedirs(LOG_DIR, exist_ok=True)
stop_event = threading.Event()

# -------- базовая настройка логов --------
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
        logger.addHandler(console_handler)
    return logger


logger = make_logger("main", "main.log")
logger_olx = make_logger("olx", "parser_olx.log")
logger_otodom = make_logger("otodom", "parser_otodom.log")
logger_morizon = make_logger("morizon", "parser_morizon.log")
logger_nieruch = make_logger("nieruchomosci", "parser_nieruchomosci.log")
logger_net = make_logger("net", "net.log")
logger_bot = make_logger("bot", "bot.log")
logger_act = make_logger("actual", "actual.log")


# -------- функции запуска --------
def run_thread(target, name):
    """Запускает поток и оборачивает его в безопасный wrapper"""
    def safe_wrapper():
        try:
            target()
        except Exception:
            err = traceback.format_exc()
            logger.error(f"Thread {name} crashed:\n{err}")

    t = threading.Thread(target=safe_wrapper, name=name, daemon=True)
    t.start()
    logger.info("Started thread %s", name)
    return t


def run_async_in_thread(coro_func, *args, **kwargs):
    """Запускает асинхронную функцию (например, aiogram-бота) в отдельном потоке"""
    def runner():
        try:
            asyncio.run(coro_func(*args, **kwargs))
        except Exception:
            err = traceback.format_exc()
            logger.error(f"Async thread {coro_func.__name__} crashed:\n{err}")
    return run_thread(runner, coro_func.__name__)


# -------- основной цикл --------
def main():
    # словарь: имя -> (функция запуска, объект потока)
    thread_specs = {
        #"olx":      lambda: run_thread(lambda: start_olx(stop_event), "olx"),
        #"otodom":   lambda: run_thread(lambda: start_otodom(stop_event), "otodom"),
        #"morizon":  lambda: run_thread(lambda: start_morizone(stop_event), "morizon"),
        #"nieruch":  lambda: run_thread(lambda: start_nieruch(stop_event), "nieruch"),
        "bot":      lambda: run_async_in_thread(run_bot, stop_event),
        #"checker":  lambda: run_async_in_thread(check_actual_listings, stop_event),
    }

    # запускаем всё один раз
    threads = {name: launcher() for name, launcher in thread_specs.items()}

    try:
        while True:
            time.sleep(30)
            dead = [name for name, t in threads.items() if not t.is_alive()]
            if dead:
                for name in dead:
                    logger.warning(f"Thread {name} is dead — restarting...")
                    threads[name] = thread_specs[name]()  # перезапуск
                    time.sleep(3)  # небольшая пауза, чтобы не заспамить рестартами
    except KeyboardInterrupt:
        logger.info("Ctrl+C -> exiting (daemon threads will terminate)")
        stop_event.set()  # уведомляем все потоки
        for name, t in threads.items():
            logger.info(f"Waiting for thread {name} to finish...")
            t.join(timeout=10)
        logger.info("✅ All threads stopped. Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()
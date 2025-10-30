import time
import logging
from typing import Tuple
from threading import Event
from concurrent.futures import ThreadPoolExecutor, as_completed

from sqlalchemy import select, delete, update

from db.session import get_sync_tx  # <-- синхронная сессия!
from db.models import Listing
from config import CHECK_INTERVAL_HOURS, MAX_CONCURRENT_CHECKS
from net.http_client import fetch_status_sync  # <-- синхронная версия
from parser.olx_parser import headers as olx_headers
from parser.otodom_parser import headers as otodom_headers
from parser.morizon_parser import HEADERS as morizon_headers
from parser.nieruch_parser import HEADERS as nieruch_headers

logger = logging.getLogger("actual")

HEADERS_BY_SOURCE = {
    "olx": olx_headers,
    "otodom": otodom_headers,
    "morizon": morizon_headers,
    "nieruch": nieruch_headers,
}


def wait_stop(stop_event: Event, timeout: float) -> None:
    """Синхронно ждёт stop_event или таймаут."""
    try:
        stop_event.wait(timeout)
    except Exception:
        pass


def _due_listings(batch_limit: int) -> list[Tuple[int, str, str | None]]:
    """
    Возвращает список кандидатів для проверки в виде простых кортежей:
    (id, url, source) — чтобы не таскать ORM-объекты между потоками.
    """
    now_ts = int(time.time())
    min_check_ts = now_ts - CHECK_INTERVAL_HOURS * 3600

    with get_sync_tx() as session:
        stmt = (
            select(Listing.id, Listing.url, Listing.source, Listing.last_check)
            .where((Listing.last_check.is_(None)) | (Listing.last_check < min_check_ts))
            .order_by(Listing.last_check.asc().nullsfirst())
            .limit(batch_limit)
        )
        rows = session.execute(stmt).all()

    # конвертируем к нужной форме
    return [(rid, url, src) for (rid, url, src, _last_check) in rows]


def _check_and_update_one(listing_id: int, url: str, source: str | None) -> None:
    """
    Синхронно проверяет одно объявление и обновляет БД.
    Отдельная сессия на каждый вызов (безопасно для потоков).
    """
    headers = HEADERS_BY_SOURCE.get((source or "").lower())
    now_ts = int(time.time())

    try:
        status_code = fetch_status_sync(url, headers=headers)
    except Exception as e:
        logger.warning(f"⚠️ Ошибка запроса {url}: {e}")
        try:
            with get_sync_tx() as session:
                session.execute(
                    update(Listing)
                    .where(Listing.id == listing_id)
                    .values(last_check=now_ts)
                )
        except Exception:
            logger.exception(f"💥 Ошибка при сохранении last_check для {url}")
        return

    try:
        with get_sync_tx() as session:
            if status_code in (404, 410, 451):
                logger.info(f"❌ [{status_code}] Удаляем {url}")
                session.execute(delete(Listing).where(Listing.id == listing_id))
            else:
                session.execute(
                    update(Listing)
                    .where(Listing.id == listing_id)
                    .values(last_check=now_ts)
                )
                if status_code != 200:
                    logger.warning(f"⚠️ [{status_code}] {url}")
    except Exception as e:
        logger.exception(f"💥 Ошибка при обновлении БД для {url}: {e}")


def check_actual_listings_sync(stop_event: Event) -> None:
    """
    Бесконечный синхронный цикл проверки актуальности.
    Параллелизация — через ThreadPoolExecutor с max_workers=MAX_CONCURRENT_CHECKS.
    """
    logger.info("🔄 Запуск синхронной проверки актуальности объявлений...")

    # защитa от 0/None в конфиге
    max_workers = max(1, int(MAX_CONCURRENT_CHECKS or 1))
    batch_limit = max_workers * 5 or 20

    while not stop_event.is_set():
        try:
            listings = _due_listings(batch_limit=batch_limit)
            if not listings:
                logger.info("✅ Нет объявлений для проверки. Спим 5 минут.")
                wait_stop(stop_event, timeout=300)
                continue

            # Параллельно проверяем URL'ы
            with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="actual") as pool:
                futures = []
                for listing_id, url, source in listings:
                    fut = pool.submit(_check_and_update_one, listing_id, url, source)
                    futures.append(fut)
                    # лёгкий троттлинг, чтобы не стрелять мгновенно всеми запросами
                    time.sleep(0.05)

                # дожидаемся завершения задач (и логируем ошибки)
                for fut in as_completed(futures):
                    try:
                        fut.result()
                    except Exception:
                        logger.exception("💥 Необработанное исключение в worker-е")

        except Exception as e:
            logger.exception(f"💥 Глобальная ошибка в цикле проверки: {e}")

        # короткая пауза между проходами или досрочный выход по stop_event
        wait_stop(stop_event, timeout=2)

    logger.info("✅ Синхронная проверка актуальности завершена (stop_event set).")

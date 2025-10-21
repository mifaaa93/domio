import asyncio
import time
import logging
from sqlalchemy import select, delete
from threading import Event

from db.session import get_async_session
from db.models import Listing
from config import CHECK_INTERVAL_HOURS, MAX_CONCURRENT_CHECKS
from net.http_client import fetch_status
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


async def wait_stop(stop_event: Event, timeout: float):
    """Асинхронно ждёт stop_event или таймаут."""
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, stop_event.wait, timeout)
    except Exception:
        pass


async def check_one_listing(listing: Listing) -> None:
    """Проверяет одно объявление и обновляет его в БД (отдельная сессия на каждый вызов)."""
    async with get_async_session() as session:
        url = listing.url
        try:
            status_code = await fetch_status(url, headers=HEADERS_BY_SOURCE.get(listing.source))
        except Exception as e:
            logger.warning(f"⚠️ Ошибка запроса {url}: {e}")
            listing.last_check = int(time.time())
            session.add(listing)
            await session.commit()
            return

        try:
            if status_code in (404, 410, 451):
                logger.info(f"❌ [{status_code}] Удаляем {url}")
                await session.execute(delete(Listing).where(Listing.id == listing.id))
            else:
                listing.last_check = int(time.time())
                session.add(listing)
                if status_code != 200:
                    logger.warning(f"⚠️ [{status_code}] {url}")
            await session.commit()
        except Exception as e:
            logger.exception(f"💥 Ошибка при обновлении БД для {url}: {e}")


async def check_actual_listings(stop_event: Event):
    """Бесконечно проверяет актуальность объявлений из базы."""
    logger.info("🔄 Запуск проверки актуальности объявлений...")

    while not stop_event.is_set():
        try:
            async with get_async_session() as session:
                now_ts = int(time.time())
                min_check_ts = now_ts - CHECK_INTERVAL_HOURS * 3600

                stmt = (
                    select(Listing)
                    .where((Listing.last_check.is_(None)) | (Listing.last_check < min_check_ts))
                    .order_by(Listing.last_check.asc().nullsfirst())
                    .limit(MAX_CONCURRENT_CHECKS * 5 or 20)
                )
                listings = (await session.execute(stmt)).scalars().all()

            if not listings:
                logger.info("✅ Нет объявлений для проверки. Спим 5 минут.")
                await wait_stop(stop_event, timeout=300)
                continue

            sem = asyncio.Semaphore(MAX_CONCURRENT_CHECKS)

            async def safe_check(l: Listing):
                async with sem:
                    try:
                        await check_one_listing(l)
                    except Exception as e:
                        logger.exception(f"💥 Ошибка при проверке {l.url}: {e}")
                    await asyncio.sleep(1)

            await asyncio.gather(*[safe_check(l) for l in listings], return_exceptions=True)

        except Exception as e:
            logger.exception(f"💥 Глобальная ошибка в цикле проверки: {e}")

        await wait_stop(stop_event, timeout=2)

    logger.info("✅ Проверка актуальности завершена (stop_event set).")

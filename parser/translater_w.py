# parser/translater_w.py
from __future__ import annotations
import logging
import threading
from time import sleep
from random import random
from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.orm import Session, selectinload

from db.session import get_sync_session
from db.models import Listing, City, District
from ai.ai_module import process_listing_one_call, translate_places

logger = logging.getLogger("translator")

# --- настройки ---
IDLE_SLEEP = 5.0
ROW_SLEEP  = 0.10
CLAIM_LIMIT_CITIES = 200
CLAIM_LIMIT_DISTRICTS = 400

LISTING_WORKERS = 4        # потоков для листингов
PLACES_WORKERS  = 1        # потоков для городов/районов
OPENAI_CONCURRENCY = 3     # одновременных вызовов к OpenAI


_openai_sema = threading.Semaphore(OPENAI_CONCURRENCY)


# ============ claim'ы ============
def _claim_one_listing(session: Session) -> Optional[Listing]:
    stmt = (
        select(Listing)
        .where(Listing.is_translated.is_(False))
        .order_by(Listing.id.asc())
        .options(selectinload(Listing.city), selectinload(Listing.district))
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    return session.execute(stmt).scalars().first()

def _claim_cities_batch(session: Session, limit: int = CLAIM_LIMIT_CITIES) -> list[City]:
    stmt = (
        select(City)
        .where(or_(City.name_uk.is_(None), City.name_en.is_(None)))
        .order_by(City.id.asc())
        .limit(limit)
        .with_for_update(skip_locked=True)
    )
    return list(session.execute(stmt).scalars().all())

def _claim_districts_batch(session: Session, limit: int = CLAIM_LIMIT_DISTRICTS) -> list[District]:
    stmt = (
        select(District)
        .where(or_(District.name_uk.is_(None), District.name_en.is_(None)))
        .order_by(District.id.asc())
        .limit(limit)
        .with_for_update(skip_locked=True)
    )
    return list(session.execute(stmt).scalars().all())


# ============ утилиты ============
def _coerce_rooms(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        try:
            return int(value)
        except Exception:
            return None
    if isinstance(value, str):
        import re
        m = re.search(r"\d+", value)
        if m:
            try:
                return int(m.group(0))
            except Exception:
                return None
    return None

def _build_ai_input(l: Listing) -> dict:
    city_str = getattr(getattr(l, "city", None), "name_pl", None) or ""
    distr_str = getattr(getattr(l, "district", None), "name_pl", None) or ""
    return {
        "title": l.title or "",
        "description": l.description or "",
        "city": city_str,
        "district": distr_str,
        "parsed_address": l.address or ""}

def _apply_translations(l: Listing, result: dict) -> bool:
    updated = False
    tr = (result or {}).get("translation") or {}
    uk = tr.get("uk") or {}
    en = tr.get("en") or {}

    title_en = en.get("title")
    title_uk = uk.get("title")
    desc_en  = en.get("description")
    desc_uk  = uk.get("description")

    if title_en and title_en != l.title_en:
        l.title_en = title_en; updated = True
    if title_uk and title_uk != l.title_uk:
        l.title_uk = title_uk; updated = True
    if desc_en and desc_en != l.description_en:
        l.description_en = desc_en; updated = True
    if desc_uk and desc_uk != l.description_uk:
        l.description_uk = desc_uk; updated = True

    addr = result.get("address")
    if addr and addr != l.address:
        l.address = addr
    
    if not l.rooms and "rooms" in (result or {}):
        new_rooms = _coerce_rooms(result.get("rooms"))
        if new_rooms is not None and new_rooms != l.rooms:
            l.rooms = new_rooms

    if updated and not l.is_translated:
        l.is_translated = True

    return updated


# ============ worker loops ============
def _listing_worker(stop_evt: threading.Event, name: str):
    logger.info("ListingWorker %s started", name)
    while not stop_evt.is_set():
        with get_sync_session() as session:
            listing = _claim_one_listing(session)
            if not listing:
                session.rollback()
                sleep(IDLE_SLEEP)
                continue

            try:
                payload = _build_ai_input(listing)
                with _openai_sema:
                    result = process_listing_one_call(payload)

                if not isinstance(result, dict):
                    logger.warning("[%s] AI returned non-dict for id=%s, rollback", name, listing.id)
                    session.rollback()
                    sleep(ROW_SLEEP)
                    continue

                changed = _apply_translations(listing, result)
                if changed:
                    session.add(listing)
                    session.commit()
                    logger.info("[%s] ✅ listing %s translated", name, listing.id)
                else:
                    session.rollback()
                    logger.info("[%s] ℹ️ nothing to update for %s", name, listing.id)
            except Exception:
                logger.exception("[%s] error translating id=%s, rollback", name, getattr(listing, "id", "?"))
                session.rollback()

        sleep(ROW_SLEEP)
    logger.info("ListingWorker %s stopped", name)


def _places_worker(stop_evt: threading.Event, name: str):
    logger.info("PlacesWorker %s started", name)
    while not stop_evt.is_set():
        did_any = False
        with get_sync_session() as session:
            # города
            try:
                cities = _claim_cities_batch(session)
                if cities:
                    did_any = True
                    with _openai_sema:
                        mapping = translate_places([c.name_pl for c in cities])
                    for c in cities:
                        tr = mapping.get(c.name_pl) or {}
                        c.name_uk = tr.get("uk") or c.name_uk
                        c.name_en = tr.get("en") or c.name_en
                    session.commit()
                    logger.info("[%s] ✅ translated cities: %d", name, len(cities))
            except Exception:
                logger.exception("[%s] cities batch failed, rollback", name)
                session.rollback()
        with get_sync_session() as session:
            # районы
            try:
                districts = _claim_districts_batch(session)
                if districts:
                    did_any = True
                    with _openai_sema:
                        mapping = translate_places([d.name_pl for d in districts])
                    for d in districts:
                        tr = mapping.get(d.name_pl) or {}
                        d.name_uk = tr.get("uk") or d.name_uk
                        d.name_en = tr.get("en") or d.name_en
                    session.commit()
                    logger.info("[%s] ✅ translated districts: %d", name, len(districts))
            except Exception:
                logger.exception("[%s] districts batch failed, rollback", name)
                session.rollback()

        sleep(ROW_SLEEP if did_any else IDLE_SLEEP)
    logger.info("PlacesWorker %s stopped", name)


# ============ PUBLIC API (БЛОКИРУЕТСЯ) ============
def start_translation_pool(stop_event: threading.Event,
                           listing_workers: int = LISTING_WORKERS,
                           places_workers: int = PLACES_WORKERS) -> None:
    """
    Блокирующая точка входа (под твою run_thread(...)):
    запускает N потоков переводов листингов + M потоков перевода городов/районов
    и держит их, пока stop_event не будет установлен.
    """
    threads: list[threading.Thread] = []

    # стартуем потоки
    for i in range(listing_workers):
        t = threading.Thread(target=_listing_worker, args=(stop_event, f"L{i+1}"), daemon=True)
        t.start()
        threads.append(t)

    for j in range(places_workers):
        t = threading.Thread(target=_places_worker, args=(stop_event, f"P{j+1}"), daemon=True)
        t.start()
        threads.append(t)

    logger.info("Translator pool started: %d listing workers, %d places workers", listing_workers, places_workers)

    # блокируемся до остановки
    try:
        while not stop_event.is_set():
            sleep(1.0)
    finally:
        # graceful shutdown: ждём завершения потоков
        for t in threads:
            t.join(timeout=5.0)
        logger.info("Translator pool stopped")

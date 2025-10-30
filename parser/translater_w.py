# translator_worker_one.py
from __future__ import annotations

import logging
from time import sleep
from threading import Event

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from db.session import get_sync_session
from db.models import Listing
from ai.ai_module import process_listing_one_call, translate_places

logger = logging.getLogger("translator")

IDLE_SLEEP = 30   # пауза, если нечего переводить
ROW_SLEEP  = 0.2  # лёгкий троттлинг между итерациями


def _claim_one(session: Session) -> Listing | None:
    """
    Забираем РОВНО ОДИН листинг под блокировку.
    FOR UPDATE SKIP LOCKED гарантирует отсутствие гонок при нескольких воркерах.
    """
    stmt = (
        select(Listing)
        .where(Listing.is_translated.is_(False))
        .order_by(Listing.id.asc())
        .options(selectinload(Listing.city), selectinload(Listing.district))
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    return session.execute(stmt).scalars().first()


def _build_ai_input(l: Listing) -> dict:
    city_str = getattr(getattr(l, "city", None), "name", None) or (str(l.city) if getattr(l, "city", None) else "")
    return {
        "title": l.title or "",
        "description": l.description or "",
        "city": city_str
    }


# translator_worker_one.py (фрагменты для замены)

def _apply_translations(l: Listing, result: dict) -> bool:
    """
    Ожидаемый формат result:
    {
        "address": "строка",
        "rooms": "строка или число",
        "translation": {
            "uk": {"title": "...", "description": "..."},
            "en": {"title": "...", "description": "..."}
        }
    }
    Обновляет: title_en/title_uk, description_en/description_uk,
               а также address и rooms (если пришли).
    Возвращает True, если были изменения В ПОЛЯХ ПЕРЕВОДА.
    """
    updated_translation = False  # только для переводов
    # --- безопасно достаём словари ---
    tr = (result or {}).get("translation") or {}
    uk = tr.get("uk") or {}
    en = tr.get("en") or {}

    # --- применяем переводы ---
    title_en = en.get("title")
    title_uk = uk.get("title")
    desc_en  = en.get("description")
    desc_uk  = uk.get("description")

    if title_en and title_en != l.title_en:
        l.title_en = title_en
        updated_translation = True
    if title_uk and title_uk != l.title_uk:
        l.title_uk = title_uk
        updated_translation = True
    if desc_en and desc_en != l.description_en:
        l.description_en = desc_en
        updated_translation = True
    if desc_uk and desc_uk != l.description_uk:
        l.description_uk = desc_uk
        updated_translation = True

    # --- адрес (не влияет на is_translated, но сохраняем если есть) ---
    if not l.address and "address" in (result or {}):
        addr = result.get("address")
        if addr and addr != l.address:
            l.address = addr

    # --- комнаты (попробуем извлечь целое число) ---
    if not l.rooms and "rooms" in (result or {}):
        rooms_raw = result.get("rooms")
        new_rooms = _coerce_rooms(rooms_raw)
        if new_rooms is not None and new_rooms != l.rooms:
            l.rooms = new_rooms

    # --- финальный флаг переведённости ---
    if updated_translation and not l.is_translated:
        l.is_translated = True

    return updated_translation


def _coerce_rooms(value) -> int | None:
    """
    Преобразует rooms из ответа ИИ в int.
    Поддерживает:
      - целое число (3)
      - строку с числом в начале/внутри ("3 pokoje", "rooms: 2", "1-комнатная")
    Если не получилось — вернёт None.
    """
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        try:
            iv = int(value)
            return iv
        except Exception:
            return None
    if isinstance(value, str):
        # ищем первое целое в строке
        import re
        m = re.search(r"\d+", value)
        if m:
            try:
                return int(m.group(0))
            except Exception:
                return None
    return None



def start_translation(stop_event: Event) -> None:
    """
    Обрабатывает по ОДНОМУ листингу за итерацию:
    1) claim: SELECT ... FOR UPDATE SKIP LOCKED LIMIT 1
    2) перевод
    3) запись и коммит
    """
    logger.info("Translator (one-by-one) started")
    try:
        while not stop_event.is_set():
            with get_sync_session() as session:
                l = _claim_one(session)
                if l is None:
                    session.rollback()
                    logger.info("Нет листингов для перевода. Спим %s сек.", IDLE_SLEEP)
                    sleep(IDLE_SLEEP)
                    continue

                try:
                    payload = _build_ai_input(l)
                    result = process_listing_one_call(payload)
                
                    if not isinstance(result, dict):
                        logger.warning("AI вернул не dict для id=%s — откатываем", l.id)
                        session.rollback()
                        sleep(ROW_SLEEP)
                        continue

                    changed = _apply_translations(l, result)
                    if changed:
                        session.add(l)
                        session.commit()
                        logger.info("✅ Translated listing id=%s", l.id)
                    else:
                        session.rollback()
                        logger.info("ℹ️ Нечего обновлять для id=%s", l.id)

                except Exception:
                    logger.exception("Ошибка перевода id=%s, откат", getattr(l, "id", "?"))
                    session.rollback()

            # лёгкий троттлинг между итерациями (даже если что-то переводили)
            sleep(ROW_SLEEP)

    except Exception as e:
        logger.exception("Translator FATAL: %s", e)
    finally:
        logger.info("Translator stopped cleanly")

# ai/ai_module.py
from __future__ import annotations

import json
import time
import unicodedata
from typing import Optional, Dict, Any, List, Iterable

from pydantic import BaseModel, Field, ValidationError
from openai import OpenAI
from openai._exceptions import (
    APIError,
    RateLimitError,
    APITimeoutError,
    APIConnectionError,
)
from config import OPENAI_API_KEY

# ============ Конфигурация ============
OPENAI_MODEL = "gpt-5-mini"   # ← как просил

if not OPENAI_API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY in environment")

client = OpenAI(api_key=OPENAI_API_KEY)


# ============ Схемы данных ============
class InputData(BaseModel):
    title: str
    description: str
    city: str

class LangBlock(BaseModel):
    title: str
    description: str

class TranslationBlock(BaseModel):
    uk: LangBlock
    en: LangBlock

class ParsedAddress(BaseModel):
    full: Optional[str] = Field(None, description="Город, Район, Улица, Дом (PL)")
    city: Optional[str] = None
    district: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    evidence: Optional[List[str]] = None

class StructExtraction(BaseModel):
    address: ParsedAddress
    rooms: Optional[int] = None

class Result(BaseModel):
    address: Optional[str] = None
    rooms: Optional[int] = None
    translation: TranslationBlock


# ============ Утилиты ============
def _with_retries(fn, max_retries: int = 3, base_delay: float = 0.8):
    attempt = 0
    while True:
        try:
            return fn()
        except (RateLimitError, APITimeoutError, APIConnectionError, APIError):
            attempt += 1
            if attempt > max_retries:
                raise
            time.sleep(base_delay * attempt)

def _json_call(messages) -> dict:
    """
    Унифицированный вызов под gpt-5-mini с обязательным JSON-ответом.
    """
    resp = _with_retries(
        lambda: client.chat.completions.create(
            model=OPENAI_MODEL,
            response_format={"type": "json_object"},
            messages=messages,
        )
    )
    raw = resp.choices[0].message.content or "{}"
    try:
        return json.loads(raw)
    except Exception:
        return {}


# ============ Вспомогалки для places ============
def _norm_key(s: str) -> str:
    return unicodedata.normalize("NFKC", s).casefold().strip()

def _ascii_fallback(s: str) -> str:
    # убираем диакритику для англ. фолбэка
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")

def _batched(iterable: Iterable[str], size: int):
    batch = []
    for x in iterable:
        if x is None:
            continue
        y = x.strip()
        if not y:
            continue
        batch.append(y)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch

# Сиды для устойчивости на топ-городах (и совпадающих экзонимах)
_SEED_EN = {
    "Warszawa": "Warsaw", "Kraków": "Krakow", "Łódź": "Lodz",
    "Wrocław": "Wroclaw", "Poznań": "Poznan", "Gdańsk": "Gdansk",
    "Szczecin": "Szczecin", "Katowice": "Katowice",
}
_SEED_UK = {
    "Warszawa": "Варшава", "Kraków": "Краків", "Łódź": "Лодзь",
    "Wrocław": "Вроцлав", "Poznań": "Познань", "Gdańsk": "Гданськ",
    "Szczecin": "Щецин", "Katowice": "Катовіце",
}


# ============ Перевод городов/районов ============
def translate_places(places: list[str], batch_size: int = 200) -> dict[str, dict[str, str]]:
    """
    Переводит список топонимов (PL) -> словарь:
    { original: {"uk": <укр>, "en": <англ>} }

    Без tools; только строгий JSON. Гарантирует ключи для всех входов.
    """
    if not places:
        return {}

    seen, ordered = {}, []
    for p in places:
        if not p:
            continue
        k = p.strip()
        if not k:
            continue
        low = _norm_key(k)
        if low not in seen:
            seen[low] = k
            ordered.append(k)

    out: dict[str, dict[str, str]] = {}

    SYSTEM = (
        "You translate Polish place names (cities or intracity districts).\n"
        "English: use established exonyms if they exist (Warszawa->Warsaw, Kraków->Krakow, Łódź->Lodz, "
        "Wrocław->Wroclaw, Poznań->Poznan, Gdańsk->Gdansk). If no exonym exists, remove diacritics (ASCII).\n"
        "Ukrainian: use established exonyms if they exist (Warszawa->Варшава, Kraków->Краків, Łódź->Лодзь, "
        "Wrocław->Вроцлав, Poznań->Познань, Gdańsk->Гданськ); otherwise provide a natural Ukrainian transcription.\n"
        "Return ONLY JSON object: {'mapping': {original: {'uk': str, 'en': str}}} for ALL inputs. "
        "Keys MUST exactly match the input strings."
    )

    for chunk in _batched(ordered, batch_size):
        USER = "Input (JSON array of strings):\n" + json.dumps(chunk, ensure_ascii=False)

        data = _json_call(
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": USER},
            ]
        )
        mapping = data.get("mapping") or {}

        # слияние + сиды + ASCII fallback
        for orig in chunk:
            trans = mapping.get(orig) or {}
            uk = (trans.get("uk") or "").strip()
            en = (trans.get("en") or "").strip()

            if not uk and orig in _SEED_UK:
                uk = _SEED_UK[orig]
            if not en and orig in _SEED_EN:
                en = _SEED_EN[orig]

            # если EN == оригинал и есть диакритики, убираем диакритику
            if en == orig and any(ord(c) > 127 for c in en):
                en = _ascii_fallback(en)

            if not uk:
                uk = orig  # крайний фолбэк
            if not en:
                en = _ascii_fallback(orig) or orig

            out[orig] = {"uk": uk, "en": en}

    return out


# ============ Основная функция: всё за один запрос ============
def process_listing_one_call(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Один вызов к OpenAI (без tools): извлекаем адрес/комнаты + переводы UK/EN.
    Возвращает строго нужный JSON (приводится к Result).
    """
    inp = InputData(**data)

    SYSTEM = (
        "You process a Polish real-estate listing. Return ONLY JSON with keys: "
        "{'address': str|null, 'rooms': int|null, "
        "'translation': {'uk': {'title': str, 'description': str}, "
        "'en': {'title': str, 'description': str}}}.\n"
        "Address: Polish, format 'Miasto, Dzielnica, Ulica, Numer' (omit missing parts). "
        "Rooms: integer; 'kawalerka/studio' and 'pokój do wynajęcia' = 1. "
        "Preserve meaning, numbers, addresses in translations."
    )
    USER = (
        f"City (hint): {inp.city}\n"
        f"Title (PL): {inp.title}\n"
        f"Description (PL): {inp.description}\n"
        "Return ONLY the JSON object described above."
    )

    data_json = _json_call(
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER},
        ]
    )

    # Мягкая нормализация rooms, если пришло строкой
    rooms = data_json.get("rooms", None)
    if isinstance(rooms, str) and rooms.isdigit():
        data_json["rooms"] = int(rooms)

    # Валидация по pydantic
    try:
        res = Result.model_validate(data_json)
    except ValidationError:
        # Попробуем мягко достроить блок translation
        tr = data_json.get("translation") or {}
        for lang in ("uk", "en"):
            block = tr.get(lang) or {}
            block["title"] = block.get("title") or ""
            block["description"] = block.get("description") or ""
            tr[lang] = block
        data_json["translation"] = tr
        res = Result.model_validate(data_json)

    return res.model_dump()

# ai/ai_module.py
from __future__ import annotations

import json
import time
from typing import Optional, Dict, Any, List, Iterable
import unicodedata

from pydantic import BaseModel, Field, ValidationError
from openai import OpenAI
from openai._exceptions import APIError, RateLimitError, APITimeoutError, APIConnectionError
from config import OPENAI_API_KEY

# ============ Конфигурация ============
OPENAI_MODEL = "gpt-4o-mini"


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


def _tool_schema_translate_places():
    return {
        "type": "function",
        "function": {
            "name": "places_translation",
            "description": (
                "Return mapping from original Polish place names to translations: "
                "{original: {uk: <Ukrainian>, en: <English>}}."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "mapping": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "uk": {"type": "string"},
                                "en": {"type": "string"},
                            },
                            "required": ["uk", "en"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["mapping"],
                "additionalProperties": False
            }
        }
    }

_PLACES_SYSTEM = (
    "You are a precise, context-aware translator for Polish geographic names (cities/districts within cities). "
    "For English: use common exonyms where they exist (e.g., 'Warszawa' -> 'Warsaw'). "
    "If no established English exonym exists, keep the original Polish form (do NOT transliterate). "
    "For Ukrainian: use common/official exonyms where they exist (e.g., 'Warszawa' -> 'Варшава'). "
    "If no established Ukrainian exonym exists, provide a natural Ukrainian transcription (do NOT invent new names). "
    "Return ONLY via function call."
)

_PLACES_USER_TMPL = (
    "Translate the following Polish place names (cities or intracity districts) to Ukrainian and English.\n"
    "Rules recap:\n"
    "- English: use established exonyms; otherwise keep original Polish.\n"
    "- Ukrainian: use established exonyms; otherwise provide a natural transcription.\n"
    "Input list (JSON array of strings):\n{json_list}"
)

def _batched(iterable: Iterable[str], size: int):
    batch = []
    for x in iterable:
        batch.append(x)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch

def _norm_key(s: str) -> str:
    # Унифицированная нормализация: убираем различия регистра и формы Unicode
    return unicodedata.normalize("NFKC", s).casefold().strip()

def translate_places(places: list[str], batch_size: int = 200) -> dict[str, dict[str, str]]:
    if not places:
        return {}

    # 1) Устраняем дубликаты, ведём маппинг "нормализованный ключ" -> "оригинал"
    seen: dict[str, str] = {}
    ordered: list[str] = []
    for p in places:
        if not p:
            continue
        key = p.strip()
        if not key:
            continue
        low = _norm_key(key)
        if low not in seen:
            seen[low] = key          # всегда помним ОРИГИНАЛЬНОЕ написание из входа
            ordered.append(key)

    result: dict[str, dict[str, str]] = {}

    for chunk in _batched(ordered, batch_size):
        # Локальная карта нормализованный->оригинал для именно этого чанка
        chunk_norm_map = {_norm_key(orig): orig for orig in chunk}

        user_msg = _PLACES_USER_TMPL.format(json_list=json.dumps(chunk, ensure_ascii=False))

        def _call():
            return client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0.1,
                messages=[
                    {"role": "system", "content": _PLACES_SYSTEM},
                    {"role": "user", "content": user_msg},
                ],
                tools=[_tool_schema_translate_places()],
                tool_choice={"type": "function", "function": {"name": "places_translation"}},
            )

        resp = _with_retries(_call)
        tool_calls = getattr(resp.choices[0].message, "tool_calls", None)

        if tool_calls:
            args = tool_calls[0].function.arguments or "{}"
            data = json.loads(args)
        else:
            def _call_fb():
                return client.chat.completions.create(
                    model=OPENAI_MODEL,
                    temperature=0.0,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": "Return ONLY a JSON {'mapping': {original: {'uk': str, 'en': str}}}."},
                        {"role": "user", "content": user_msg},
                    ],
                )
            fb = _with_retries(_call_fb)
            data = json.loads(fb.choices[0].message.content or "{}")

        mapping = data.get("mapping", {})

        # 2) Сливаем ответ модели, МЭППЯ по НОРМАЛИЗОВАННОМУ ключу
        for model_orig, trans in mapping.items():
            low = _norm_key(model_orig)
            # Prefer: оригинал из текущего чанка -> из всех входов -> слово из модели
            base_key = chunk_norm_map.get(low) or seen.get(low) or model_orig
            uk = trans.get("uk")
            en = trans.get("en")
            if isinstance(uk, str) and isinstance(en, str):
                result[base_key] = {"uk": uk, "en": en}

        # 3) Гарантируем наличие перевода для каждого элемента чанка
        for orig in chunk:
            if orig not in result:
                result[orig] = {"uk": orig, "en": orig}

    return result

# ============ Утилиты ============
def _with_retries(fn, max_retries: int = 3, base_delay: float = 0.8):
    attempt = 0
    while True:
        try:
            return fn()
        except (RateLimitError, APITimeoutError, APIConnectionError, APIError) as e:
            attempt += 1
            if attempt > max_retries:
                raise
            time.sleep(base_delay * attempt)

def _tool_schema_struct():
    """JSON-schema для function-calling: извлечение структуры."""
    return {
        "type": "function",
        "function": {
            "name": "extract_structure",
            "description": "Extracts address (PL) and number of rooms from Polish title/description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "object",
                        "properties": {
                            "full": {"type": ["string", "null"]},
                            "city": {"type": ["string", "null"]},
                            "district": {"type": ["string", "null"]},
                            "street": {"type": ["string", "null"]},
                            "house_number": {"type": ["string", "null"]},
                            "confidence": {"type": ["number", "null"], "minimum": 0.0, "maximum": 1.0},
                            "evidence": {"type": ["array", "null"], "items": {"type": "string"}}
                        },
                        "required": ["full"],
                        "additionalProperties": False
                    },
                    "rooms": {"type": ["integer", "null"]}
                },
                "required": ["address", "rooms"],
                "additionalProperties": False
            }
        }
    }

def _tool_schema_split_translation():
    """JSON-schema для чёткого разделения title/description после перевода."""
    return {
        "type": "function",
        "function": {
            "name": "pack_translation",
            "description": "Packs translated text into title and description fields.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["title", "description"],
                "additionalProperties": False
            }
        }
    }


# ============ Промпты ============
STRUCT_SYSTEM = (
    "Jesteś asystentem przetwarzającym ogłoszenia nieruchomości w Polsce. "
    "Zadania: (1) Wydobądź adres (miasto, dzielnica, ulica, numer) po polsku; (2) Policz liczbę pokoi. "
    "Jeśli brak danych — zwracaj null. Nie halucynuj. Zwracaj przez wywołanie funkcji."
)

STRUCT_USER_TMPL = (
    "Dane wejściowe (po polsku):\n"
    "Miasto (od klienta): {city}\n"
    "Tytuł: {title}\n"
    "Opis: {description}\n\n"
    "Wytyczne:\n"
    "- Adres po polsku; 'full' buduj: Miasto, Dzielnica, Ulica, Numer.\n"
    "- Kawalerka/studio = 1 pokój. Frazy 'pokój do wynajęcia' = 1.\n"
)

TRANSL_SYSTEM = (
    "You are a precise, context-aware translator from Polish. "
    "Preserve meaning, numbers, currency, addresses and real-estate terminology. "
    "Return the translation only."
)

TRANSL_USER_TMPL = (
    "Source title (PL): {title}\n"
    "Source description (PL): {description}\n"
    "Target language: {lang}"
)


# ============ Логика извлечения структуры ============
def _extract_structure(data: InputData) -> StructExtraction:
    def _call():
        return client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.1,
            messages=[
                {"role": "system", "content": STRUCT_SYSTEM},
                {"role": "user", "content": STRUCT_USER_TMPL.format(
                    city=data.city, title=data.title, description=data.description
                )},
            ],
            tools=[_tool_schema_struct()],
            tool_choice={"type": "function", "function": {"name": "extract_structure"}},
        )

    resp = _with_retries(_call)

    # Извлекаем tool_call arguments
    try:
        tool_calls = resp.choices[0].message.tool_calls
    except Exception:
        tool_calls = None

    if not tool_calls or not len(tool_calls):
        # fallback: попросим строгий JSON текстом
        # (в редких случаях модель не инициирует tool_call)
        def _call_fallback():
            return client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0.1,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "Return ONLY a JSON with keys address and rooms."},
                    {"role": "user", "content": STRUCT_USER_TMPL.format(
                        city=data.city, title=data.title, description=data.description
                    )},
                ],
            )
        fb = _with_retries(_call_fallback)
        raw_json = fb.choices[0].message.content or "{}"
        parsed = json.loads(raw_json)
        return StructExtraction.model_validate(parsed)

    args = tool_calls[0].function.arguments or "{}"
    parsed = json.loads(args)
    return StructExtraction.model_validate(parsed)


# ============ Перевод (PL→target) + упаковка ============
def _translate_pl(title_pl: str, description_pl: str, target_lang_code: str) -> LangBlock:
    lang_map = {"uk": "Ukrainian", "en": "English"}
    target_lang = lang_map.get(target_lang_code, "English")

    def _call_translate():
        return client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.1,
            messages=[
                {"role": "system", "content": TRANSL_SYSTEM},
                {"role": "user", "content": TRANSL_USER_TMPL.format(
                    title=title_pl, description=description_pl, lang=target_lang
                )},
            ],
        )

    tr = _with_retries(_call_translate)
    translated_text = tr.choices[0].message.content or ""

    # Просим модель распаковать в JSON через function-calling
    def _call_pack():
        return client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.0,
            messages=[
                {"role": "system", "content": f"Return ONLY via function call a JSON with 'title' and 'description' in {target_lang}."},
                {"role": "user", "content": translated_text},
            ],
            tools=[_tool_schema_split_translation()],
            tool_choice={"type": "function", "function": {"name": "pack_translation"}},
        )

    pack = _with_retries(_call_pack)
    tool_calls = pack.choices[0].message.tool_calls
    if not tool_calls:
        # запасной вариант: попросим json_object
        def _call_pack_fb():
            return client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0.0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": f"Return JSON with 'title' and 'description' in {target_lang}."},
                    {"role": "user", "content": translated_text},
                ],
            )
        pfb = _with_retries(_call_pack_fb)
        raw = pfb.choices[0].message.content or "{}"
        out = json.loads(raw)
        return LangBlock(**out)

    args = tool_calls[0].function.arguments or "{}"
    out = json.loads(args)
    return LangBlock(**out)


# ============ Публичная функция ============
def process_listing(data: Dict[str, Any]) -> Dict[str, Any]:
    inp = InputData(**data)

    struct = _extract_structure(inp)
    uk = _translate_pl(inp.title, inp.description, "uk")
    en = _translate_pl(inp.title, inp.description, "en")

    return Result(
        address=struct.address.full,
        rooms=struct.rooms,
        translation=TranslationBlock(uk=uk, en=en),
    ).model_dump()


def process_listing_one_call(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Один запрос к OpenAI: извлекаем адрес/комнаты + переводы UK/EN.
    Возвращает строго нужный JSON.
    """
    inp = InputData(**data)

    tool_schema = {
        "type": "function",
        "function": {
            "name": "process_all",
            "description": "Extract address and rooms from PL text and translate title/description to UK and EN.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {"type": ["string", "null"], "description": "Адрес на польском: 'город, район, улица, дом'"},
                    "rooms": {"type": ["integer", "null"], "description": "Количество комнат (int), если есть"},
                    "translation": {
                        "type": "object",
                        "properties": {
                            "uk": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                },
                                "required": ["title", "description"],
                                "additionalProperties": False
                            },
                            "en": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                },
                                "required": ["title", "description"],
                                "additionalProperties": False
                            },
                        },
                        "required": ["uk", "en"],
                        "additionalProperties": False
                    }
                },
                "required": ["address", "rooms", "translation"],
                "additionalProperties": False
            }
        }
    }

    SYSTEM = (
        "Jesteś asystentem do ogłoszeń nieruchomości w Polsce. "
        "Z jednego wejścia wykonaj: (1) wydobądź adres po polsku w formacie 'Miasto, Dzielnica, Ulica, Numer' (jeśli brak elementu — pomiń), "
        "(2) policz liczbę pokoi (kawalerka/studio = 1; 'pokój do wynajęcia' = 1), "
        "(3) przetłumacz tytuł i opis z polskiego na ukraiński i angielski, zachowując sens, liczby, adresy i terminy nieruchomości. "
        "Zwróć TYLKO poprzez wywołanie funkcji."
    )

    USER = (
        f"Dane wejściowe (PL):\n"
        f"Miasto (od klienta): {inp.city}\n"
        f"Tytuł: {inp.title}\n"
        f"Opis: {inp.description}\n\n"
        f"Wytyczne adresu:\n"
        f"- Zwracaj po polsku, format: Miasto, Dzielnica, Ulica, Numer (tylko to, co pewne).\n"
        f"- Jeśli nic не udało się pewnie ustalić — address=null.\n"
        f"Wytyczne pokoi:\n"
        f"- Liczba całkowita, jeśli w tekście. Kawalerka/studio i 'pokój do wynajęcia' = 1.\n"
        f"Tłumaczenia:\n"
        f"- UK i EN — oddaj jako pola translation.uk i translation.en z title/description."
    )

    def _call():
        return client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": USER},
            ],
            tools=[tool_schema],
            tool_choice={"type": "function", "function": {"name": "process_all"}},
        )

    resp = _with_retries(_call)

    tool_calls = getattr(resp.choices[0].message, "tool_calls", None)
    if tool_calls:
        args = tool_calls[0].function.arguments or "{}"
        out = json.loads(args)
    else:
        # Fallback: попросим json_object, если tool не сработал.
        def _call_fb():
            return client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0.0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "Return ONLY a JSON with keys: address, rooms, translation.uk{title,description}, translation.en{title,description}."},
                    {"role": "user", "content": USER},
                ],
            )
        fb = _with_retries(_call_fb)
        out = json.loads(fb.choices[0].message.content or "{}")

    # Валидация и приведение к нужной финальной структуре:
    try:
        res = Result.model_validate(out)
    except ValidationError:
        # Попробуем мягко привести типы (например, если rooms строкой)
        rooms = out.get("rooms", None)
        if isinstance(rooms, str) and rooms.isdigit():
            out["rooms"] = int(rooms)
        res = Result.model_validate(out)

    return res.model_dump()


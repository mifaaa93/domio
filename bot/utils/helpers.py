import re
from decimal import Decimal, InvalidOperation

# Синонимы суффиксов
_SUFFIX_ALIASES = [
    (r"(?:tys|тыс|тис)\.?", "k"),
    (r"(?:mln|млн|m)\.?", "m"),
    (r"(?:mld|млрд|bn|b)\.?", "b"),
]

# Слова/символы валют, которые можно выбросить
_CURRENCY_RE = re.compile(
    r"(uah|грн|₴|pln|zł|zl|usd|\$|eur|€|руб|₽|₸|kzt|ron|lei|czk|₫|vnd|gbp|£)",
    re.IGNORECASE
)

def parse_price(text: str) -> int | None:
    """
    Парсит цену из произвольной строки.
    Поддерживает:
      - 12000, 12 000, 12,000, 12.000  -> 12000
      - 12k, 12.5k -> 12000, 12500
      - 1.2m / 1,2 mln / 1.2 млн -> 1_200_000
      - 0.8b / 0,8 млрд -> 800_000_000
    Возвращает int или None.
    """
    if not text:
        return None

    t = text.strip()

    # Нормализация: унифицируем десятичный разделитель к точке
    t = t.replace("\u00A0", " ")  # неразрывный пробел
    t = t.replace(",", ".")
    t = _CURRENCY_RE.sub("", t.lower())

    # Приводим словесные суффиксы к k/m/b
    for pat, repl in _SUFFIX_ALIASES:
        t = re.sub(pat, repl, t, flags=re.IGNORECASE)

    # Если диапазон "10-12k" — берём первую часть до дефиса
    t = re.split(r"[–—-]", t, maxsplit=1)[0].strip()

    # Ищем число + необязательный суффикс k/m/b
    m = re.search(r"(?P<num>\d+(?:[ \u202F.\u2009]\d{3})*|\d+(?:\.\d+)?)(?P<suf>[kmb]?)", t)
    if not m:
        return None

    num, suf = m.group("num"), m.group("suf")

    # Если это формат с разделителями тысяч (1.234.567 или 1 234 567) и без десятичной части — уберём всё, кроме цифр
    if suf == "" and re.fullmatch(r"\d{1,3}(?:[ \u202F.\u2009]\d{3})+", num):
        digits_only = re.sub(r"\D", "", num)
        try:
            return int(digits_only)
        except ValueError:
            return None

    # Иначе — обычное десятичное число (мог быть записан как 12.5)
    try:
        base = Decimal(re.sub(r"[^\d.]", "", num))
    except InvalidOperation:
        return None

    # Суффиксы: k = *1000, m = *1_000_000, b = *1_000_000_000
    if   suf == "k":
        base *= 1_000
    elif suf == "m":
        base *= 1_000_000
    elif suf == "b":
        base *= 1_000_000_000

    try:
        return int(base)
    except (OverflowError, ValueError):
        return None

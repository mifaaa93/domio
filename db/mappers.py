# db/mappers_min.py
from __future__ import annotations
from typing import Any, Dict, Optional
import re
from bs4 import BeautifulSoup

from sqlalchemy.orm import Session
from db.repo import upsert_city_by_name_pl, upsert_district_by_name_pl

from config import CITIES_STR, PETS_PHRASE, CHILD_PHRASE, PETS_CHILD_PHRASE, NO_COMISSION_PHRASE

ROOMS_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,   # "4 i więcej" → нижняя граница
    "five": 5,
    "more": 10,  # "więcej niż 10"
}

def exctract_text_from_html(raw_text: str) -> str:
    '''
    '''
    if raw_text:
        try:
            soup = BeautifulSoup(raw_text, 'lxml')
            return soup.text
        except Exception as e:
            pass
    return raw_text


def pets_child_comission_from_desc(desc: str | None, title: str | None) -> tuple[bool | None, bool | None]:
    """
    Ищет фразы из PETS_PHRASE, CHILD_PHRASE, PETS_CHILD_PHRASE
    в описании и названии. Если фраза найдена — ставим False
    (запрещено). Если ничего не найдено — остаётся None.
    """
    pets_allowed = None
    child_allowed = None
    no_comission = None

    text = f"{desc or ''} {title or ''}".lower()
    if any(p in text for p in NO_COMISSION_PHRASE):
        no_comission = True

    # если есть фраза, где запрещено и то, и то
    if any(p in text for p in PETS_CHILD_PHRASE):
        pets_allowed = False
        child_allowed = False
        return pets_allowed, child_allowed

    # отдельно проверяем животных
    if any(p in text for p in PETS_PHRASE):
        pets_allowed = False

    # отдельно проверяем детей
    if any(p in text for p in CHILD_PHRASE):
        child_allowed = False

    return pets_allowed, child_allowed, no_comission


def _norm_url(u: str | None) -> str | None:
    if not u: return None
    return u.strip().rstrip('/')



def map_olx_to_listing(
    session: Session,
    offer: Dict[str, Any],
    *,
    property_type: str = "apartment",   # apartment | house | room  (совместимо с CheckConstraint)
    deal_type: str = "sale",            # rent | sale (можно менять в парсере)
    ) -> Dict[str, Any]:
    """
    Преобразует OLX JSON-объект в dict для модели Listing.
    Город/район апсертятся по польским названиям и возвращаются как FK.
    """
    source = "olx"
    source_ad_id = str(offer.get("id"))
    url = _norm_url(offer.get("url"))
    external_url = _norm_url(offer.get("external_url"))

    title = exctract_text_from_html(offer.get("title"))
    description = exctract_text_from_html(offer.get("description"))

    # --- Локация ---
    loc = offer.get("location") or {}
    city_name_pl = ((loc.get("city") or {}).get("name")) or "Unknown"
    city_name_pl = city_name_pl.strip().title()
    if city_name_pl not in CITIES_STR:
        return None
    city_id = upsert_city_by_name_pl(session, name_pl=city_name_pl)

    district_id = None
    district_name_pl: str = (loc.get("district") or {}).get("name")
    if district_name_pl:
        district_name_pl = district_name_pl.strip().title()
        district_id = upsert_district_by_name_pl(session, city_id=city_id, name_pl=district_name_pl)

    address = None  # определим позже через GPT

    # --- Числовые/категориальные поля ---
    area_m2: Optional[float] = None
    rooms: Optional[int] = None
    price: Optional[float] = None

    pets_allowed, child_allowed, no_comission = pets_child_comission_from_desc(description, title)
    market: Optional[str] = None   # <-- инициализация!

    for p in offer.get("params", []) or []:
        key = p.get("key")
        val = p.get("value") or {}

        if key == "m":  # площадь
            raw = (val.get("key") or "").replace(",", ".")
            try:
                area_m2 = float(raw) if raw else None
            except Exception:
                pass

        elif key == "rooms":
            vk = (val.get("key") or "").lower()
            if vk in ROOMS_MAP:
                rooms = ROOMS_MAP[vk]
            else:
                lab = (val.get("label") or "")
                m = re.search(r"\d+", lab)
                rooms = int(m.group(0)) if m else rooms

        elif key == "price":
            v = val.get("value")
            try:
                price = float(v) if v is not None else price
            except Exception:
                pass

        elif key in ("pets", "animals"):
            k = (val.get("key") or "")
            if k in ("Tak", "Nie"):
                pets_allowed = (k == "Tak")

        elif key == "market":
            # напр. 'primary'/'secondary' (зависит от источника)
            market = (val.get("key") or "").strip() or None

    # --- Фото ---
    photos = []
    for ph in offer.get("photos") or []:
        link = ph.get("link")
        w = ph.get("width")
        h = ph.get("height")
        if link and w and h:
            photos.append(link.replace("{width}", str(w)).replace("{height}", str(h)))
        elif link:
            photos.append(link.replace("{width}", "1024").replace("{height}", "768"))
    photos = photos or None


    return dict(
        source=source,
        source_ad_id=source_ad_id,
        property_type=property_type,
        deal_type=deal_type,
        title=title,
        description=description,
        url=url,
        external_url=external_url,
        city_id=city_id,
        district_id=district_id,
        address=address,
        area_m2=area_m2,
        rooms=rooms,
        price=price,
        market=market,
        pets_allowed=pets_allowed,
        child_allowed=child_allowed,
        photos=photos,
        no_comission=no_comission,
        raw=offer,
    )

def map_otodom_to_listing(
    session: Session,
    ad: Dict[str, Any],
    *,
    property_type: str = "apartment",   # apartment | house | room
    deal_type: str = "sale",            # sale | rent
) -> Dict[str, Any]:
    """
    Преобразует Otodom ad (из props.pageProps.ad) в dict для модели Listing.
    Город/район апсертятся по PL-названиям и возвращаются как FK.
    """

    # ---------- базовые ----------
    source = "otodom"
    source_ad_id = str(ad.get("id") or ad.get("publicId") or "")
    url = _norm_url(ad.get("url") or ad.get("relativeUrl"))
    external_url = None  # у otodom обычно нет внешней карты ссылок на карточке

    # ---------- заголовок/описание ----------
    title_raw = ad.get("title")
    description_html = ad.get("description")
    title = exctract_text_from_html(title_raw) if isinstance(title_raw, str) else title_raw
    description = exctract_text_from_html(description_html)

    # ---------- deal_type / property_type (переопределим, если точно знаем) ----------
    # ad.adCategory: {"name": "FLAT","type": "SELL"}
    cat = (ad.get("adCategory") or {})
    cat_name = (cat.get("name") or "").upper()
    cat_type = (cat.get("type") or "").upper()

    # property_type
    if cat_name == "FLAT":         property_type = "apartment"
    elif cat_name == "HOUSE":      property_type = "house"
    elif cat_name == "ROOM":       property_type = "room"

    # deal_type
    if cat_type == "SELL":         deal_type = "sale"
    elif cat_type == "RENT":       deal_type = "rent"

    # ---------- локация ----------
    # ad.location.address.city.name / district.name / street.name
    loc = ad.get("location") or {}
    addr = loc.get("address") or {}

    city_name_pl = (
        ((addr.get("city") or {}).get("name"))
        or (ad.get("adTrackingData") or {}).get("city_name")
    )
    city_name_pl = city_name_pl.strip().title()
    if city_name_pl not in CITIES_STR:
        return None
    city_id = upsert_city_by_name_pl(session, name_pl=city_name_pl)

    district_id = None
    district_name_pl = (addr.get("district") or {}).get("name")
    if district_name_pl:
        district_name_pl = district_name_pl.strip().title()
        district_id = upsert_district_by_name_pl(session, city_id=city_id, name_pl=district_name_pl)

    # address (строковое поле модели) — положим улицу, если она есть
    street_name = (addr.get("street") or {}).get("name")
    address = street_name.strip() if isinstance(street_name, str) and street_name.strip() else None

    # ---------- цена / валюта ----------
    price = None
    currency = None
    for ch in ad.get("characteristics") or []:
        if ch.get("key") == "price":
            # value = "559000", currency="PLN"
            v = ch.get("value")
            try:
                price = float(str(v).replace(",", "."))
            except Exception:
                price = None
            currency = ch.get("currency") or currency
            break
    if price is None:
        # запасной путь из target.Price (int)
        v = (ad.get("target") or {}).get("Price")
        try:
            price = float(v) if v is not None else None
        except Exception:
            price = None

    # ---------- комнаты ----------
    rooms = None
    prop = ad.get("property") or {}
    props = prop.get("properties") or {}
    if "numberOfRooms" in props:
        try:
            rooms = int(props["numberOfRooms"])
        except Exception:
            rooms = None
    if rooms is None:
        # запасной путь через characteristics
        for ch in ad.get("characteristics") or []:
            if ch.get("key") == "rooms_num":
                try:
                    rooms = int(float(str(ch.get("value")).replace(",", ".")))
                except Exception:
                    rooms = None
                break
    if rooms is None:
        v = (ad.get("target") or {}).get("Rooms_num")
        try:
            rooms = int(float(str(v).replace(",", "."))) if v is not None else None
        except Exception:
            rooms = None

    # ---------- площадь ----------
    area_m2 = None
    area_obj = prop.get("area")
    if isinstance(area_obj, dict) and "value" in area_obj:
        try:
            area_m2 = float(str(area_obj["value"]).replace(",", "."))
        except Exception:
            area_m2 = None
    if area_m2 is None:
        # запасные пути
        for ch in ad.get("characteristics") or []:
            if ch.get("key") in ("m", "area", "powierzchnia"):
                try:
                    area_m2 = float(str(ch.get("value")).replace(",", "."))
                except Exception:
                    area_m2 = None
                break
        if area_m2 is None:
            v = (ad.get("target") or {}).get("Area")
            try:
                area_m2 = float(str(v).replace(",", ".")) if v is not None else None
            except Exception:
                area_m2 = None

    # ---------- рынок / pets ----------
    # рынок есть и в ad.market ("SECONDARY") и в characteristics (market::secondary)
    market = None
    if isinstance(ad.get("market"), str) and ad.get("market"):
        market = ad["market"].lower()  # 'secondary' | 'primary'
    else:
        for ch in ad.get("characteristics") or []:
            if ch.get("key") == "market":
                market = (ch.get("value") or "").lower() or market
                break

    pets_allowed, child_allowed, no_comission = pets_child_comission_from_desc(description, title)
    # ---------- фото ----------
    photos: list[str] = []
    for img in ad.get("images") or []:
        if isinstance(img, dict):
            u = img.get("large") or img.get("medium") or img.get("small") or img.get("thumbnail")
            if isinstance(u, str):
                photos.append(u)
    photos = photos or None

    return dict(
        source=source,
        source_ad_id=source_ad_id,
        property_type=property_type,
        deal_type=deal_type,
        title=title,
        description=description,
        url=url,
        external_url=external_url,
        city_id=city_id,
        district_id=district_id,
        address=address,
        area_m2=area_m2,
        rooms=rooms,
        price=price,
        market=market,
        pets_allowed=pets_allowed,
        child_allowed=child_allowed,
        photos=photos,        
        no_comission=no_comission,
        raw=ad,
    )


def map_morizon_to_listing(
    session: Session,
    offer: Dict[str, Any],
    *,
    property_type: str = "apartment",   # apartment | house | room
    deal_type: str = "sale",            # sale | rent
) -> Dict[str, Any]:
    """
    Преобразует разобранную карточку Morizon (dict из parse_morizon_card) к твоей модели Listing.
    """
    source = "morizon"
    source_ad_id = str(offer.get("source_ad_id") or "")
    url = offer.get("url")
    external_url = offer.get("external_url")

    title = offer.get("title")
    description = offer.get("description")

    # --- Локация ---
    city_name_pl = offer.get("city")
    city_id = upsert_city_by_name_pl(session, name_pl=city_name_pl)

    district_id = None
    district_name_pl: str = offer.get("district")
    if district_name_pl:
        district_id = upsert_district_by_name_pl(session, city_id=city_id, name_pl=district_name_pl)

    # Улица (как address в твоей модели)
    address = offer.get("street") or None

    # --- Числа ---
    area_m2 = offer.get("area_m2")
    try:
        area_m2 = float(area_m2) if area_m2 is not None else None
    except Exception:
        area_m2 = None

    rooms = offer.get("rooms")
    try:
        rooms = int(rooms) if rooms is not None else None
    except Exception:
        rooms = None

    price = offer.get("price")
    try:
        price = float(price) if price is not None else None
    except Exception:
        price = None

    market = offer.get("market")          # на Morizon редко явно есть рынок в карточке
    
    pets_allowed, child_allowed, no_comission = pets_child_comission_from_desc(description, title)

    photos = offer.get("images") or None

    return dict(
        source=source,
        source_ad_id=source_ad_id or url,
        property_type=property_type,
        deal_type=deal_type,
        title=title,
        description=description,
        url=url,
        external_url=external_url,
        city_id=city_id,
        district_id=district_id,
        address=address,
        area_m2=area_m2,
        rooms=rooms,
        price=price,
        market=market,
        pets_allowed=pets_allowed,
        child_allowed=child_allowed,
        no_comission=no_comission,
        photos=photos,
        raw=offer,   # сохраняем разобранный payload
    )


def map_nieruch_to_listing(
    session: Session,
    offer: Dict[str, Any],
    *,
    property_type: str = "apartment",   # apartment | house | room
    deal_type: str = "sale",            # sale | rent
) -> Dict[str, Any]:
    """
    Преобразует разобранную карточку nieruchomosci-online.pl (dict из parse_nieruch_card)
    к единому формату Listing.
    """
    source = "nieruch"
    source_ad_id = str(offer.get("source_ad_id") or "")
    url = offer.get("url")
    external_url = offer.get("external_url")

    title = offer.get("title")
    description = offer.get("description")

    # --- Локация ---
    city_name_pl = offer.get("city")
    city_id = upsert_city_by_name_pl(session, name_pl=city_name_pl)

    district_id = None
    district_name_pl: str = offer.get("district")
    if district_name_pl:
        district_id = upsert_district_by_name_pl(session, city_id=city_id, name_pl=district_name_pl)

    address = offer.get("street") or None

    # --- Числовые параметры ---
    def to_float(value):
        try:
            return float(str(value).replace(",", ".").strip()) if value not in (None, "", "null") else None
        except Exception:
            return None

    def to_int(value):
        try:
            return int(value)
        except Exception:
            return None

    area_m2 = to_float(offer.get("area_m2"))
    rooms = to_int(offer.get("rooms"))
    price = to_float(offer.get("price"))

    market = offer.get("market")  # 'primary' | 'secondary' или None
    pets_allowed, child_allowed, no_comission = pets_child_comission_from_desc(description, title)
    # --- Фото ---
    images = offer.get("images") or None

    return dict(
        source=source,
        source_ad_id=source_ad_id or url,
        property_type=property_type,
        deal_type=deal_type,
        title=title,
        description=description,
        url=url,
        external_url=external_url,
        city_id=city_id,
        district_id=district_id,
        address=address,
        area_m2=area_m2,
        rooms=rooms,
        price=price,
        market=market,
        pets_allowed=pets_allowed,
        child_allowed=child_allowed,
        no_comission=no_comission,
        photos=images,
        raw=offer,   # сохраняем оригинальный словарь
    )
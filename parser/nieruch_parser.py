# parser/nieruch_parser.py
import logging
from time import sleep
from random import randint
from typing import Dict, List, Tuple, DefaultDict, Optional
from collections import defaultdict
import re
import json
from threading import Event

from bs4 import BeautifulSoup

from net.http_client import http_get
from db.session import get_sync_session
from db.repo import add_listing, filter_new_urls
from db.mappers import map_nieruch_to_listing
from config import CITY_IDS_NIERUCH, PROP_TYPES_NIERUCH, parser_pause

logger = logging.getLogger("nieruchomosci")

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "pl,ru;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "sec-ch-ua": "\"Google Chrome\";v=\"141\", \"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"141\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "upgrade-insecure-requests": "1"
}

# =======================
# Листинг (страница результатов)
# =======================

def build_nieruch_search_url(
    deal_type: str,      # "sale" | "rent"
    property_type: str,  # "apartment" | "house" | "room"
    city: str
) -> str:
    """
    deal_type: sale -> 'sprzedaz', rent -> 'wynajem'
    property_type: apartment -> 'mieszkania', house -> 'domy', room -> 'pokoje'
    """
    dmap = {"sale": "sprzedaz", "rent": "wynajem"}
    pmap = {"apartment": "mieszkania", "house": "dom", "room": "pokoj"}

    d = dmap.get(deal_type, "sprzedaz")
    p = pmap.get(property_type, "mieszkania")
    return f"https://www.nieruchomosci-online.pl/szukaj.html?3,{p},{d},,{city}&o=modDate,desc"
    return f"https://www.nieruchomosci-online.pl/szukaj.html?3,{p},{d},,{city},,,,,,,1&o=modDate,desc" # только частные


def extract_listing_urls_from_search_html(html: str) -> List[str]:
    """
    Извлекаем ссылки на карточки из выдачи.
    """
    soup = BeautifulSoup(html, "lxml")
    urls: set[str] = set()

    candidates = soup.find_all("h2", {"class": "name body-lg"})
    for item in candidates:
        href = item.find('a', href=True)
        if href:
            urls.add(href.get('href'))
    
    return list(urls)

def get_search_page_urls(*, deal_type: str, property_type: str, city: str) -> List[str]:
    url = build_nieruch_search_url(deal_type=deal_type, property_type=property_type, city=city)
    r = http_get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    return extract_listing_urls_from_search_html(r.text)

# =======================
# Карточка
# =======================
def _clean_text(s: Optional[str]) -> Optional[str]:
    if not s:
        return s
    return re.sub(r"\s+", " ", s).strip()

def _num_from_text(s: Optional[str]) -> Optional[float]:
    if not s:
        return None
    # допускаем пробелы/неразрывные пробелы/запятые
    m = re.search(r"(\d[\d\s\u00a0\u202f\.,]*)", s)
    if not m:
        return None
    raw = m.group(1)
    raw = raw.replace("\u00a0", " ").replace("\u202f", " ")
    raw = raw.replace(" ", "").replace(",", ".")
    try:
        return float(raw)
    except Exception:
        return None

def _dedupe_keep_order(urls: List[str]) -> List[str]:
    seen, out = set(), []
    for u in urls:
        if u and u not in seen:
            seen.add(u); out.append(u)
    return out

def images_from_box_gallery(gallery: BeautifulSoup) -> List[str]:
    """
    Достаёт фото из <ul class="box-gallery">... (как в примере).
    Возвращает список абсолютных URL без дублей, в правильном порядке.
    """
    if not gallery:
        return []
    # собираем (order_key, url)
    items: List[Tuple[int, str]] = []
    for li in gallery.find_all("li"):
        img = li.find("img")
    return _dedupe_keep_order([u for _, u in items])


def extract_images_from_handle_record(scripts: list[BeautifulSoup]) -> List[str]:
    """
    Извлекает ссылки на фото (jpg/png/webp) из блока `modules.record.handleRecord({...})`
    на nieruchomosci-online.pl.
    Работает без рендера JS.
    """
    photo_urls = []
    for script in scripts:
        if 'modules.record.handleRecord' in script.text:
            text = script.string

            # Находим JSON с "photos"
            match = re.search(r'photos\s*:\s*(\{.*?\}),\s*\n\t\tvideo', text, re.S)
            if not match:
                continue

            photos_raw = match.group(1)

            # Исправляем escape-последовательности
            photos_clean = photos_raw.replace('\\/', '/')

            # Попытка распарсить JSON
            try:
                photos = json.loads(photos_clean)
            except json.JSONDecodeError:
                # Если не получилось напрямую — подправим ключи
                photos_clean = re.sub(r'(\w+):', r'"\1":', photos_clean)
                photos = json.loads(photos_clean)

            # приоритет — "x", затем "l"
            urls = photos.get("x") or photos.get("l") or []
            urls = [u.replace('\\/', '/') for u in urls]

            # убираем дубли, сохраняя порядок
            unique_urls = list(dict.fromkeys(urls))

            photo_urls.extend(unique_urls)
            break
    return photo_urls

def _extract_details_table(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Блок «Szczegóły ogłoszenia»: <ul class="list-h"> внутри #detailsTable.
    Пары выглядят как <li><strong>Label:</strong> <span>Value</span></li>.
    Возвращаем {label_lower: value_text}.
    """
    res: Dict[str, str] = {}
    details = soup.select("#detailsTable ul.list-h li")
    for li in details:
        strong = li.find("strong")
        span = li.find("span")
        if not strong or not span:
            continue
        label = _clean_text(strong.get_text(" ", strip=True)).rstrip(":").lower()
        value = _clean_text(span.get_text(" ", strip=True))
        if label and value:
            res[label] = value
    return res

# ---------- основной парсер карточки ----------

def parse_nieruch_card(html: str, city_name: str, url: str) -> Dict:
    """
    Возвращает словарь:
    {
      "title", "description", "price", "area_m2", "rooms",
      "district", "street", "market", "images",
      "url", "external_url", "source_ad_id"
    }
    """
    soup = BeautifulSoup(html, "lxml")
    details = _extract_details_table(soup)

    # --- URL / ID ---
    # из /.../25923251.html вытащим id
    source_ad_id = None
    if url:
        m = re.search(r"/(\d+)\.html(?:[?#]|$)", url)
        if m:
            source_ad_id = m.group(1)

    # --- Заголовок ---
    # в верхнем блоке: h1.header-b.mod-c ...
    title = None
    h1 = soup.select_one(".box-offer-top h1, h1.header-b")
    if h1:
        title = _clean_text(h1.get_text(" ", strip=True))
    if not title:
        ogt = soup.find("meta", property="og:title")
        if ogt and ogt.get("content"):
            title = _clean_text(ogt["content"])

    # --- Цена / Площадь / Цена за м2 ---
    price = None
    pnode = soup.select_one(".info-primary-price")
    if pnode:
        price = _num_from_text(pnode.get_text(" ", strip=True))
    if price is None:
        # в «Szczegóły ogłoszenia»: <strong>Cena:</strong> <span>690 000 zł (...)</span>
        v = details.get("cena")
        if v:
            price = _num_from_text(v)

    area_m2 = None
    anode = soup.select_one(".info-area")
    if anode:
        area_m2 = _num_from_text(anode.get_text(" ", strip=True))
    if area_m2 is None:
        # ещё вариант в «Charakterystyka mieszkania»
        v = details.get("charakterystyka mieszkania")
        if v:
            # строка вида: "47,24 m², 3 pokoje; stan: ..."
            m = re.search(r"([\d\s\u00a0\u202f\.,]+)\s*m", v, flags=re.I)
            if m:
                area_m2 = _num_from_text(m.group(1))

    # --- Комнаты ---
    rooms = None
    # быстрый вариант: в таблице-«плашках»
    rnode = soup.select_one("#attributesTable .icon-data-rooms ~ .box__attributes--content .fsize-a")
    if rnode:
        rooms = int(_num_from_text(rnode.get_text(" ", strip=True)) or 0) or None
    if rooms is None:
        v = details.get("charakterystyka mieszkania")
        if v:
            # там же «..., 3 pokoje; ...»
            m = re.search(r"(\d+)\s*pokoje?|\b(\d+)\b", v, flags=re.I)
            if m:
                rooms = int(next(g for g in m.groups() if g))  # первая непустая группа

    # --- Market (Rynek) ---
    market = None
    v = details.get("rynek")
    if v:
        vv = v.strip().lower()
        if "pierwotn" in vv:        # pierwotny
            market = "primary"
        elif "wtórn" in vv or "wtorn" in vv or "wtor" in vv:  # wtórny
            market = "secondary"
        else:
            market = vv

    # --- Адрес: улица/район/город ---
    # 1) Верхняя строка под заголовком: ".title-b" (desktop) или <h2> под h1
    #    Пример: "Magiera, Bielany, Warszawa, mazowieckie"
    address = None
    district = None

    tline = soup.select_one("li.body-md.adress span") or soup.select_one(".box-offer-top h2.header-e, .box-offer-top h2")
    if tline:
        address = tline.text
    
    # --- Описание ---
    # Короткая/развёрнутая части в #boxCustomDesc
    description = None
    desc_box = soup.select_one("#boxCustomDesc")
    if desc_box:
        for sel in (".estate-desc-more", ".estate-desc-less",):
            node = desc_box.select_one(sel)
            if node:
                description = _clean_text(node.get_text("\n", strip=True)) or None
                break
    if not description:
        # общий фолбэк
        desc_any = soup.find(class_=re.compile(r"(desc|opis)", re.I))
        if desc_any:
            description = _clean_text(desc_any.get_text("\n", strip=True))

    # --- Фото ---
    images = extract_images_from_handle_record(soup.find_all("script", {"type": "text/javascript"})) or images_from_box_gallery(soup.find("ul", {"class": "box-gallery"}))

    return {
        "title": title,
        "description": description,
        "price": price,
        "area_m2": area_m2,
        "rooms": rooms,
        "district": district,
        "city": city_name,
        "address": address,
        "market": market,
        "images": images or None,
        "external_url": None,
        "source_ad_id": source_ad_id,
    }


def fetch_and_parse_card(url: str, *, city_name: str) -> Dict:
    r = http_get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    data = parse_nieruch_card(r.text, city_name=city_name, url=url)
    data["url"] = url
    return data

# =======================
# Пайплайн
# =======================

def collect_new_urls(last_ids: Dict[Tuple[str, str, str], set]) -> Dict[Tuple[str, str, str], List[str]]:
    res: Dict[Tuple[str, str, str], List[str]] = defaultdict(list)
    for city in CITY_IDS_NIERUCH:
        for property_type, deal_type in PROP_TYPES_NIERUCH:
            key = (city, property_type, deal_type)
            try:
                urls = get_search_page_urls(deal_type=deal_type, property_type=property_type, city=city)
                for u in urls:
                    if u not in last_ids[key]:
                        last_ids[key].add(u)
                        res[key].append(u)
                sleep(randint(1, 4))
            except Exception:
                logger.exception("search failed: city=%s prop=%s deal=%s",
                                 city, property_type, deal_type,
                                 exc_info=False)
    return res

def make_round(last_ids: Dict[Tuple[str, str, str], set]) -> None:
    try:
        all_urls = collect_new_urls(last_ids)
        total_found = sum(len(v) for v in all_urls.values())
        logger.info("Found nieruchomosci-online adds %s", total_found)
        total_added = 0
        with get_sync_session() as session:
            for key, urls in all_urls.items():
                city, property_type, deal_type = key
                new_urls = filter_new_urls(session, urls)
                for url in new_urls:
                    try:
                        card = fetch_and_parse_card(url, city_name=city)
                        listing = map_nieruch_to_listing(
                            session,
                            card,
                            property_type=property_type,
                            deal_type=deal_type,
                        )
                        if add_listing(session, listing):
                            total_added += 1
                            session.commit()
                    except Exception:
                        logger.exception("nieruch: failed card %s", url, exc_info=False)
                session.commit()
        logger.info("Added nieruchomosci-online adds %s", total_added)
    except Exception:
        logger.exception("make_round nieruch failed", exc_info=False)



def start_nieruch(stop_event: Event) -> None:
    last_ids: DefaultDict[Tuple[str, str, str], set] = defaultdict(set)
    logger.info("Started")
    try:
        while not stop_event.is_set():
            make_round(last_ids)
            for _ in range(parser_pause):
                if stop_event.is_set():
                    break
                sleep(1)
    except Exception as e:
        logger.exception("nieruchomosci parser error: %s", e)
    finally:
        logger.info("nieruchomosci parser stopped cleanly")

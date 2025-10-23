# parser/morizon_parser.py
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
from db.mappers import map_morizon_to_listing  # добавим ниже
# при желании можно переиспользовать твои конфиги для городов/типов
from config import CITY_IDS_MORIZON, PROP_TYPES_MORIZON, parser_pause

logger = logging.getLogger("morizon")

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "sec-ch-ua": "\"Google Chrome\";v=\"141\", \"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"141\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1"
    }
# =======================
# Листинг (страница результатов)
# =======================

def build_morizon_search_url(
    deal_type: str,      # "sale" | "rent"
    property_type: str,  # "apartment" | "house" | "room"
    city_slug: str     # "wroclaw" | "warszawa" и т.д.

) -> str:
    """
    Формируем простой URL поиска. На Morizon типы идут во множественном числе.
    deal_type: sale -> '', rent -> 'do-wynajecia/'
    property_type: apartment -> 'mieszkania', house -> 'domy', room -> 'pokoje'
    """
    deal_map = {"sale": "", "rent": "do-wynajecia/"}
    prop_map = {"apartment": "mieszkania", "house": "domy", "room": "pokoje"}

    d = deal_map.get(deal_type, "")
    p = prop_map.get(property_type, "mieszkania")
    return f"https://www.morizon.pl/{d}{p}/najnowsze/{city_slug}/"
    return f"https://www.morizon.pl/{d}{p}/najnowsze/{city_slug}/?ps%5Bowner%5D%5B0%5D=3" # только частные



def extract_listing_urls_from_search_html(html: str) -> List[str]:
    """
    Извлекаем ссылки на карточки с поисковой страницы.
    Селекторы сделаны широкими, с несколькими fallback.
    """
    soup = BeautifulSoup(html, "lxml")
    urls: List[str] = []

    # 1) частый вариант: заголовок карточки содержит ссылку
    candidates = soup.find_all("a", {"data-cy":"propertyUrl"})
    seen = set()
    for a in candidates:
        href = a.get("href")
        if not href: 
            continue
        # абсолютные/относительные:
        if href.startswith("/"):
            href = "https://www.morizon.pl" + href
        # фильтруем заведомо лишние
        if "/oferta/" in href and href not in seen:
            seen.add(href)
            urls.append(href)
    return urls

def get_search_page_urls(
    *,
    deal_type: str, property_type: str, city_slug: str) -> List[str]:
    url = build_morizon_search_url(
        deal_type=deal_type, property_type=property_type, city_slug=city_slug)
    r = http_get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    return extract_listing_urls_from_search_html(r.text)


# =======================
# Карточка
# =======================

def _num_from_text(s: str | None) -> float | None:
    if not s:
        return None
    m = re.search(r"(\d[\d\s .,]*)", s)
    if not m:
        return None
    val = m.group(1).replace(" "," ").replace(" ", "").replace(",", ".")
    try:
        return float(val)
    except Exception:
        return None

def _extract_details_table(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Извлекает характеристики (Rynek, Rok budowy, Powierzchnia, Liczba pokoi и т.д.)
    из таблиц, списков и dl-блоков на карточке Morizon.
    Возвращает словарь {label_lower: value_text}.
    """

    res: Dict[str, str] = {}
    for box in soup.select(".iT04N1"):
        label_div = box.select_one(".YSTCwm._3rio9t, .YSTCwm:not(.M3ijI0)")
        value_div = box.select_one(".YSTCwm.M3ijI0, [data-cy='itemValue']")
        label = label_div.get_text(" ", strip=True) if label_div else None
        value = value_div.get_text(" ", strip=True) if value_div else None
        if label and value:
            res[label.lower()] = value
    
    return res

def _split_srcset_best(srcset: str) -> str | None:
    """
    Возвращает URL с максимальным дескриптором из srcset.
    Пример: "... 300w, ... 450w, ... 600w, ... 900w" -> ссылка на 900w.
    """
    cand = []
    for part in srcset.split(","):
        p = part.strip()
        if not p:
            continue
        m = re.match(r"(\S+)\s+(\d+)w|\s*(\S+)\s+(\d+(?:\.\d+)?)x", p)
        # поддержим оба формата: 900w или 2x
        if m:
            if m.group(1) and m.group(2):
                url, w = m.group(1), int(m.group(2))
                cand.append((url, ("w", w)))
            elif m.group(3) and m.group(4):
                url, x = m.group(3), float(m.group(4))
                cand.append((url, ("x", x)))
    if not cand:
        return None
    # сортируем: сначала по 'w', затем по 'x'
    def key(item):
        kind, val = item[1]
        return (0, val) if kind == "w" else (1, val)
    cand.sort(key=key, reverse=True)
    return cand[0][0]

def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for u in items:
        if not u:
            continue
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out

def _images_from_dom_photo(soup: BeautifulSoup) -> List[str]:
    urls: List[str] = []

    # Основная галерея: кнопки с миниатюрами внутри #gallery__photos
    for btn in soup.select("#gallery__photos button"):
        img = btn.find("img")
        if not img:
            continue
        # если есть srcset — берём самый крупный
        ss = img.get("srcset")
        if ss:
            best = _split_srcset_best(ss)
            if best:
                urls.append(best)
                continue
        # иначе — хотя бы src/data-src
        u = img.get("src") or img.get("data-src")
        if u:
            urls.append(u)

    # На всякий: любые <source srcset> внутри галереи
    for src in soup.select("#gallery__photos source[srcset]"):
        best = _split_srcset_best(src.get("srcset", ""))
        if best:
            urls.append(best)

    return urls

def _images_from_jsonld(soup: BeautifulSoup) -> List[str]:
    out: List[str] = []
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(s.string or "")
        except Exception:
            continue
        objs = data if isinstance(data, list) else [data]
        for obj in objs:
            if not isinstance(obj, dict):
                continue
            imgs = obj.get("image")
            if isinstance(imgs, list):
                out.extend([u for u in imgs if isinstance(u, str)])
            elif isinstance(imgs, str):
                out.append(imgs)
    return out

def get_imgs_for_card(url: str) -> list[str]:
    """
    добавляем /photo в конец url и парсим все фото со страницы
    """
    photo_url = (url or "").rstrip("/") + "/photo"
    r = http_get(photo_url, headers=HEADERS, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")

    # 1) Из DOM галереи берём максимально большие версии по srcset
    dom_imgs = _images_from_dom_photo(soup)

    # 2) JSON-LD (иногда даёт хотя бы обложку)
    ld_imgs = _images_from_jsonld(soup)

    # 3) OG-изображение (fallback)
    og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
    og_img = [og["content"]] if og and og.get("content") else []

    # Совмещаем с приоритетом DOM (обычно там полный набор), затем JSON-LD, затем og:image
    all_imgs = _dedupe_keep_order(dom_imgs + ld_imgs + og_img)

    return all_imgs

def parse_morizon_card(html: str, city_name: str, url: str) -> Dict:
    """
    Парсит карточку Morizon и возвращает словарь для маппера:
    {
      "title", "description", "price", "rooms", "area_m2",
      "district", "street", "images", "url", "external_url",
      "source_ad_id", "location", "market"
    }

    Зависит от вспомогательных функций в модуле:
      _num_from_text(s: str|None) -> float|None
      _extract_details_table(soup: BeautifulSoup) -> Dict[str, str]
    """
    soup = BeautifulSoup(html, "lxml")
    details = _extract_details_table(soup)
    # ---------- Title ----------
    title: Optional[str] = None
    # самый надёжный селектор на новом Morizon
    node = soup.select_one('h1[data-cy="pageDetailsPropertyTitle"]')
    if node:
        title = node.get_text(" ", strip=True)
    if not title:
        for sel in ("h1", "header h1", ".property__header h1"):
            node = soup.select_one(sel)
            if node:
                title = node.get_text(" ", strip=True)
                break
    if not title:
        ogt = soup.find("meta", attrs={"name": "og:title"}) or soup.find("meta", property="og:title")
        if ogt and ogt.get("content"):
            title = ogt["content"]

    # ---------- Price ----------
    price: Optional[float] = None
    pnode = soup.select_one('span[data-cy="priceRowPrice"]')
    if pnode:
        price = _num_from_text(pnode.get_text(" ", strip=True))
    if price is None:
        # альтернативные блоки
        for sel in ("[class*='price']", "[id*='price']", ".priceBox", ".property__price"):
            node = soup.select_one(sel)
            if node:
                price = _num_from_text(node.get_text(" ", strip=True))
                if price is not None:
                    break
    if price is None:
        ogd = soup.find("meta", property="og:description")
        if ogd and ogd.get("content"):
            price = _num_from_text(ogd["content"])
    if price is None:
        # общий поиск по тексту
        txt = soup.get_text(" ", strip=True)
        m = re.search(r"([\d\s.,\u202f\u00a0]{4,})\s*zł", txt, flags=re.I)
        if m:
            price = _num_from_text(m.group(1))

    # ---------- Rooms ----------
    rooms: Optional[int] = None
    rnode = soup.select_one('span[data-cy="detailsRowTextNumberOfRooms"]')
    if rnode:
        m = re.search(r"(\d+)", rnode.get_text(" ", strip=True))
        if m:
            rooms = int(m.group(1))

    # ---------- Area ----------
    area_m2: Optional[float] = None
    anode = soup.select_one('span[data-cy="detailsRowTextArea"]')
    if anode:
        area_m2 = _num_from_text(anode.get_text(" ", strip=True))

    # ---------- Description ----------
    description: Optional[str] = None
    # типовые контейнеры описания
    for sel in (
        '.ASk2iX',                             # встречается на новом Morizon
        "[class*='description']",
        "[id*='description']",
        ".offer-description",
        "article"
    ):
        node = soup.select_one(sel)
        if node:
            description = node.get_text("\n", strip=True)
            if description:
                break
    if not description:
        block = soup.find(string=re.compile(r"\bOpis\b", re.I))
        if block and block.parent:
            description = block.parent.get_text("\n", strip=True)


    # ---------- Address: city/district/street ----------
    # ---------- Address: city/district/street ----------
    address: Optional[str] = None

    # Новый адресный блок: цепочка <span> внутри .location-row__second_column h2
    loc_h2 = soup.select_one(".location-row__second_column h2")
    if loc_h2:
        address = loc_h2.text
        


    # ---------- Market (Rynek: primary/secondary) ----------
    market: Optional[str] = None
    for k in ("rynek", "typ rynku"):
        if k in details and details[k]:
            v = details[k].strip().lower()
            if "pierwotn" in v:            # pierwotny
                market = "primary"
            elif "wtórn" in v or "wtorn" in v or "wtor" in v:  # wtórny
                market = "secondary"
            else:
                market = v
            break
    if not market:
        # fallback по описанию
        desc_lower = (description or "").lower()
        if "rynek pierwotny" in desc_lower or "z rynku pierwotnego" in desc_lower:
            market = "primary"
        elif "rynek wtórny" in desc_lower or "z rynku wtórnego" in desc_lower or "rynek wtor" in desc_lower:
            market = "secondary"

    # ---------- URL / external / ID ----------


    external_url = None  # у Morizon внешней ссылки на карточке обычно нет

    source_ad_id: Optional[str] = None
    images = None
    m = re.search(r"(\d{6,})", url)
    if m:
        source_ad_id = m.group(1)
    else:
        source_ad_id = url.rstrip("/").rsplit("/", 1)[-1]
    images: List[str] = get_imgs_for_card(url)

    return {
        "title": title,
        "description": description,
        "price": price,
        "rooms": rooms,
        "area_m2": area_m2,
        "city": city_name,
        "district": None,
        "address": address,
        "images": images,
        "url": url,
        "external_url": external_url,
        "source_ad_id": source_ad_id,
        "market": market,
        "details": details,
    }


def fetch_and_parse_card(url: str, *, city_name: str) -> Dict:
    r = http_get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    data = parse_morizon_card(r.text, city_name=city_name, url=url)
    return data


# =======================
# Пайплайн
# =======================

def collect_new_urls(last_ids: Dict[Tuple[str, str, str], set]) -> Dict[Tuple[str, str, str], List[str]]:
    """
    Собираем урлы с нескольких страниц поиска.
    """
    res: Dict[Tuple[str, str, str], List[str]] = defaultdict(list)
    for city, city_slug in CITY_IDS_MORIZON:
        for property_type, deal_type in PROP_TYPES_MORIZON:
            key = (city, property_type, deal_type)
            try:
                urls = get_search_page_urls(
                    deal_type=deal_type, property_type=property_type, city_slug=city_slug
                )
                for url in urls:
                    if url not in last_ids[key]:
                        last_ids[key].add(url)
                        res[key].append(url)
                sleep(randint(1,4))  # вежливая пауза
            except Exception:
                logger.exception("failed search page: deal=%s prop=%s city=%s",
                                deal_type, property_type, city_slug,
                                exc_info=False)
    return res


def make_round(last_ids: Dict[Tuple[str, str, str], set]) -> None:
    """
    1) собираем урлы
    2) фильтруем те, что уже в БД (url или external_url)
    3) по новым грузим карточки, парсим, маппим и сохраняем
    """
    try:
        all_urls = collect_new_urls(last_ids)
        tmp = sum([len(val) for val in all_urls.values()])
        logger.info(f"Found morizon adds {tmp}")
        total = 0
        with get_sync_session() as session:
            for key, urls in all_urls.items():
                city, property_type, deal_type = key
                new_urls = filter_new_urls(session, urls)
                for i, url in enumerate(new_urls, 1):
                    try:
                        card = fetch_and_parse_card(url, city_name=city)
                        listing_dict = map_morizon_to_listing(
                            session,
                            card,
                            property_type=property_type,
                            deal_type=deal_type,
                        )
                        if add_listing(session, listing_dict):
                            total += 1 
                            session.commit()
                    except Exception:
                        logger.exception("morizon: failed card %s", url,
                                         exc_info=False)

                session.commit()
        logger.info(f"Added morizon adds {total}")
    except Exception:
        logger.exception("make_round morizon failed", exc_info=False)


def start_morizone(stop_event: Event) -> None:
    '''
    '''
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
        logger.exception("morizon parser error: %s", e)
    finally:
        logger.info("morizon parser stopped cleanly")

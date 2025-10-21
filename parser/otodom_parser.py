# parser/otodom_parser.py
import logging
from collections import defaultdict
from time import sleep
from random import randint
from typing import DefaultDict, Dict, List, Tuple
from threading import Event
from bs4 import BeautifulSoup

from net.http_client import http_get
from config import CITY_IDS_OTODOM, PROP_TYPES_OTODOM, parser_pause
from db.mappers import map_otodom_to_listing
from db.session import get_sync_session
from db.repo import add_listing, filter_new_urls
import json

logger = logging.getLogger("otodom")
headers = {
    "accept": "*/*",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjEzODkzNjgiLCJhcCI6IjEwOTM0NDAzMTAiLCJpZCI6IjU5Y2IwM2NlYjkyM2VkNzgiLCJ0ciI6IjUzMGViYzE2MTljMjllYTNiOWE2Nzk1NzhjOGNlODlmIiwidGkiOjE3NTk0NzM4MDg3NTksInRrIjoiMTcwNTIyMiJ9fQ==",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "traceparent": "00-530ebc1619c29ea3b9a679578c8ce89f-59cb03ceb923ed78-01",
    "x-nextjs-data": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Referer": "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/mazowieckie/warszawa/warszawa/warszawa"
  }

def test_js(js: dict, idx: str = "0") -> None:
    with open(f"test_otodom_{idx}.json", mode="w", encoding="utf-8") as file:
        json.dump(js, file, indent=4, ensure_ascii=False, default=str)


def get_page(deal_type: str, prop_type: str, region: str, city: str, offset: int = 1) -> list[str]:
    """
    возвращает список ссылок для города
    """
    url = f"https://www.otodom.pl/pl/wyniki/{deal_type}/{prop_type}/{region}/{city}/{city}/{city}"
    params = {
    "limit": 72,
    "ownerTypeSingleSelect": "ALL", #ALL PRIVATE
    "by": "LATEST",
    "direction": "DESC",
    "page": offset,
    }
    resp = http_get(
        url,
        params=params,
        headers=headers
    )
    page = resp.text
    soup = BeautifulSoup(page, 'lxml')
    listing = soup.find("div", {"data-cy": "search.listing.organic"})
    if listing is not None:
        items = listing.find_all("a", {"data-cy": "listing-item-link"}, href=True)[:-2]
        return ["https://www.otodom.pl" + item.get("href") for item in items if item]
    
    return []

def get_NEXT_DATA(url: str) -> dict:
    '''
    '''
    resp = http_get(
        url,
        headers=headers
    )
    page = resp.text
    soup = BeautifulSoup(page, 'lxml')
    nd_tag = soup.find("script", id="__NEXT_DATA__", type="application/json")
    if not nd_tag or not nd_tag.string:
        raise RuntimeError("__NEXT_DATA__ not found")

    nd = json.loads(nd_tag.string)
    ad = nd.get("props", {}).get("pageProps", {}).get("ad")
    if not ad:
        raise RuntimeError("ad object not found in pageProps")
    return ad



def get_all_new_posts(
    last_ids: Dict[Tuple[str, str, str], set]
) -> Dict[Tuple[str, str, str], List[dict]]:
    """
    Возвращает новые объявления, сгруппированные ключом (property_type, deal_type).
    last_ids хранит последний id по ключу (city_id, category_id).
    """
    res: Dict[Tuple[str, str, str], List[str]] = defaultdict(list)
    for region, city in CITY_IDS_OTODOM:

        for categories, property_type, deal_type in PROP_TYPES_OTODOM:
            prop_type_str, deal_type_str = categories
            key = (city, property_type, deal_type)
            try:
                urls = get_page(deal_type_str, prop_type_str, region, city)
                for url in urls:
                    if url not in last_ids[key]:
                        last_ids[key].add(url)
                        res[key].append(url)
                sleep(randint(1,2))  # вежливая пауза
            except Exception:
                logger.exception(
                    "get_all_new_posts failed for city=%s category=%s deal=%s",
                    city,
                    property_type,
                    deal_type,
                    exc_info=False)
    return res


def make_round(last_ids: dict) -> None:
    '''
    '''
    try:
        posts = get_all_new_posts(last_ids)
        tmp = sum([len(val) for val in posts.values()])
        logger.info(f"Found otodom adds {tmp}")
        total = 0
        with get_sync_session() as session:
            for key, urls in posts.items():
                new_urls = filter_new_urls(session, urls)
                city, property_type, deal_type = key
                for url in new_urls:
                    try:
                        next_data = get_NEXT_DATA(url)
                        if next_data:
                            otd_l = map_otodom_to_listing(
                                session,
                                next_data,
                                property_type=property_type,
                                deal_type=deal_type)
                            if add_listing(session, otd_l):
                                total += 1
                    except Exception as e:
                        logger.error(f"Error procesing url: {url} {e}")
        
        logger.info("Committed %d otodom listings", total)

    except Exception:
        logger.exception("make_round otodom failed", exc_info=False)


def start_otodom(stop_event: Event):
    # ключ: (city_id, category_id) -> последний увиденный offer.id
    last_ids: DefaultDict[Tuple[str, str, str], set] = defaultdict(set)
    logger.info("Started")
    try:
        while not stop_event.is_set():
            make_round(last_ids)
            logger.debug("otodom last_ids snapshot: %r", dict(last_ids))
            for _ in range(parser_pause):
                if stop_event.is_set():
                    break
                sleep(1)
    except Exception as e:
        logger.exception("otodom parser error: %s", e)
    finally:
        logger.info("otodom parser stopped cleanly")
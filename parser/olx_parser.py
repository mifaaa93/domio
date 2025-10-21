# parser/olx_parser.py
import logging
from collections import defaultdict
from time import sleep
from random import randint
from typing import DefaultDict, Dict, List, Tuple
from threading import Event

from net.http_client import get_json  # <— новый импорт
from config import CITY_IDS_OLX, PROP_TYPES_OLX, parser_pause
from db.mappers import map_olx_to_listing
from db.session import get_sync_session
from db.repo import add_listing
import json

logger = logging.getLogger("olx")


def test_js(js: dict, idx: str = "0") -> None:
    with open(f"test_{idx}.json", mode="w", encoding="utf-8") as file:
        json.dump(js, file, indent=4, ensure_ascii=False, default=str)


headers = {
    "accept": "*/*",
    "accept-language": "uk",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-client": "DESKTOP",
    "x-platform-type": "mobile-html5",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}


def check_post_OLX(post_id: int) -> dict:
    url = f"https://www.olx.pl/api/v2/offers/{post_id}/"
    js = get_json(
      url,
      headers=headers,
    )
    return js or {}


def get_page(city_id: int, category_id: int, offset: int = 0) -> dict:
    url = "https://www.olx.pl/api/v1/offers/"
    params = {
        "offset": offset,
        "limit": 50,
        "category_id": category_id,
        "city_id": city_id,
        "currency": "PLN",
        "sort_by": "created_at:desc",
        "filter_refiners": "spell_checker",
        #"private_business": "private", # только частные
    }
    return get_json(
        url,
        params=params,
        headers=headers
    )



def get_all_new_posts(
    last_ids: DefaultDict[Tuple[int, int], int]
) -> Dict[Tuple[str, str], List[dict]]:
    """
    Возвращает новые объявления, сгруппированные ключом (property_type, deal_type).
    last_ids хранит последний id по ключу (city_id, category_id).
    """
    res: Dict[Tuple[str, str], List[dict]] = defaultdict(list)
    for city_id in CITY_IDS_OLX:
        for category_id, property_type, deal_type in PROP_TYPES_OLX:
            key = (city_id, category_id)
            old_cur_id = last_ids[key]
            try:
                payload = get_page(city_id, category_id)
                data = payload.get("data") or []
                if not data:
                    continue
                for offer in data:
                    offer: dict
                    cur_id = offer.get("id") or 0
                    if cur_id > old_cur_id:
                        res[(property_type, deal_type)].append(offer)
                        last_ids[key] = max(cur_id, last_ids[key])
                sleep(randint(1,4))  # вежливая пауза
            except Exception:
                logger.exception(
                    "get_all_new_posts failed for city=%s category=%s", city_id, category_id,
                    exc_info=False)
    return res


def make_round(last_ids: DefaultDict[Tuple[int, int], int]) -> None:
    try:
        posts = get_all_new_posts(last_ids)
        if not posts:
            logger.info("No new posts this round")
            return
        else:
            tmp = sum([len(val) for val in posts.values()])
            logger.info(f"Found olx adds {tmp}")
        with get_sync_session() as session:
            total = 0
            for (property_type, deal_type), offers in posts.items():
                for item in offers:
                    try:
                        listing = map_olx_to_listing(
                            session, item,
                            property_type=property_type,
                            deal_type=deal_type,
                        )
                        if add_listing(session, listing):
                            total += 1
                    except Exception:
                        logger.exception(
                            "Failed to upsert listing (prop=%s, deal=%s, src_id=%s)",
                            property_type, deal_type, item.get("id"),
                            exc_info=False
                        )
            logger.info("Committed %d olx listings", total)
    except Exception as e:
        logger.error(f"make_round olx failed {e}")

def start_olx(stop_event: Event):
    # ключ: (city_id, category_id) -> последний увиденный offer.id
    last_ids: DefaultDict[Tuple[int, int], int] = defaultdict(int)
    logger.info("Started OLX parser")

    try:
        while not stop_event.is_set():
            make_round(last_ids)
            for _ in range(parser_pause):
                if stop_event.is_set():
                    break
                sleep(1)
    except Exception as e:
        logger.exception("OLX parser error: %s", e)
    finally:
        logger.info("OLX parser stopped cleanly")

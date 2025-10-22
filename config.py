import os
from dotenv import load_dotenv

load_dotenv()

LOG_DIR = "logs"
SYNC_URL = os.getenv("DATABASE_URL")
ASYNC_URL = os.getenv("DATABASE_ASYNC_URL")

BOT_TOKEN = os.getenv("DOMIO_BOT_TOKEN")
ASSET_DIR = os.path.join("bot", "assets", "img")




parser_pause = 180 # как часто проверять новые 
CHECK_INTERVAL_HOURS = 2 
HTTP_TIMEOUT: int = 15           # сек
HTTP_MAX_RETRIES: int = 3
HTTP_RETRY_STATUSES = {429, 500, 502, 503, 504}
HTTP_SKEEP_STATUSES = (404, 410, )
HTTP_BACKOFF_BASE: float = 1.0   # сек (экспоненциальный с джиттером)

PROXIES_POOL: list[str] = [
    "193.28.191.99",
    "154.36.74.49",
    ]
PROXIES_HOST = "brd.superproxy.io"
PROXIES_PORT = "33335"
PROXIES_USERNAME = os.getenv("PROXIES_USERNAME")
PROXIES_PASS = os.getenv("PROXIES_PASS")

# максимальное число одновременных запросов
MAX_CONCURRENT_CHECKS = len(PROXIES_POOL)

# города и типы для олх
CITY_IDS_OLX = (
    17871, # Варшава
    8959, # Краків
    10609, # Лодзь
    19701, # Вроцлав
    13983, # Познань
    5659, # Гданськ
    16705, # Щецин
    7691, # Катовіце
    )
PROP_TYPES_OLX = (
    (15, "apartment", "rent",), # квартиры аренда apartment | house | room rent | sale
    (14, "apartment", "sale",), # квартиры продажа
    (20, "house", "rent",), # дома аренда
    (18, "house", "sale",), # дома продажа
    (11, "room", "rent",), # комнаты аренда
)
CITIES_STR = (
    "Warszawa",
    "Kraków",
    "Łódź",
    "Wrocław",
    "Poznań",
    "Gdańsk",
    "Szczecin",
    "Katowice",
    )

CITY_IDS_NIERUCH = (
    "Warszawa",
    "Kraków",
    "Łódź",
    "Wrocław",
    "Poznań",
    "Gdańsk",
    "Szczecin",
    "Katowice",
    )
# города и типы для otodom
CITY_IDS_OTODOM = (
    ("mazowieckie", "warszawa", ), # Варшава
    ("malopolskie", "krakow", ), # Краків
    ("lodzkie", "lodz", ), # Лодзь
    ("dolnoslaskie", "wroclaw", ), # Вроцлав
    ("wielkopolskie", "poznan", ), # Познань
    ("pomorskie", "gdansk", ), # Гданськ
    ("zachodniopomorskie", "szczecin", ), # Щецин
    ("slaskie", "katowice", ), # Катовіце
    )

PROP_TYPES_OTODOM = (
    (("mieszkanie", "wynajem", ), "apartment", "rent",), # квартиры аренда apartment | house | room rent | sale
    (("mieszkanie", "sprzedaz", ), "apartment", "sale",), # квартиры продажа
    (("dom", "wynajem", ), "house", "rent",), # дома аренда
    (("dom", "sprzedaz", ), "house", "sale",), # дома продажа
    (("pokoj", "wynajem", ), "room", "rent",), # комнаты аренда
    (("kawalerka", "wynajem", ), "apartment", "rent",), # студия аренда
    (("kawalerka", "sprzedaz", ), "apartment", "sale",), # студия продажа
)

CITY_IDS_MORIZON = (
    ("Warszawa", "warszawa", ), # Варшава
    ("Kraków", "krakow", ), # Краків
    ("Łódź", "lodz", ), # Лодзь
    ("Wrocław", "wroclaw", ), # Вроцлав
    ("Poznań", "poznan", ), # Познань
    ("Gdańsk", "gdansk", ), # Гданськ
    ("Szczecin", "szczecin", ), # Щецин
    ("Katowice", "katowice", ), # Катовіце
    )

PROP_TYPES_MORIZON = (
    ("apartment", "rent",), # квартиры аренда apartment | house | room rent | sale
    ("apartment", "sale",), # квартиры продажа
    ("house", "rent",), # дома аренда
    ("house", "sale",), # дома продажа
    ("room", "rent",), # комнаты аренда\
)

CITY_IDS_NIERUCH = (
    "Warszawa",
    "Kraków",
    "Łódź",
    "Wrocław",
    "Poznań",
    "Gdańsk",
    "Szczecin",
    "Katowice",
    )

PROP_TYPES_NIERUCH = (
    ("apartment", "rent",), # квартиры аренда apartment | house | room rent | sale
    ("apartment", "sale",), # квартиры продажа
    ("house", "rent",), # дома аренда
    ("house", "sale",), # дома продажа
    ("room", "rent",), # комнаты аренда\
)



PETS_PHRASE = (
    "bez zwierząt", "bez zwierzat", "nie akceptuje zwierząt",
    "nie akceptujemy zwierząt", "nie akceptuje zwierzat",
    "nie akceptujemy zwierzat", "bez psa", "bez kota",
    )
CHILD_PHRASE = (
    "bez dzieci", "nie dla dzieci", "tylko dorośli",
    "tylko dorosli", "brak dzieci", "no kids", "dla singla", "dla pary",
    )
PETS_CHILD_PHRASE = (
    "bez dzieci i zwierząt", "bez dzieci i zwierzat",
    "tylko dorosli bez zwierzat", "tylko dorośli bez zwierząt",
)

NO_COMISSION_PHRASE = (
        "bez prowizji",
        "0% prowizji",
        "brak prowizji",
        "zero prowizji",
        "bezpośrednio",  # часто значит "от собственника"
        "bez posrednika",
        "bez pośrednika",
        "sprzedaż bezpośrednia",
)
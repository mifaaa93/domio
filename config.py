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

CITIES_STR_SALE = (
    "Kraków",
    "Katowice",
    )

CITY_DISTRICTS = {
    "Warszawa": (
        "Śródmieście",
        "Mokotów",
        "Wola",
        "Praga-Północ",
        "Praga-Południe",
        "Żoliborz",
        "Ochota",
        "Ursynów",
        "Bielany",
        "Włochy",
        "Wilanów",
        "Bemowo",
        "Targówek",
        "Ursus",
        "Wawer",
        "Białołęka",
        "Rembertów",
        "Wesoła",
        "Włochy",
    ),
    "Kraków": (
        "Stare Miasto",
        "Grzegórzki",
        "Prądnik Czerwony",
        "Prądnik Biały",
        "Krowodrza",
        "Bronowice",
        "Zwierzyniec",
        "Dębniki",
        "Łagiewniki-Borek Fałęcki",
        "Podgórze Duchackie",
        "Bieżanów-Prokocim",
        "Podgórze",
        "Czyżyny",
        "Mistrzejowice",
        "Nowa Huta",
        "Bieńczyce",
        "Wzgórza Krzesławickie",
        "Swoszowice",
    ),
    "Łódź": (
        "Bałuty",
        "Polesie",
        "Śródmieście",
        "Widzew",
        "Górna",
    ),
    "Wrocław": (
        "Stare Miasto",
        "Śródmieście",
        "Krzyki",
        "Fabryczna",
        "Psie Pole",
    ),
    "Poznań": (
        "Stare Miasto",
        "Nowe Miasto",
        "Jeżyce",
        "Grunwald",
        "Wilda",
    ),
    "Gdańsk": (
        "Śródmieście",
        "Wrzeszcz Górny",
        "Wrzeszcz Dolny",
        "Przymorze Wielkie",
        "Oliwa",
        "Zaspa-Rozstaje",
        "Chełm",
        "Orunia-Św. Wojciech-Lipce",
        "Ujeścisko-Łostowice",
        "Osowa",
        "Jasień",
        "Letnica",
        "Matarnia",
        "Piecki-Migowo",
    ),
    "Szczecin": (
        "Śródmieście",
        "Pogodno",
        "Niebuszewo",
        "Pomorzany",
        "Dąbie",
        "Zdroje",
        "Bukowe-Klęskowo",
        "Bezrzecze",
        "Warszewo",
        "Gumieńce",
    ),
    "Katowice": (
        "Śródmieście",
        "Koszutka",
        "Bogucice",
        "Dąb",
        "Ligota-Panewniki",
        "Piotrowice-Ochojec",
        "Zawodzie",
        "Janów-Nikiszowiec",
        "Wełnowiec-Józefowiec",
        "Załęże",
        "Szopienice-Burowiec",
        "Brynow",
        "Murcki",
        "Podlesie",
    ),
}

# чуть больше список
CITY_DISTRICTS = {
    "Warszawa": [
        "Mokotów", "Ursynów", "Włochy", "Rembertów", "Praga-Południe", "Wola", "Targówek", "Śródmieście",
        "Ursus", "Praga-Północ", "Wilanów", "Białołęka", "Bemowo", "Żoliborz", "Bielany", "Ochota",
        "Gocław", "Saska Kępa", "Kabaty", "Stare Bielany", "Czyste", "Wawer", "Marysin Wawerski",
        "Anin", "Zerzeń", "Radość", "Międzylesie", "Las", "Zacisze", "Służew", "Służewiec", "Natolin",
        "Stare Włochy", "Stegny", "Dolny Mokotów", "Żoliborz Oficerski", "Koło", "Nowe Miasto",
        "Śródmieście Północne", "Śródmieście Południowe", "Wawrzyszew", "Muranów", "Grochów",
        "Stara Praga", "Tarchomin", "Nowa Praga", "Wilanów Zawady", "Powsin", "Zawady",
    ],
    "Kraków": [
        "Podgórze Duchackie", "Grzegórzki", "Czyżyny", "Prądnik Czerwony", "Dębniki", "Prądnik Biały",
        "Bronowice", "Bieżanów-Prokocim", "Łagiewniki-Borek Fałęcki", "Mistrzejowice", "Krowodrza",
        "Podgórze", "Stare Miasto", "Zwierzyniec", "Wzgórza Krzesławickie", "Nowa Huta", "Bieńczyce",
        "Swoszowice", "Ruczaj", "Wola Justowska", "Salwator", "Tyniec", "Opatkowice", "Borek Fałęcki",
        "Rajsko", "Kurdwanów", "Piaski Wielkie", "Kliny", "Sidzina", "Krowodrza Górka",
        "Podgórze Zabłocie", "Kazimierz", "Rakowice", "Olsza", "Podgórze-Dębniki",
    ],
    "Łódź": [
        "Bałuty", "Polesie", "Śródmieście", "Widzew", "Górna", "Radogoszcz", "Teofilów", "Chojny",
        "Retkinia", "Stare Polesie", "Nowe Rokicie", "Doły", "Karolew", "Jagodnica-Złotno", "Ruda Pabianicka",
        "Koziny", "Żubardź", "Wiskitno", "Stoki", "Łagiewniki", "Radiostacja", "Księży Młyn", "Manhattan",
    ],
    "Wrocław": [
        "Śródmieście", "Krzyki", "Stare Miasto", "Fabryczna", "Psie Pole", "Brochów", "Jagodno",
        "Gaj", "Grabiszyn", "Ołbin", "Sępolno", "Biskupin", "Leśnica", "Oporów", "Partynice", "Ołtaszyn",
        "Klecina", "Popowice", "Pilczyce", "Muchobór Wielki", "Muchobór Mały", "Żerniki", "Psie Pole-Zawidawie",
        "Księże Wielkie", "Księże Małe", "Tarnogaj", "Nadodrze", "Plac Grunwaldzki", "Huby", "Grabiszynek",
        "Złotniki", "Przedmieście Oławskie",
    ],
    "Poznań": [
        "Stare Miasto", "Nowe Miasto", "Jeżyce", "Grunwald", "Wilda", "Winogrady", "Naramowice", "Piątkowo",
        "Rataje", "Łazarz", "Sołacz", "Podolany", "Chartowo", "Dębiec", "Kobylepole", "Szczepankowo",
        "Fabianowo-Kotowo", "Krzyżowniki-Smochowice", "Umultowo", "Morasko", "Żegrze", "Śródka", "Chwaliszewo",
        "Antoninek", "Starołęka", "Wilczak", "Marcelin",
    ],
    "Gdańsk": [
        "Śródmieście", "Wrzeszcz Górny", "Wrzeszcz Dolny", "Przymorze Wielkie", "Przymorze Małe",
        "Chełm", "Orunia-Św. Wojciech-Lipce", "Ujeścisko-Łostowice", "Oliwa", "Piecki-Migowo", "Letnica",
        "Zaspa-Rozstaje", "Jasień", "Osowa", "Matarnia", "Złota Karczma", "Stogi", "Brzeźno", "Strzyża",
        "Żabianka-Wejhera-Jelitkowo-Tysiąclecia", "Suchanino", "Nowy Port", "Przymorze", "Orunia Górna-Gdańsk Południe",
    ],
    "Szczecin": [
        "Śródmieście", "Pogodno", "Niebuszewo", "Pomorzany", "Dąbie", "Zdroje", "Bukowe-Klęskowo", "Bezrzecze",
        "Warszewo", "Gumieńce", "Majowe", "Podjuchy", "Os. Słoneczne", "Żelechowa", "Os. Przyjaźni", "Drzetowo",
        "Turzyn", "Stołczyn", "Skolwin", "Os. Arkońskie", "Międzyodrze-Wyspa Pucka",
    ],
    "Katowice": [
        "Śródmieście", "Koszutka", "Bogucice", "Dąb", "Ligota-Panewniki", "Piotrowice-Ochojec", "Zawodzie",
        "Janów-Nikiszowiec", "Wełnowiec-Józefowiec", "Załęże", "Szopienice-Burowiec", "Brynow",
        "Murcki", "Podlesie", "Kostuchna", "Osiedle Tysiąclecia", "Osiedle Witosa", "Giszowiec",
        "Osiedle Paderewskiego-Muchowiec", "Dąbrówka Mała",
    ],
}


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
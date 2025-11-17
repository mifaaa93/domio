import os
from dotenv import load_dotenv

load_dotenv()
LANGUAGES = ("uk", "en", "pl",)

LOG_DIR = "logs"
SYNC_URL = os.getenv("DATABASE_URL")
ASYNC_URL = os.getenv("DATABASE_ASYNC_URL")

BOT_TOKEN = os.getenv("DOMIO_BOT_TOKEN")
ASSET_DIR = os.path.join("bot", "assets", "img")
ADMIN_IDS = (480055341, 630186846, )

SUBSCRIBES_CHANNEL=int(os.getenv("SUBSCRIBES_CHANNEL"))
HIPOTEKA_LEADS_CHANNEL=int(os.getenv("HIPOTEKA_LEADS_CHANNEL"))
REFERAL_CHANNEL=int(os.getenv("REFERAL_CHANNEL"))

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
PROXIES_HOST = os.getenv("PROXIES_HOST")
PROXIES_PORT = os.getenv("PROXIES_PORT")
PROXIES_USERNAME = os.getenv("PROXIES_USERNAME")
PROXIES_PASS = os.getenv("PROXIES_PASS")

DOMAIN = os.getenv("DOMAIN")
MINIAPP_URL = f"{DOMAIN}/miniapp/"
UPAY_CALL_URL = f"{DOMAIN}/payments/upay"
CREATE_INVOICE_URL = f"{DOMAIN}/miniapp/create_invoice/"
BOT_URL = os.getenv("BOT_URL")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME")
REVIEWS_URL = os.getenv("REVIEWS_URL")
DOMIO_INSTAGRAM = os.getenv("DOMIO_INSTAGRAM")


SERVICES_CHANNELS = {
    "Warszawa": {
        "moving_transport": -100, # Транспорт при переїзді
        "notary": "warszawa_notary_contact", # Нотаріус
        "sworn_translator": "warsaw_sworn_translator_contact", # Присяжний перекладач
        "technical_acceptance": "technical_acceptance_contact", # Технічний прийом квартири
    },
    "Kraków": {
        "repair_turnkey": -1003296401138, # 🏠 Ремонт “під ключ”
        "plumber": -1003463612796, # 🚰 Сантехнік / гідравлік
        "custom_furniture": -1002919629303, # Майстер меблів на замовлення
        "electrician": -1003358470672, # Електрик
        "small_repairs": -1003475531771, # Дрібний ремонт
        "notary": "krakow_notary_contact", # Нотаріус
        "sworn_translator": "krakow_sworn_translator_contact", # Присяжний перекладач
        "moving_transport": -1003336596169, # Транспорт при переїзді
        "technical_acceptance": "technical_acceptance_contact", # Технічний прийом квартири
    },
    "Łódź": {
        "moving_transport": -100, # Транспорт при переїзді
        "notary": "lodz_notary_contact", # Нотаріус
        "sworn_translator": "lodz_sworn_translator_contact", # Присяжний перекладач
        "technical_acceptance": "technical_acceptance_contact", # Технічний прийом квартири
    },
    "Wrocław": {
        "moving_transport": -100, # Транспорт при переїзді
        "notary": "wroclaw_notary_contact", # Нотаріус
        "sworn_translator": "wroclaw_sworn_translator_contact", # Присяжний перекладач
        "technical_acceptance": "technical_acceptance_contact", # Технічний прийом квартири
    },
    "Poznań": {
        "moving_transport": -100, # Транспорт при переїзді
        "notary": "poznan_notary_contact", # Нотаріус
        "sworn_translator": "poznan_sworn_translator_contact", # Присяжний перекладач
        "technical_acceptance": "technical_acceptance_contact", # Технічний прийом квартири
    },
    "Gdańsk": {
        "moving_transport": -100, # Транспорт при переїзді
        "notary": "gdansk_notary_contact", # Нотаріус
        "sworn_translator": "gdansk_sworn_translator_contact", # Присяжний перекладач
        "technical_acceptance": "technical_acceptance_contact", # Технічний прийом квартири
    },
    "Szczecin": {
        "moving_transport": -100, # Транспорт при переїзді
        "notary": "szczecin_notary_contact", # Нотаріус
        "sworn_translator": "szczecin_sworn_translator_contact", # Присяжний перекладач
        "technical_acceptance": "technical_acceptance_contact", # Технічний прийом квартири
    },
    "Katowice": {
        "moving_transport": -100, # Транспорт при переїзді
        "notary": "katowice_notary_contact", # Нотаріус
        "sworn_translator": "katowice_sworn_translator_contact", # Присяжний перекладач
        "technical_acceptance": "technical_acceptance_contact", # Технічний прийом квартири
    },
}

REFFERAL_PERCENT = 0.3 # сколько получают реффералы


# словарь где хранятся цены подписок
TARIFFS_DICT = {
    "SUBSCRIPTION": {
        "test":  {'price': 4.99,  'days': 3,  'is_test': True,  'next_sub': "2week", "currency": "PLN", "description": "Domio service subscription for 3 days."},
        "2week": {'price': 19.99, 'days': 14, 'is_test': False, 'next_sub': "2week", "currency": "PLN", "description": "Domio service subscription for 14 days."},
        "month": {'price': 34.99, 'days': 30, 'is_test': False, 'next_sub': "month", "currency": "PLN", "description": "Domio service subscription for 1 month."},
    },
    "ONE_TIME": {
        "guides": {'price': 99.0, "currency": "PLN", "description": "Domio guide on buying property in Poland."}
    }

}


REGLAMENT_URLS = {
    "pl": "https://domioestate.pl/regulamin-uslugi/",
    "uk": "https://domioestate.pl/uk/reglament-poslugi/",
    "en": "https://domioestate.pl/en/terms-of-service/"
}
PRIVACI_URLS = {
    "pl": "https://domioestate.pl/polityka-prywatnosci/",
    "uk": "https://domioestate.pl/uk/polityka-konfidenciinosti/",
    "en": "https://domioestate.pl/en/privacy-policy/"
}

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# максимальное число одновременных запросов
MAX_CONCURRENT_CHECKS = len(PROXIES_POOL)


PAYU_POS_ID = os.getenv("PAYU_POS_ID")
PAYU_CLIENT_ID = os.getenv("PAYU_CLIENT_ID")
PAYU_CLIENT_SECRET = os.getenv("PAYU_CLIENT_SECRET")
PAYU_SECOND_KEY = os.getenv("PAYU_SECOND_KEY")
PAYU_SANDBOX = os.getenv("PAYU_SANDBOX", "true").lower() == "true"


METERS_LIST = (0, 20, 30, 40, 50, 60, 100, )

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

AGENT_CHANNELS = {
    "Warszawa": HIPOTEKA_LEADS_CHANNEL,
    "Kraków": None,
    "Łódź": None,
    "Wrocław": None,
    "Poznań": None,
    "Gdańsk": None,
    "Szczecin": None,
    "Katowice": None,
}

CITY_DISTRICTS = {
    "Warszawa": [
        "Centrum", "Bemowo", "Białołęka", "Bielany", "Mokotów", "Ochota",
        "Praga-Południe", "Praga-Północ", "Rembertów", "Śródmieście",
        "Targówek", "Ursus", "Ursynów", "Wawer", "Wesoła",
        "Wilanów", "Włochy", "Wola", "Żoliborz"
    ],
    "Kraków": [
        "Centrum", "Stare Miasto", "Grzegórzki", "Prądnik Czerwony", "Prądnik Biały",
        "Krowodrza", "Bronowice", "Zwierzyniec", "Dębniki",
        "Łagiewniki-Borek Fałęcki", "Swoszowice", "Podgórze Duchackie",
        "Bieżanów-Prokocim", "Podgórze", "Czyżyny", "Mistrzejowice",
        "Bieńczyce", "Wzgórza Krzesławickie", "Nowa Huta"
    ],
    "Łódź": [
        "Centrum", "Bałuty", "Górna", "Polesie", "Śródmieście", "Widzew"
    ],
    "Wrocław": [
        "Centrum", "Fabryczna", "Krzyki", "Psie Pole", "Stare Miasto", "Śródmieście"
    ],
    "Poznań": [
        "Centrum", "Grunwald", "Jeżyce", "Nowe Miasto", "Stare Miasto", "Wilda"
    ],
    "Gdańsk": [
        "Centrum", "Aniołki", "Brętowo", "Brzeźno", "Chełm", "Jasień", "Kokoszki",
        "Krakowiec-Górki Zachodnie", "Letnica", "Matarnia", "Młyniska",
        "Nowy Port", "Oliwa", "Olszynka", "Orunia-Św. Wojciech-Lipce",
        "Orunia Górna-Gdańsk Południe", "Osowa", "Piecki-Migowo",
        "Przeróbka", "Przymorze Małe", "Przymorze Wielkie", "Rudniki",
        "Siedlce", "Stogi", "Strzyża", "Suchanino", "Śródmieście",
        "Ujeścisko-Łostowice", "VII Dwór", "Wrzeszcz Dolny", "Wrzeszcz Górny",
        "Wyspa Sobieszewska", "Zaspa-Młyniec", "Zaspa-Rozstaje",
        "Żabianka-Wejhera-Jelitkowo-Tysiąclecia"
    ],
    "Szczecin": [
        "Centrum", "Północ", "Prawobrzeże", "Śródmieście", "Zachód"
    ],
    "Katowice": [
        "Centrum", "Bogucice", "Brynów-Osiedle Zgrzebnioka", "Dąb", "Dąbrówka Mała",
        "Giszowiec", "Janów-Nikiszowiec", "Kostuchna", "Koszutka",
        "Ligota-Panewniki", "Murcki", "Osiedle Paderewskiego-Muchowiec",
        "Osiedle Tysiąclecia", "Piotrowice-Ochojec", "Podlesie",
        "Szopienice-Burowiec", "Śródmieście", "Wełnowiec-Józefowiec",
        "Załęska Hałda-Brynów", "Załęże", "Zawodzie", "Zarzecze"
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
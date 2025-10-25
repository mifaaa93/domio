from typing import Literal, Dict

Lang = Literal["uk", "en", "pl"]
marker_ok = "✅"
# --- Основные тексты ---
TEXTS: Dict[str, Dict[Lang, str]] = {
    "choose_language": {
        "uk": (
            "Please select language\n"
            "Proszę wybrać język\n"
            "Будь-ласка обери мову\n"),
    },
    "language_set": {
        "uk": "✅ Мову встановлено: Українська!",
        "en": "✅ Language set: English!",
        "pl": "✅ Ustawiono język: Polski!",
    },

    "main_menu": {
        "uk": "🏠 Головне меню",
        "en": "🏠 Main menu",
        "pl": "🏠 Menu główne",
    },
    "search_type": {
        "uk": "Обери тип пошуку",
        "en": "Choose search type",
        "pl": "Wybierz typ wyszukiwania",
    },
    "estate_type": {
        "uk": "Обери тип нерухомості",
        "en": "Choose property type",
        "pl": "Wybierz typ nieruchomości",
    },
    "market_type": {
        "uk": "Обери тип ринку",
        "en": "Choose market type",
        "pl": "Wybierz typ rynku",
    },
    "select_city": {
        "uk": "🌆 Оберіть місто",
        "en": "🌆 Choose city",
        "pl": "🌆 Wybierz miasto",
    },
    "select_district": {
        "uk": "📍 Відміть галочкою район і натисни «Далі»",
        "en": "📍 Select districts and press «Next»",
        "pl": "📍 Zaznacz dzielnice i naciśnij «Dalej»",
    },
    "area_from": {
        "uk": "Від якої площі шукаєш?",
        "en": "What minimum area are you looking for?",
        "pl": "Od jakiego metrażu szukasz?"
    },
    "area_to": {
        "uk": "До якої площі шукаєш?",
        "en": "What maximum area are you looking for?",
        "pl": "Do jakiego metrażu szukasz?"
    },
    "rooms_count": {
        "uk": "Зазнач к-сть кімнат",
        "en": "Specify the number of rooms",
        "pl": "Podaj liczbę pokoi"
    },
    "price_from": {
        "uk": "Обери ВІД якої вартості ти шукаєш нерухомість",
        "en": "Choose the minimum price for the property you’re looking for",
        "pl": "Wybierz minimalną cenę nieruchomości, której szukasz"
    },
    "price_to": {
        "uk": "Обери ДО якої вартості ти шукаєш нерухомість",
        "en": "Choose the maximum price for the property you’re looking for",
        "pl": "Wybierz maksymalną cenę nieruchomości, której szukasz"
    },
    "child": {
        "uk": "Маєш дітей",
        "en": "Do you have children?",
        "pl": "Czy masz dzieci?"
    },
    "pets": {
        "uk": "Маєш тваринку",
        "en": "Do you have a pet?",
        "pl": "Czy masz zwierzątko?"
    },
    "results": {
        "uk": (
            "Результат пошуку\n"
            "Domio підібрав для тебе {total} квартир, що відповідають твоєму запиту.\n\n"
            "Твій запит:\n"
            "{search}"
        ),
        "en": (
            "Search results\n"
            "Domio has found {total} apartments that match your request.\n\n"
            "Your request:\n"
            "{search}"
        ),
        "pl": (
            "Wynik wyszukiwania\n"
            "Domio znalazło dla Ciebie {total} mieszkań pasujących do Twojego zapytania.\n\n"
            "Twoje zapytanie:\n"
            "{search}"
        )
    }
}

BUTTONS: Dict[str, Dict[Lang, str]] = {
    # --- Основное меню ---
    "search": {
        "uk": "🔍 Пошук квартир",
        "en": "🔍 Search apartments",
        "pl": "🔍 Wyszukaj mieszkanie",
    },
    "subscribe": {
        "uk": "⭐ Оформити доступ",
        "en": "⭐ Get access",
        "pl": "⭐ Uzyskaj dostęp",
    },
    "how_to_use": {
        "uk": "📘 Як користуватися",
        "en": "📘 How to use",
        "pl": "📘 Jak korzystać",
    },
    "favorites": {
        "uk": "💾 Збережені",
        "en": "💾 Saved",
        "pl": "💾 Zapisane",
    },
    "guides": {
        "uk": "📘 Гайди",
        "en": "📘 Guides",
        "pl": "📘 Poradniki",
    },
    "contact_agent": {
        "uk": "🤝 Контакт з ріелтором",
        "en": "🤝 Contact agent",
        "pl": "🤝 Kontakt z agentem",
    },
    "mortgage": {
        "uk": "🏦 Іпотека",
        "en": "🏦 Mortgage",
        "pl": "🏦 Kredyt hipoteczny",
    },
    "builders_services": {
        "uk": "🛠 Будівельні послуги",
        "en": "🛠 Construction services",
        "pl": "🛠 Usługi budowlane",
    },
    "earn_with_domio": {
        "uk": "💰 Заробіток з Domio",
        "en": "💰 Earn with Domio",
        "pl": "💰 Zarabiaj z Domio",
    },
    "reviews": {
        "uk": "🗣 Відгуки",
        "en": "🗣 Reviews",
        "pl": "🗣 Opinie",
    },
    "help": {
        "uk": "🛟 Допомога",
        "en": "🛟 Help",
        "pl": "🛟 Pomoc",
    },
    "language": {
        "uk": "🌐 Мова",
        "en": "🌐 Language",
        "pl": "🌐 Język",
    },
    "back": {
        "uk": "⬅️ Назад",
        "en": "⬅️ Back",
        "pl": "⬅️ Wstecz",
    },
    "next": {
        "uk": "➡️ Далі",
        "en": "➡️ Next",
        "pl": "➡️ Dalej",
    },
    "placeholder_main_menu": {
        "uk": "Оберіть дію...",
        "en": "Choose an action...",
        "pl": "Wybierz działanie...",
    },
    "sale_btn": {
        "uk": "💰 Купівля",
        "en": "💰 Buy",
        "pl": "💰 Kupno",
    },
    "rent_btn": {
        "uk": "🏠 Оренда",
        "en": "🏠 Rent",
        "pl": "🏠 Wynajem",
    },
    "apartment_btn": {
        "uk": "🏢 Квартира",
        "en": "🏢 Apartment",
        "pl": "🏢 Mieszkanie",
    },
    "house_btn": {
        "uk": "🏡 Будинок",
        "en": "🏡 House",
        "pl": "🏡 Dom",
    },
    "room_btn": {
        "uk": "🛏 Кімната",
        "en": "🛏 Room",
        "pl": "🛏 Pokój",
    },
    "secondary_btn": {
        "uk": "🏘 Вторинка",
        "en": "🏘 Secondary market",
        "pl": "🏘 Rynek wtórny",
    },
    "primary_btn": {
        "uk": "🏗 Новобудова",
        "en": "🏗 New development",
        "pl": "🏗 Rynek pierwotny",
    },
    "all_district_btn": {
        "uk": "📍 Всі райони",
        "en": "📍 All districts",
        "pl": "📍 Wszystkie dzielnice",
    },
    "any_area_btn": {
        "uk": "Будь-яка площа",
        "en": "Any area",
        "pl": "Dowolny metraż"
    },
    "area_from_btn": {
        "uk": "від {meters} м2",
        "en": "from {meters} m²",
        "pl": "od {meters} m²"
    },
    "area_to_btn": {
        "uk": "до {meters} м2",
        "en": "up to {meters} m²",
        "pl": "do {meters} m²"
    },
    "rooms_count_btn1": {
        "uk": "1 кімната",
        "en": "1 room",
        "pl": "1 pokój"
    },
    "rooms_count_btn2": {
        "uk": "2 кімнати",
        "en": "2 rooms",
        "pl": "2 pokoje"
    },
    "rooms_count_btn3": {
        "uk": "3 кімнати",
        "en": "3 rooms",
        "pl": "3 pokoje"
    },
    "rooms_count_btn4": {
        "uk": "4 кімнати",
        "en": "4 rooms",
        "pl": "4 pokoje"
    },
    "rooms_count_btn5": {
        "uk": "5 та більше кімнат",
        "en": "5+ rooms",
        "pl": "5 i więcej pokoi"
    },
    "any_price_btn": {
        "uk": "Без обмеженнь",
        "en": "No limit",
        "pl": "Bez ograniczeń"
    },
    "yes_btn": {
        "uk": "Так",
        "en": "Yes",
        "pl": "Tak"
    },
    "no_btn": {
        "uk": "Ні",
        "en": "No",
        "pl": "Nie"
    },
    "refresh_btn": {
        "uk": "Оновити пошук",
        "en": "Refresh search",
        "pl": "Odśwież wyszukiwanie"
    },
    "result_btn": {
        "uk": "Результати запиту",
        "en": "Search results",
        "pl": "Wyniki wyszukiwania"
    }
}


ALERTS: Dict[str, Dict[Lang, str]] = {
    "no_room_selected": {
        "uk": "🔢 Оберіть кількість кімнат",
        "en": "🔢 Choose the number of rooms",
        "pl": "🔢 Wybierz liczbę pokoi",
    },
}

def t(lang: Lang | None, key: str) -> str:
    """Возвращает текст по ключу и языку с fallback на uk."""
    return TEXTS.get(key, {}).get(lang or "uk", TEXTS.get(key, {}).get("uk", key))


def btn(lang: Lang | None, key: str) -> str:
    """Возвращает текст кнопки по ключу и языку с fallback на uk."""
    return BUTTONS.get(key, {}).get(lang or "uk", BUTTONS.get(key, {}).get("uk", key))

def alert_t(lang: Lang | None, key: str) -> str:
    """Возвращает текст уведомления по ключу и языку с fallback на uk."""
    return ALERTS.get(key, {}).get(lang or "uk", ALERTS.get(key, {}).get("uk", key))

def btn_tuple(key: str) -> str:
    """Возвращает текст кнопки по ключу и языку с fallback на uk."""
    return tuple(BUTTONS.get(key, {}).values())

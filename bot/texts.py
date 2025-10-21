from typing import Literal, Dict

Lang = Literal["uk", "en", "pl"]

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
    "choose_city": {
        "uk": "🌆 Оберіть місто",
        "en": "🌆 Choose city",
        "pl": "🌆 Wybierz miasto",
    },
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
    "placeholder_main_menu": {
        "uk": "Оберіть дію...",
        "en": "Choose an action...",
        "pl": "Wybierz działanie...",
    }
}


def t(lang: Lang | None, key: str) -> str:
    """Возвращает текст по ключу и языку с fallback на uk."""
    return TEXTS.get(key, {}).get(lang or "uk", TEXTS.get(key, {}).get("uk", key))


def btn(lang: Lang | None, key: str) -> str:
    """Возвращает текст кнопки по ключу и языку с fallback на uk."""
    return BUTTONS.get(key, {}).get(lang or "uk", BUTTONS.get(key, {}).get("uk", key))

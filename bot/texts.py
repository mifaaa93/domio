from typing import Literal, Dict
from config import TARIFFS_DICT

subscribe_prices = TARIFFS_DICT["SUBSCRIPTION"]
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
    },
    "favorites": {
        "uk": "Збережених оголошень: {total}",
        "en": "Saved listings: {total}",
        "pl": "Zapisanych ogłoszeń: {total}",
    },
    "subscribe_main": {
        "uk": f'''<i>💛 Що дає кожна підписка:</i>
🔸 Пробна за {subscribe_prices["test"]["price"]} зл, щоб перевірити, як працює пошук квартир.
🔸 Підписка на два тижні за {subscribe_prices["2week"]["price"]} зл — <b>повний доступ:</b>
🔸 Місячна підписка за {subscribe_prices["month"]["price"]} зл — <b>повний доступ:</b>
• сповіщення, коли з’являються нові квартири 🏠
• можливість зберігати результати пошуку 📋
• безкоштовні гайди з оренди 🧾

<i>💬 Оплачуючи підписку та користуючись пошуком квартир, ти автоматично підтверджуєш, що ознайомився та погоджуєшся з регламентом і політикою приватності Domio</i>''',
        "pl": f"""<i>💛 Co daje każdy abonament:</i>
🔸 Okres próbny za {subscribe_prices["test"]["price"]} zł, aby sprawdzić, jak działa wyszukiwanie mieszkań.
🔸 Abonament na dwa tygodnie za {subscribe_prices["2week"]["price"]} zł — <b>pełny dostęp:</b>
🔸 Abonament miesięczny za {subscribe_prices["month"]["price"]} zł — <b>pełny dostęp:</b>
• powiadomienia o nowych mieszkaniach 🏠
• możliwość zapisywania wyników wyszukiwania 📋
• bezpłatne poradniki dotyczące najmu 🧾

<i>💬 Opłacając abonament i korzystając z wyszukiwarki mieszkań, automatycznie potwierdzasz, że zapoznałeś(-aś) się z regulaminem i polityką prywatności Domio.</i>""",
        "en": f"""<i>💛 What each subscription gives you:</i>
🔸 Trial for {subscribe_prices["test"]["price"]} PLN to test how the apartment search works.
🔸 Two-week subscription for {subscribe_prices["2week"]["price"]} PLN — <b>full access:</b>
🔸 Monthly subscription for {subscribe_prices["month"]["price"]} PLN — <b>full access:</b>
• alerts when new apartments appear 🏠
• ability to save your search results 📋
• free renting guides 🧾

<i>💬 By paying for a subscription and using the apartment search, you automatically confirm that you have read and agree to Domio’s Terms and Privacy Policy.</i>"""

    },
    "successful_subscription": {
        "uk": "✅ У тебе активована підписка на {days} дні(-ів) до {valid_to}",
        "en": "✅ Your subscription is active for {days} day(s) until {valid_to}",
        "pl": "✅ Masz aktywną subskrypcję na {days} dni, ważną do {valid_to}"
    },
    "settings": {
        "uk": "⚙️ Налаштування",
        "en": "⚙️ Settings",
        "pl": "⚙️ Ustawienia",
    },
    "earn_with_domio": {
        "uk": "Твоє реферальне посилання:\n{url}\n\nПоточний баланс: {current} PLN\nНараховано за весь час: {total} PLN",
        "en": "Your referral link:\n{url}\n\nYour current balance: {current} PLN\nTotal earned from referrals: {total} PLN",
        "pl": "Twój link polecający:\n{url}\n\nAktualny stan konta: {current} PLN\nŁącznie zarobiono z poleceń: {total} PLN",
    },
    "recurring_prompt_disable": {
        "uk": "Ти бажаєш вимкнути автопродовження підписки?",
        "en": "Do you want to turn off subscription auto-renewal?",
        "pl": "Chcesz wyłączyć automatyczne odnawianie subskrypcji?",
    },
    "support": {
        "uk": "🆘 <b>Допомога Domio</b>\nЯкщо щось не працює, виникла проблема чи маєш ідею, як зробити Domio ще кращим — напиши нам прямо тут 💬\nМи читаємо всі повідомлення і завжди відповідаємо!\nТвоя думка допомагає нам розвиватися 💛\n{username}",
        "en": "🆘 <b>Domio Support</b>\nIf something isn’t working, you’ve run into a problem, or you have an idea to make Domio even better — send us a message right here 💬\nWe read every message and always reply!\nYour feedback helps us grow 💛\n{username}",
        "pl": "🆘 <b>Pomoc Domio</b>\nJeśli coś nie działa, masz problem albo pomysł, jak ulepszyć Domio — napisz do nas tutaj 💬\nCzytamy wszystkie wiadomości i zawsze odpisujemy!\nTwoja opinia pomaga nam się rozwijać 💛\n{username}"
    },
    "reviews": {
        "uk": "🗣 <b>Відгуки про Domio</b>\nХочеш побачити, що кажуть наші користувачі?\nПереглянь реальні відгуки за посиланням нижче 👇\n👉 <a href=\"{url}\">Відгуки про Domio</a>.",
        "en": "🗣 <b>Reviews about Domio</b>\nWant to see what our users say?\nCheck real reviews at the link below 👇\n👉 <a href=\"{url}\">Reviews about Domio</a>.",
        "pl": "🗣 <b>Opinie o Domio</b>\nChcesz zobaczyć, co mówią nasi użytkownicy?\nZobacz prawdziwe opinie pod linkiem poniżej 👇\n👉 <a href=\"{url}\">Opinie o Domio</a>."
    },
}

BUTTONS: Dict[str, Dict[Lang, str]] = {
    # --- Основное меню ---
    "settings": {
        "uk": "⚙️ Налаштування",
        "en": "⚙️ Settings",
        "pl": "⚙️ Ustawienia",
    },
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
    "recurring": {
        "uk": "Вимкнути автопродовження",
        "en": "Turn off auto-renewal",
        "pl": "Wyłącz automatyczne odnawianie",
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
        "uk": "від {meters} м²",
        "en": "from {meters} m²",
        "pl": "od {meters} m²"
    },
    "area_to_btn": {
        "uk": "до {meters} м²",
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
    "any_rooms_count_btn": {
        "uk": "Будь-яка кількість",
        "en": "Any number",
        "pl": "Dowolna liczba"
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
    },
    "open_listing_btn": {
        "uk": "Переглянути оголошення",
        "en": "View listing",
        "pl": "Zobacz ogłoszenie"
    },
    "like_listing_btn": {
        "uk": "Зберегти",
        "en": "Save",
        "pl": "Zapisz"
    },
    "unlike_listing_btn": {
        "uk": "Видалити",
        "en": "Remove",
        "pl": "Usuń"
    },
    "my_favorites_btn": {
        "uk": "Переглянути збережені",
        "en": "View saved",
        "pl": "Zobacz zapisane",
    },
    "subscribe_main_test_btn": {
        "uk": f"Підписка {subscribe_prices['test']['price']} зл / 3 дні",
        "en": f"Subscription {subscribe_prices['test']['price']} PLN / 3 days",
        "pl": f"Abonament {subscribe_prices['test']['price']} zł / 3 dni",
    },
    "subscribe_main_2week_btn": {
        "uk": f"Підписка {subscribe_prices['2week']['price']} зл / 2 тижні",
        "en": f"Subscription {subscribe_prices['2week']['price']} PLN / 2 weeks",
        "pl": f"Abonament {subscribe_prices['2week']['price']} zł / 2 tyg.",
    },
    "subscribe_main_month_btn": {
        "uk": f"Підписка {subscribe_prices['month']['price']} зл / міс",
        "en": f"Subscription {subscribe_prices['month']['price']} PLN / mo",
        "pl": f"Abonament {subscribe_prices['month']['price']} zł / mies.",
    },
    "reglament_btn_text": {
        "uk": "Регламент",
        "en": "Terms of Service",
        "pl": "Regulamin",
    },
    "privacy_btn_text": {
        "uk": "Політика приватності",
        "en": "Privacy Policy",
        "pl": "Polityka prywatności",
    },
    "pay_btn": {
        "uk": "Оплатити {amount}",
        "en": "Pay {amount}",
        "pl": "Zapłać {amount}"
    },
    "show_all_btn": {
        "uk": "Дивитись всі",
        "en": "View all",
        "pl": "Zobacz wszystkie"
    },
    "map_btn": {
        "uk": "🗺 Карта",
        "en": "🗺 Map",
        "pl": "🗺 Mapa"
    },
}

LISTINGS = {
    "listing_new_text": {
        "uk": '''<b>🏠 Нова квартира знайдена!</b>
Domio щойно знайшов для тебе свіжу пропозицію напряму від власника 👇

📍 <b>Місто:</b> {city}
💰 <b>Ціна:</b> {price} PLN
📏 <b>Площа:</b> {area} м²
🛏 <b>Кімнат:</b> {rooms}
📄 <b>Опис:</b>
{description}''',

        "en": '''<b>🏠 New apartment found!</b>
Domio has just found a fresh offer directly from the owner 👇

📍 <b>City:</b> {city}
💰 <b>Price:</b> {price} PLN
📏 <b>Area:</b> {area} m²
🛏 <b>Rooms:</b> {rooms}
📄 <b>Description:</b>
{description}''',

        "pl": '''<b>🏠 Znaleziono nowe mieszkanie!</b>
Domio właśnie znalazł dla Ciebie świeżą ofertę bezpośrednio od właściciela 👇

📍 <b>Miasto:</b> {city}
💰 <b>Cena:</b> {price} PLN
📏 <b>Powierzchnia:</b> {area} m²
🛏 <b>Pokoje:</b> {rooms}
📄 <b>Opis:</b>
{description}'''
    }
}


ALERTS: Dict[str, Dict[Lang, str]] = {
    "no_room_selected": {
        "uk": "🔢 Оберіть кількість кімнат",
        "en": "🔢 Choose the number of rooms",
        "pl": "🔢 Wybierz liczbę pokoi",
    },
    "no_such_tariff": {
        "uk": "Такого тарифу вже не існує",
        "en": "That plan no longer exists",
        "pl": "Taki plan już nie istnieje",
    },
    "listing_deleted": {
        "uk": "Оголошення вже неактуальне",
        "en": "This listing is no longer available",
        "pl": "To ogłoszenie jest już nieaktualne",
    },
    "recurring_disable_confirmed": {
        "uk": "Автопродовження вимкнуто",
        "en": "Auto-renewal disabled",
        "pl": "Automatyczne odnawianie wyłączone",
        },
}

def t(lang: Lang | None, key: str) -> str:
    """Возвращает текст по ключу и языку с fallback на uk."""
    return TEXTS.get(key, {}).get(lang or "uk", TEXTS.get(key, {}).get("uk", key))

def listing_t(lang: Lang | None, key: str) -> str:
    """Возвращает текст по ключу и языку с fallback на uk."""
    return LISTINGS.get(key, {}).get(lang or "uk", LISTINGS.get(key, {}).get("uk", key))

def btn(lang: Lang | None, key: str) -> str:
    """Возвращает текст кнопки по ключу и языку с fallback на uk."""
    return BUTTONS.get(key, {}).get(lang or "uk", BUTTONS.get(key, {}).get("uk", key))

def alert_t(lang: Lang | None, key: str) -> str:
    """Возвращает текст уведомления по ключу и языку с fallback на uk."""
    return ALERTS.get(key, {}).get(lang or "uk", ALERTS.get(key, {}).get("uk", key))

def btn_tuple(key: str) -> str:
    """Возвращает текст кнопки по ключу и языку с fallback на uk."""
    return tuple(BUTTONS.get(key, {}).values())

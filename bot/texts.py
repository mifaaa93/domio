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
        "uk": "Обери <b>тип пошуку</b>",
        "en": "Choose <b>search type</b>",
        "pl": "Wybierz <b>typ wyszukiwania</b>",
    },
    "estate_type": {
        "uk": "Обери <b>тип нерухомості</b>",
        "en": "Choose <b>property type</b>",
        "pl": "Wybierz <b>typ nieruchomości</b>",
    },
    "market_type": {
        "uk": "Обери <b>тип ринку</b>",
        "en": "Choose <b>market type</b>",
        "pl": "Wybierz <b>typ rynku</b>",
    },
    "select_city": {
        "uk": "🌆 Оберіть <b>місто</b>",
        "en": "🌆 Choose <b>city</b>",
        "pl": "🌆 Wybierz <b>miasto</b>",
    },
    "select_district": {
        "uk": "📍 Відміть галочкою <b>район</b> і натисни <b>«Далі»</b>",
        "en": "📍 Select <b>districts</b> and press <b>«Next»</b>",
        "pl": "📍 Zaznacz <b>dzielnice</b> i naciśnij <b>«Dalej»</b>",
    },
    "area_from": {
        "uk": "Від якої <b>площі</b> шукаєш?",
        "en": "What minimum <b>area</b> are you looking for?",
        "pl": "Od jakiego <b>metrażu</b> szukasz?"
    },
    "area_to": {
        "uk": "<b>До</b> якої <b>площі</b> шукаєш?",
        "en": "<b>What</b> maximum <b>area</b> are you looking for?",
        "pl": "<b>Do</b> jakiego <b>metrażu</b> szukasz?"
    },
    "rooms_count": {
        "uk": "Зазнач <b>к-сть кімнат</b>",
        "en": "Specify <b>the number of room</b>s",
        "pl": "Podaj <b>liczbę pokoi</b>"
    },
    "price_from": {
        "uk": "Впиши <b>від якої</b> вартості шукаєш нерухомість",
        "en": "Enter the <b>minimum</b> price of the property you're looking for",
        "pl": "Wpisz <b>od jakiej</b> ceny szukasz nieruchomości"
    },
    "price_to": {
        "uk": "Впиши <b>до якої</b> вартості шукаєш нерухомість",
        "en": "Enter the <b>maximum</b> price of the property you're looking for",
        "pl": "Wpisz <b>do jakiej</b> ceny szukasz nieruchomości"
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
            "<b>Результат пошуку</b>\n"
            "Domio підібрав для тебе <b>{total} квартир</b>, що відповідають твоєму запиту.\n\n"
            "<b>Твій запит:</b>\n"
            "{search}"
        ),
        "en": (
            "<b>Search results</b>\n"
            "Domio has found <b>{total} apartments</b> that match your request.\n\n"
            "<b>Your request:</b>\n"
            "{search}"
        ),
        "pl": (
            "<b>Wynik wyszukiwania</b>\n"
            "Domio znalazło dla Ciebie <b>{total} mieszkań</b> pasujących do Twojego zapytania.\n\n"
            "<b>Twoje zapytanie:</b>\n"
            "{search}"
        )
    },
    "favorites": {
        "uk": "Збережених оголошень: {total}",
        "en": "Saved listings: {total}",
        "pl": "Zapisanych ogłoszeń: {total}",
    },
    "subscribe_main": {
        "uk": f'''<b>💛 Що дає кожна підписка:</b>
🔸 {subscribe_prices["test"]["price"]} зл/ 3 дні, щоб перевірити як працює пошук квартир.
🔸 <b>{subscribe_prices["2week"]["price"]} зл/ 14 днів</b> — повний доступ,
🔸 {subscribe_prices["month"]["price"]} зл/ місяць — повний доступ.

<b>Повний доступ:</b>
• сповіщення, коли з’являються нові квартири 🏠
• можливість зберігати результати пошуку 📋
• безкоштовний гайд з оренди 🧾

<i>💬 Оплачуючи підписку та користуючись пошуком квартир, ти автоматично підтверджуєш, що ознайомився та погоджуєшся з регламентом і політикою приватності Domio</i>''',
        "en": f'''<b>💛 What each subscription gives:</b>
🔸 {subscribe_prices["test"]["price"]} zł / 3 days — to try how the apartment search works.
🔸 <b>{subscribe_prices["2week"]["price"]} zł / 14 days</b> — full access,
🔸 {subscribe_prices["month"]["price"]} zł / month — full access.

<b>Full access:</b>
• notifications when new apartments appear 🏠
• ability to save search results 📋
• free rental guide 🧾

<i>💬 By paying for a subscription and using the apartment search, you automatically confirm that you have read and agree to Domio’s Terms and Privacy Policy</i>''',
        "pl": f'''<b>💛 Co daje każda subskrypcja:</b>
🔸 {subscribe_prices["test"]["price"]} zł / 3 dni — aby sprawdzić, jak działa wyszukiwanie mieszkań.
🔸 <b>{subscribe_prices["2week"]["price"]} zł / 14 dni</b> — pełny dostęp,
🔸 {subscribe_prices["month"]["price"]} zł / miesiąc — pełny dostęp.

<b>Pełny dostęp:</b>
• powiadomienia, gdy pojawiają się nowe mieszkania 🏠
• możliwość zapisywania wyników wyszukiwania 📋
• darmowy poradnik o wynajmie 🧾

<i>💬 Opłacając subskrypcję i korzystając z wyszukiwania mieszkań, automatycznie potwierdzasz, że zapoznałeś się i zgadzasz się z regulaminem i polityką prywatności Domio</i>''',
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
    "sub_settings_full": {
        "uk": '''Твоя підписка активна до: <b>{until}</b>\nПовний доступ: ✅''',
        "en": '''Your subscription is active until: <b>{until}</b>\nFull access: ✅''',
        "pl": '''Twoja subskrypcja jest aktywna do: <b>{until}</b>\nPełny dostęp: ✅''',
    },
    "sub_settings": {
        "uk": '''Твоя підписка активна до: <b>{until}</b>\nПовний доступ: ❌''',
        "en": '''Your subscription is active until: <b>{until}</b>\nFull access: ❌''',
        "pl": '''Twoja subskrypcja jest aktywna do: <b>{until}</b>\nPełny dostęp: ❌''',
    },
    "no_sub_settings": {
        "uk": '''Твоя підписка не активна''',
        "en": '''Your subscription is not active''',
        "pl": '''Twoja subskrypcja nie jest aktywna''',
    },
    "autocontinue_info": {
        "uk": '''Підписка буде автоматично продовжена <b>{date}.</b>''',
        "en": '''The subscription will be automatically renewed on <b>{date}.</b>''',
        "pl": '''Subskrypcja zostanie automatycznie odnowiona <b>{date}.</b>''',
    },

    "earn_with_domio": {
        "uk": "<b>Твоє реферальне посилання:</b>\n{url}\n\nПоточний баланс: {current} PLN\nНараховано за весь час: {total} PLN",
        "en": "<b>Your referral link:</b>\n{url}\n\nYour current balance: {current} PLN\nTotal earned from referrals: {total} PLN",
        "pl": "<b>Twój link polecający:</b>\n{url}\n\nAktualny stan konta: {current} PLN\nŁącznie zarobiono z poleceń: {total} PLN",
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
    "earn_instruction": {
        "uk": "Інструкція: ",
        "en": "Інструкція: ",
        "pl": "Інструкція: ",
    },
    "ask_earn_payout": {
        "uk": "У тебе на балансі: <b>{current} PLN</b>\n\nТи бажаешь вивести гроші за рефералів?",
        "en": "You have <b>{current} PLN</b> on your balance.\n\nWould you like to withdraw referral earnings?",
        "pl": "Na Twoim koncie: <b>{current} PLN</b>\n\nCzy chcesz wypłacić środki z poleceń?",
    },
    "payout_request_sended": {
        "uk": "Твій запит на вивід коштів за рефералів відправлений.\n<b>Сумма: {amount} PLN</b>\n\nНаш менеджер зв'яжеться з тобою найближчим часом!",
        "en": "Your withdrawal request for referral earnings has been sent.\n<b>Amount: {amount} PLN</b>\n\nOur manager will contact you shortly!",
        "pl": "Twoje zlecenie wypłaty środków z poleceń zostało wysłane.\n<b>Kwota: {amount} PLN</b>\n\nNasz menedżer skontaktuje się z Tobą wkrótce!",
    },
    "only_full_sub": {
        "uk": "Ця функція доступна лише в повному доступі!",
        "en": "This feature is available only with full access!",
        "pl": "Ta funkcja jest dostępna tylko w ramach pełnego dostępu!",
    },
    "how_to_use": {
        "uk": "Обери інструкцію 👇",
        "en": "Choose an instruction 👇",
        "pl": "Wybierz instrukcję 👇",
    },
    "instruction_rent": {
        "uk": "Тримай покрокову інструкцію з пошуку оренди без комісії в Domio.",
        "en": "Here’s a step-by-step guide to finding rentals without commission on Domio.",
        "pl": "Oto instrukcja krok po kroku, jak znaleźć wynajem bez prowizji w Domio."
    },
    "instruction_mortgage": {
        "uk": "Тримай покрокову інструкцію як перевірити свою кредитоспроможність.",
        "en": "Here’s a step-by-step guide on how to check your creditworthiness.",
        "pl": "Oto instrukcja krok po kroku, jak sprawdzić swoją zdolność kredytową."
    },
    "instruction_access": {
        "uk": "Тримай покрокову інструкцію, як оформити доступ у Domio.",
        "en": "Here’s a step-by-step guide on how to get access in Domio.",
        "pl": "Oto instrukcja krok po kroku, jak uzyskać dostęp w Domio."
    },
    "instruction_services": {
        "uk": "Тримай покрокову інструкцію, як працюють Додаткові послуги в Domio.",
        "en": "Here’s a step-by-step guide on how the Additional Services in Domio work.",
        "pl": "Oto instrukcja krok po kroku, jak działają Usługi Dodatkowe w Domio."
    },
    "instruction_earn": {
        "uk": "Тримай покрокову інструкцію, як можна заробляти разом з Domio.",
        "en": "Here’s a step-by-step guide on how you can earn with Domio.",
        "pl": "Oto instrukcja krok po kroku, jak możesz zarabiać z Domio."
    },
    "instruction_primary": {
        "uk": "Тримай покрокову інструкцію з пошуку купівлі нерухомості без комісії в Domio.",
        "en": "Here’s a step-by-step guide to finding property purchases without commission on Domio.",
        "pl": "Oto instrukcja krok po kroku, jak znaleźć nieruchomość na sprzedaż bez prowizji w Domio."
    },
    "instruction_secondary": {
        "uk": "Тримай покрокову інструкцію з пошуку купівлі нерухомості без комісії в Domio.",
        "en": "Here’s a step-by-step guide to buying property without commission on Domio.",
        "pl": "Oto instrukcja krok po kroku, jak kupić nieruchomość bez prowizji w Domio."
    },

}

VIDEO_IDS = {
    "instruction_rent": {
        "uk": "",
        "en": "",
        "pl": ""
    },
    "instruction_mortgage": {
        "uk": "",
        "en": "",
        "pl": ""
    },
    "instruction_access": {
        "uk": "",
        "en": "",
        "pl": ""
    },
    "instruction_services": {
        "uk": "",
        "en": "",
        "pl": ""
    },
    "instruction_earn": {
        "uk": "",
        "en": "",
        "pl": ""
    },
    "instruction_primary": {
        "uk": "",
        "en": "",
        "pl": ""
    },
    "instruction_secondary": {
        "uk": "",
        "en": "",
        "pl": ""
    }

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
        "uk": "🪄 Як користуватися",
        "en": "🪄 How to use",
        "pl": "🪄 Jak korzystać",
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
        "uk": "🛠 Інші послуги",
        "en": "🛠 Other services",
        "pl": "🛠 Inne usługi",
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
        "uk": "🌐 Змінити мову",
        "en": "🌐 Change language",
        "pl": "🌐 Zmień język",
    },
    "recurring": {
        "uk": "❌ Вимкнути автопродовження",
        "en": "❌ Turn off auto-renewal",
        "pl": "❌ Wyłącz automatyczne odnawianie",
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
        "pl": "🗺 Mapa",
    },
    "instruction_btn": {
        "uk": "Інструкція",
        "en": "Instruction",
        "pl": "Instrukcja"
    },
    "pay_out_btn": {
        "uk": "Вивести гроші",
        "en": "Withdraw money",
        "pl": "Wypłać pieniądze"
    },
    "instruction_rent_btn": {
        "uk": "Для оренди квартири",
        "en": "For renting an apartment",
        "pl": "Dla wynajmu mieszkania"
    },
    "instruction_buy_btn": {
        "uk": "Для купівлі квартири",
        "en": "For buying an apartment",
        "pl": "Dla zakupu mieszkania"
    },
    "instruction_mortgage_btn": {
        "uk": "Для Іпотеки",
        "en": "For mortgage",
        "pl": "Dla kredytu hipotecznego"
    },
    "instruction_access_btn": {
        "uk": "Як оформити доступ",
        "en": "How to get access",
        "pl": "Jak uzyskać dostęp"
    },
    "instruction_services_btn": {
        "uk": "Як працюють Додаткові послуги",
        "en": "How additional services work",
        "pl": "Jak działają usługi dodatkowe"
    },
    "instruction_earn_btn": {
        "uk": "Як можна заробляти з Domio",
        "en": "How to earn with Domio",
        "pl": "Jak zarabiać z Domio"
    },
    "instruction_primary_btn": {
        "uk": "Первинний ринок",
        "en": "Primary market",
        "pl": "Rynek pierwotny"
    },
    "instruction_secondary_btn": {
        "uk": "Вторинний ринок",
        "en": "Secondary market",
        "pl": "Rynek wtórny"
    }

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
    "no_ref_balance": {
        "uk": "Порожній баланс",
        "en": "Empty balance",
        "pl": "Brak środków",
    },
    "not_aval_in_test": {
        "uk": "Ця функція доступна лише в повному доступі!",
        "en": "This feature is available only with full access!",
        "pl": "Ta funkcja jest dostępna tylko w ramach pełnego dostępu!",
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

def vid(lang: Lang | None, key: str) -> str:
    """Возвращает айди видео по ключу и языку с fallback на uk."""
    return VIDEO_IDS.get(key, {}).get(lang or "uk", VIDEO_IDS.get(key, {}).get("uk"))

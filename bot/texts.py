from typing import Literal, Dict
from config import TARIFFS_DICT, DOMIO_INSTAGRAM

guide_price = TARIFFS_DICT["ONE_TIME"]["guides"]["price"]
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
    "comissiom_type":  {
        "uk": "Тільки <b>Без комісії</b>",
        "en": "Only <b>No commission</b>",
        "pl": "Tylko <b>Bez prowizji</b>",
    },
    "builders_type":  {
        "uk": "Вибери <b>тип послуги</b>",
        "en": "Choose <b>service type</b>",
        "pl": "Wybierz <b>typ usługi</b>",
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
        "uk": "🌆 Вибери <b>місто</b>",
        "en": "🌆 Choose <b>city</b>",
        "pl": "🌆 Wybierz <b>miasto</b>",
    },
    "select_city_agent": {
        "uk": "🌆 Вибери <b>місто</b>",
        "en": "🌆 Choose <b>city</b>",
        "pl": "🌆 Wybierz <b>miasto</b>",
    },
    "select_city_builders": {
        "uk": "🌆 Вибери <b>місто</b>",
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
    "price_range": {
        "uk": "Впиши бюджет <b>від до</b>,\nнаприклад 3000-5000",
        "en": "Enter the budget <b>from–to</b>,\nfor example 3000–5000",
        "pl": "Wpisz budżet <b>od do</b>,\nna przykład 3000–5000"
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
    "instruction_sale": {
        "uk": "Тримай покрокову інструкцію з пошуку купівлі нерухомості без комісії в Domio.",
        "en": "Here’s a step-by-step guide to finding property purchases without commission on Domio.",
        "pl": "Oto instrukcja krok po kroku, jak znaleźć nieruchomość na sprzedaż bez prowizji w Domio."
    },
    "guides": {
        "uk": f'''<b>📚 База знань Domio</b>
Тут ти знайдеш гайди, які допоможуть безпечно орендувати квартиру й крок за кроком купити власне житло в Польщі.

<b>✅ Інструкції по оренді</b> — <i>безкоштовні для користувачів з повною підпискою.</i>
<b>💡 Гайд з купівлі нерухомості</b> — доступний окремо за {guide_price:.0f} зл.''',
        "en": f'''<b>📚 Domio Knowledge Base</b>
Here you'll find guides that help you safely rent an apartment and step-by-step buy your own home in Poland.

<b>✅ Rental instructions</b> — <i>free for users with a full subscription.</i>
<b>💡 Home-buying guide</b> — available separately for {guide_price:.0f} PLN.''',
        "pl": f'''<b>📚 Baza wiedzy Domio</b>
Tutaj znajdziesz poradniki, które pomogą bezpiecznie wynająć mieszkanie i krok po kroku kupić własne mieszkanie w Polsce.

<b>✅ Instrukcje dotyczące wynajmu</b> — <i>darmowe dla użytkowników z pełną subskrypcją.</i>
<b>💡 Poradnik kupna nieruchomości</b> — dostępny osobno za {guide_price:.0f} zł.''',
    },
    "guides_rent": {
        "uk": "🎧 Тут ти знайдеш гайд, який допоможе безпечно орендувати квартиру в Польщі.\nКористуйся — і оренда стане простою та спокійною.",
        "en": "🎧 Here you’ll find a guide to help you safely rent an apartment in Poland.\nUse it — and renting will become simple and worry-free.",
        "pl": "🎧 Tutaj znajdziesz poradnik, który pomoże Ci bezpiecznie wynająć mieszkanie w Polsce.\nKorzystaj — a wynajem stanie się prosty i bezstresowy."
    },
    "guides_sale": {
        "uk": "<b>📘 Е-бук “Крок за кроком: як купити нерухомість у Польщі”</b>\nУ цьому гайді я детально пояснюю, як самостійно знайти, перевірити й купити своє житло в Польщі — квартиру, дім чи таунхаус.\nЯ зібрав тут увесь свій досвід з 2017 року, коли купив свою першу квартиру в Польщі. Тепер, як ліцензований ріелтор, я ділюся перевіреними кроками, щоб ти міг упевнено пройти весь процес без помилок.\n\n📖 Усередині ти знайдеш — <a href=\"{toc_link}\">Зміст</a>\n\n💰 Вартість: 99 зл\n(Е-бук доступний у форматі PDF після оплати)",
        "en": "<b>📘 E-book “Step by Step: How to Buy Property in Poland”</b>\nIn this guide, I explain in detail how to independently find, verify, and buy your own home in Poland — an apartment, house, or townhouse.\nI’ve gathered all my experience since 2017, when I bought my first apartment in Poland. Now, as a licensed realtor, I share proven steps so you can confidently go through the entire process without mistakes.\n\n📖 Inside you’ll find — <a href=\"{toc_link}\">Table of Contents</a>\n\n💰 Price: 99 PLN\n(The e-book is available in PDF format after payment)",
        "pl": "<b>📘 E-book „Krok po kroku: jak kupić nieruchomość w Polsce”</b>\nW tym poradniku szczegółowo wyjaśniam, jak samodzielnie znaleźć, sprawdzić i kupić własne mieszkanie w Polsce — apartament, dom lub segment.\nZebrałem tu całe moje doświadczenie od 2017 roku, kiedy kupiłem swoje pierwsze mieszkanie w Polsce. Teraz, jako licencjonowany agent nieruchomości, dzielę się sprawdzonymi krokami, abyś mógł pewnie przejść cały proces bez błędów.\n\n📖 W środku znajdziesz — <a href=\"{toc_link}\">Spis treści</a>\n\n💰 Cena: 99 zł\n(E-book dostępny w formacie PDF po dokonaniu płatności)"
    },
    "service_not_availabel": {
        "uk": f"😔 Вибач, але зараз у твоєму регіоні ми ще не маємо партнерів для цієї послуги.\n\nМи активно розширюємо мережу перевірених фахівців — як тільки з’являться у твоєму місті, ми повідомимо 🏙️\n\nПідписуйся на наш Instagram, щоб бути в курсі оновлень 👉 <a href=\"{DOMIO_INSTAGRAM}\">Domio</a>",
        "en": f"😔 Sorry, but we currently don’t have partners offering this service in your region.\n\nWe’re actively expanding our network of verified specialists — as soon as they appear in your city, we’ll let you know 🏙️\n\nFollow us on Instagram to stay updated 👉 <a href=\"{DOMIO_INSTAGRAM}\">Domio</a>",
        "pl": f"😔 Przepraszamy, ale obecnie nie mamy partnerów świadczących tę usługę w Twoim regionie.\n\nAktywnie rozwijamy naszą sieć sprawdzonych specjalistów — gdy tylko pojawią się w Twoim mieście, damy Ci znać 🏙️\n\nŚledź nas na Instagramie, aby być na bieżąco 👉 <a href=\"{DOMIO_INSTAGRAM}\">Domio</a>",
    },
    "wait_description_service": {
        "uk": '''Напиши коротко, що потрібно зробити  
та свій номер телефону 📞.

📝 Залиш заявку  
Залишаючи заявку, ти підтверджуєш, що ознайомився з Регламентом і Політикою конфіденційності Domio.
''',
        "en": '''Briefly describe what needs to be done  
and leave your phone number 📞.

📝 Submit a request  
By submitting the request, you confirm that you have read the Domio Regulations and Privacy Policy.
''',
        "pl": '''Napisz krótko, co trzeba zrobić  
i podaj swój numer telefonu 📞.

📝 Złóż zgłoszenie  
Składając zgłoszenie, potwierdzasz, że zapoznałeś(-aś) się z Regulaminem i Polityką prywatności Domio.
''',
    },
    "moving_transport": {
        "uk": '''<b>🚚 Переїжджаєш? Domio допоможе!</b>

Тут ти можеш залишити свою заявку:
📍звідки і куди треба переїхати,
📞 свої контактні дані.

Менеджер зв’яжеться з тобою, щоб узгодити деталі та вартість.''',
        "en": '''<b>🚚 Moving? Domio can help!</b>

Here you can leave your request:
📍 where you need to move from and to,
📞 your contact details.

A manager will contact you to arrange the details and the price.''',

        "pl": '''<b>🚚 Przeprowadzasz się? Domio pomoże!</b>

Tutaj możesz zostawić swoje zgłoszenie:
📍 skąd i dokąd trzeba się przeprowadzić,
📞 swoje dane kontaktowe.

Menadżer skontaktuje się z Tobą, aby uzgodnić szczegóły i koszt.''',
    },
    "wait_start_address_service": {
        "uk": "Вкажи <b>звідки</b>",
        "en": "Enter <b>from where</b>",
        "pl": "Podaj <b>skąd</b>",
    },
    "wait_end_address_service": {
        "uk": "Вкажи <b>куди</b>",
        "en": "Enter <b>to where</b>",
        "pl": "Podaj <b>dokąd</b>",
    },
    "request_was_accepted": {
        "uk": "Ваша заявка <b>прийнята!</b>",
        "en": "Your request has been <b>accepted!</b>",
        "pl": "Twoje zgłoszenie zostało <b>zaakceptowane!</b>",
    },
}

CONTACTS = {
    "krakow_notary_contact": {
        "uk": "• д-р Лілія Твардош  \nтел.: 12 259 44 29, 607 505 145  \nфакс: 12 259 44 29  \ne-mail: lilija.twardosz@kin.pl  \nвебсайт: LilijaTwardosz.Notariusz.pl\n\n• Notariusz Sandra Błaszczyk-Kozłowska  \nАдреса: ul. Kalwaryjska 12/12, 30-509 Kraków  \nТелефон: +48 12-341-46-39  \nEmail: kancelaria@notariuszekalwaryjska.pl",
        "en": "• Dr. Lilia Twardosz  \nTel.: 12 259 44 29, 607 505 145  \nFax: 12 259 44 29  \nEmail: lilija.twardosz@kin.pl  \nWebsite: LilijaTwardosz.Notariusz.pl\n\n• Notary Sandra Błaszczyk-Kozłowska  \nAddress: ul. Kalwaryjska 12/12, 30-509 Kraków  \nPhone: +48 12-341-46-39  \nEmail: kancelaria@notariuszekalwaryjska.pl",
        "pl": "• dr Lilia Twardosz  \ntel.: 12 259 44 29, 607 505 145  \nfaks: 12 259 44 29  \ne-mail: lilija.twardosz@kin.pl  \nstrona: LilijaTwardosz.Notariusz.pl\n\n• Notariusz Sandra Błaszczyk-Kozłowska  \nAdres: ul. Kalwaryjska 12/12, 30-509 Kraków  \nTelefon: +48 12-341-46-39  \nEmail: kancelaria@notariuszekalwaryjska.pl"
    },

    "katowice_notary_contact": {
        "uk": "• Kancelaria Notarialna Halina Mikołajczyk & Agnieszka Mikołajczyk  \nАдреса: ul. Młyńska 5/4, 40-098 Katowice  \nТелефон: +48 517 440 771, 32 253 86 22, 32 253 86 30  \nEmail: mikolajczyk@kancelarie-notarialne.info.pl, halinamikolajczyk@notariusz.pl\n\n• Kancelaria Notarialna Zuzanna Wojtaszek-Bałazińska & Kinga Bednarz-Wysocka  \nАдреса: ul. Żelazna 4, 40-851 Katowice  \nТелефон: +48 32 307 55 54, +48 883 314 408  \nEmail: kancelaria@NotarialnaKatowice.pl",
        "en": "• Notary Office Halina Mikołajczyk & Agnieszka Mikołajczyk  \nAddress: ul. Młyńska 5/4, 40-098 Katowice  \nPhone: +48 517 440 771, 32 253 86 22, 32 253 86 30  \nEmail: mikolajczyk@kancelarie-notarialne.info.pl, halinamikolajczyk@notariusz.pl\n\n• Notary Office Zuzanna Wojtaszek-Bałazińska & Kinga Bednarz-Wysocka  \nAddress: ul. Żelazna 4, 40-851 Katowice  \nPhone: +48 32 307 55 54, +48 883 314 408  \nEmail: kancelaria@NotarialnaKatowice.pl",
        "pl": "• Kancelaria Notarialna Halina Mikołajczyk & Agnieszka Mikołajczyk  \nAdres: ul. Młyńska 5/4, 40-098 Katowice  \nTelefon: +48 517 440 771, 32 253 86 22, 32 253 86 30  \nEmail: mikolajczyk@kancelarie-notarialne.info.pl, halinamikolajczyk@notariusz.pl\n\n• Kancelaria Notarialna Zuzanna Wojtaszek-Bałazińska & Kinga Bednarz-Wysocka  \nAdres: ul. Żelazna 4, 40-851 Katowice  \nTelefon: +48 32 307 55 54, +48 883 314 408  \nEmail: kancelaria@NotarialnaKatowice.pl"
    },

    "wroclaw_notary_contact": {
        "uk": "• Kancelaria Notarialna Justyna Pelc-Woldan  \nАдреса: ul. Szczytnicka 54/3, 50-382 Wrocław  \nТелефон: +48 510 103 433, +48 510 103 499  \nEmail: kancelaria@nasznotariusz.pl\n\n• Kancelaria Notarialna Bartosz Katarzyński  \nАдреса: ul. Wielka 29/3, 53-338 Wrocław  \nТелефон: +48 797 573 705, +48 71 342 00 12  \nEmail: kancelaria@notariuszkatarzynski.pl",
        "en": "• Notary Office Justyna Pelc-Woldan  \nAddress: ul. Szczytnicka 54/3, 50-382 Wrocław  \nPhone: +48 510 103 433, +48 510 103 499  \nEmail: kancelaria@nasznotariusz.pl\n\n• Notary Office Bartosz Katarzyński  \nAddress: ul. Wielka 29/3, 53-338 Wrocław  \nPhone: +48 797 573 705, +48 71 342 00 12  \nEmail: kancelaria@notariuszkatarzynski.pl",
        "pl": "• Kancelaria Notarialna Justyna Pelc-Woldan  \nAdres: ul. Szczytnicka 54/3, 50-382 Wrocław  \nTelefon: +48 510 103 433, +48 510 103 499  \nEmail: kancelaria@nasznotariusz.pl\n\n• Kancelaria Notarialna Bartosz Katarzyński  \nAdres: ul. Wielka 29/3, 53-338 Wrocław  \nTelefon: +48 797 573 705, +48 71 342 00 12  \nEmail: kancelaria@notariuszkatarzynski.pl"
    },

    "poznan_notary_contact": {
        "uk": "• Kancelaria Notarialna Magdalena Fret-Gołaś & Złata Liwinska-Zając  \nАдреса: ul. Matejki 44/2, 60-767 Poznań  \nТелефон: +48 517 767 400  \nEmail: notariusz@golas-zajac.pl\n\n• Kancelaria Notarialna Tomasz Trytt  \nАдреса: ul. Zeylanda 6/5, Poznań  \nТелефон: 61 662 81 31, 535 535 636  \nEmail: kancelaria@notariuszepoznan.pl",
        "en": "• Notary Office Magdalena Fret-Gołaś & Złata Liwinska-Zając  \nAddress: ul. Matejki 44/2, 60-767 Poznań  \nPhone: +48 517 767 400  \nEmail: notariusz@golas-zajac.pl\n\n• Notary Office Tomasz Trytt  \nAddress: ul. Zeylanda 6/5, Poznań  \nPhone: 61 662 81 31, 535 535 636  \nEmail: kancelaria@notariuszepoznan.pl",
        "pl": "• Kancelaria Notarialna Magdalena Fret-Gołaś & Złata Liwinska-Zając  \nAdres: ul. Matejki 44/2, 60-767 Poznań  \nTelefon: +48 517 767 400  \nEmail: notariusz@golas-zajac.pl\n\n• Kancelaria Notarialna Tomasz Trytt  \nAdres: ul. Zeylanda 6/5, Poznań  \nTelefon: 61 662 81 31, 535 535 636  \nEmail: kancelaria@notariuszepoznan.pl"
    },

    "warszawa_notary_contact": {
        "uk": "• Kancelaria Notarialna Marta Chemperek & Emilia Karwowska-Lelak  \nАдреса: ul. Ludwika Idzikowskiego 16, 00-710 Warszawa  \nТелефон: 22 245 48 48, +48 888 888 434, +48 888 888 435  \nEmail: biuro@notariusz-warszawski.pl\n\n• Kancelaria Notarialna Karolina Kowalik & Małgorzata Kowalewska-Łагуна  \nАдреса: ul. Hoża 37/16, 00-681 Warszawa  \nТелефон: +48 508 965 517, +48 22 416 95 17  \nEmail: kancelaria@warszawanotariusze.pl",
        "en": "• Notary Office Marta Chemperek & Emilia Karwowska-Lelak  \nAddress: ul. Ludwika Idzikowskiego 16, 00-710 Warsaw  \nPhone: 22 245 48 48, +48 888 888 434, +48 888 888 435  \nEmail: biuro@notariusz-warszawski.pl\n\n• Notary Office Karolina Kowalik & Małgorzata Kowalewska-Łaguna  \nAddress: ul. Hoża 37/16, 00-681 Warsaw  \nPhone: +48 508 965 517, +48 22 416 95 17  \nEmail: kancelaria@warszawanotariusze.pl",
        "pl": "• Kancelaria Notarialna Marta Chemperek & Emilia Karwowska-Lelak  \nAdres: ul. Ludwika Idzikowskiego 16, 00-710 Warszawa  \nTelefon: 22 245 48 48, +48 888 888 434, +48 888 888 435  \nEmail: biuro@notariusz-warszawski.pl\n\n• Kancelaria Notarialna Karolina Kowalik & Małgorzata Kowalewska-Łagуна  \nAdres: ul. Hoża 37/16, 00-681 Warszawa  \nTelefon: +48 508 965 517, +48 22 416 95 17  \nEmail: kancelaria@warszawanotariusze.pl"
    },

    "gdansk_notary_contact": {
        "uk": "• Kancelaria Notarialna Sylwia Burdach & Ewelina Jabłońska  \nАдреса: ul. Sobótki 10b/2, 80-247 Gdańsk  \nТелефон: 536 204 218, 536 728 449  \nEmail: kancelarianotarialnawrzeszcz@gmail.com\n\n• Kancelaria Notarialna Michał Ciechanowski  \nАдреса: ul. Kartuska 260, 80-125 Gdańsk  \nТелефон: +48 58 765 73 70  \nEmail: biuro@notariusz-gdansk.com.pl",
        "en": "• Notary Office Sylwia Burdach & Ewelina Jabłońska  \nAddress: ul. Sobótki 10b/2, 80-247 Gdańsk  \nPhone: 536 204 218, 536 728 449  \nEmail: kancelarianotarialnawrzeszcz@gmail.com\n\n• Notary Office Michał Ciechanowski  \nAddress: ul. Kartuska 260, 80-125 Gdańsk  \nPhone: +48 58 765 73 70  \nEmail: biuro@notariusz-gdansk.com.pl",
        "pl": "• Kancelaria Notarialna Sylwia Burdach & Ewelina Jabłońska  \nAdres: ul. Sobótki 10b/2, 80-247 Gdańsk  \nTelefon: 536 204 218, 536 728 449  \nEmail: kancelarianotarialnawrzeszcz@gmail.com\n\n• Kancelaria Notarialna Michał Ciechanowski  \nAdres: ul. Kartuska 260, 80-125 Gdańsk  \nTelefon: +48 58 765 73 70  \nEmail: biuro@notariusz-gdansk.com.pl"
    },

    "szczecin_notary_contact": {
        "uk": "• Kancelaria Notarialna Konrad Stuła & Michał Sosnowski  \nАдреса: ul. Grodzka 20/2, 70-560 Szczecin  \nТелефон: +48 91 350 75 71, +48 730 505 984  \nEmail: notariusz@stula.com.pl\n\n• Kancelaria Notarialna Izabela Link  \nАдреса: ul. Niemierzyńska 23/U2, 71-436 Szczecin  \nТелефон: +48 667 530 131  \nEmail: kontakt@notariuszlink.pl",
        "en": "• Notary Office Konrad Stuła & Michał Sosnowski  \nAddress: ul. Grodzka 20/2, 70-560 Szczecin  \nPhone: +48 91 350 75 71, +48 730 505 984  \nEmail: notariusz@stula.com.pl\n\n• Notary Office Izabela Link  \nAddress: ul. Niemierzyńska 23/U2, 71-436 Szczecin  \nPhone: +48 667 530 131  \nEmail: kontakt@notariuszlink.pl",
        "pl": "• Kancelaria Notarialna Konrad Stuła & Michał Sosnowski  \nAdres: ul. Grodzka 20/2, 70-560 Szczecin  \nTelefon: +48 91 350 75 71, +48 730 505 984  \nEmail: notariusz@stula.com.pl\n\n• Kancelaria Notarialna Izabela Link  \nAdres: ul. Niemierzyńska 23/U2, 71-436 Szczecin  \nTelefon: +48 667 530 131  \nEmail: kontakt@notariuszlink.pl"
    },

    "lodz_notary_contact": {
        "uk": "• Notariusz Piotr Ciepły – Kancelaria Notarialna  \nАдреса: ul. Zachodnia 70, 90-403 Łódź  \nТелефон: (42) 664-69-29, +48 609 918 160  \nEmail: piotr.cieply@notariusze.lodz.pl\n\n• Kancelaria Notarialna Kułaj & Wasiak s.c.  \nАдреса: ul. Rzgowska 30, 93-172 Łódź  \nТелефон: +48 42 203 9 203, 515 05 77 71, 515 05 77 72  \nEmail: kancelaria@notariuszekw.pl",
        "en": "• Notary Piotr Ciepły – Notary Office  \nAddress: ul. Zachodnia 70, 90-403 Łódź  \nPhone: (42) 664-69-29, +48 609 918 160  \nEmail: piotr.cieply@notariusze.lodz.pl\n\n• Notary Office Kułaj & Wasiak s.c.  \nAddress: ul. Rzgowska 30, 93-172 Łódź  \nPhone: +48 42 203 9 203, 515 05 77 71, 515 05 77 72  \nEmail: kancelaria@notariuszekw.pl",
        "pl": "• Notariusz Piotr Ciepły – Kancelaria Notarialna  \nAdres: ul. Zachodnia 70, 90-403 Łódź  \nTelefon: (42) 664-69-29, +48 609 918 160  \nEmail: piotr.cieply@notariusze.lodz.pl\n\n• Kancelaria Notarialna Kułaj & Wasiak s.c.  \nAdres: ul. Rzgowska 30, 93-172 Łódź  \nTelefon: +48 42 203 9 203, 515 05 77 71, 515 05 77 72  \nEmail: kancelaria@notariuszekw.pl"
    },
    
    "katowice_sworn_translator_contact": {
        "uk": "Ім’я: Shemetov Oleg\nАдреса: Zofii Nałkowskiej 14/46, 40-425 Katowice\nТелефон: 539-190-185\nE-mail: shemetovo@gmail.com",
        "en": "Name: Białecka Barbara\nAddress: ul. Kanarków 6C, 40-535 Katowice\nPhone: 789-311-277\nE-mail: bialecka@pro.onet.pl",
        "pl": "katowice_sworn_translator_contact"
    },

    "wroclaw_sworn_translator_contact": {
        "uk": "Ім’я: Sofia Baianova\nАдреса: ul. Nyska 50/42, 50-505 Wrocław\nТелефон: 727 779 929\nE-mail: biuro@doslivno.pl",
        "en": "Name: Antosz Maria\nAddress: ul. Białowieska 77/6, 54-234 Wrocław\nPhone: 518 595 024\nE-mail: katarzynantosz@gmail.com",
        "pl": "wroclaw_sworn_translator_contact"
    },

    "poznan_sworn_translator_contact": {
        "uk": "Ім’я: Khrystyna Antoniak\nАдреса: ul. Daleka 37/16, 60-124 Poznań\nТелефон: 451 085 786\nE-mail: k.antoniak@gmail.com",
        "en": "Name: Apenuvor Agnieszka\nAddress: ul. Wierzbięcice 51/3, 61-547 Poznań\nPhone: 510 324 427\nE-mail: agnieszka.apenuvor@gmail.com",
        "pl": "poznan_sworn_translator_contact"
    },

    "warsaw_sworn_translator_contact": {
        "uk": "Ім’я: Piotr Antuszewicz\nАдреса: ul. Kasprowicza 12/2, 01-871 Warszawa\nТелефон: 667 728 348\nE-mail: piotr.antuszewicz@gmail.com",
        "en": "Name: Arczewska Anna\nAddress: ul. Sienna 72A/901, 00-833 Warszawa\nPhone: 601 614 084\nE-mail: traducciones@onet.pl",
        "pl": "warsaw_sworn_translator_contact"
    },

    "gdansk_sworn_translator_contact": {
        "uk": "Ім’я: Ilona Bieszke\nАдреса: ul. Traugutta 4/2, 80-221 Gdańsk\nТелефон: 790 769 103\nE-mail: ilona.bieszke@gmail.com",
        "en": "Name: Bańko-Karczewska Dorota\nAddress: ul. Staszica 6/5, 80-262 Gdańsk\nPhone: (58) 623-36-79, 609-726-357\nE-mail: dorota.banko@bankotlumaczenia.pl",
        "pl": "gdansk_sworn_translator_contact"
    },

    "szczecin_sworn_translator_contact": {
        "uk": "Ім’я: Jurij Czajka\nАдреса: ul. Żubrów 6/106, 71-617 Szczecin\nТелефон: 536 446 307\nE-mail: chaika.tlumaczenia@gmail.com",
        "en": "Name: Baranowski Marian\nAddress: ul. Kwiatów Polskich 69, 71-499 Szczecin\nPhone: 604 969 649\nE-mail: incontra@baranowska.pl",
        "pl": "szczecin_sworn_translator_contact"
    },

    "lodz_sworn_translator_contact": {
        "uk": "Ім’я: Mariia Bakerenkova\nАдреса: ul. Rzgowska 315 m 21, 93-338 Łódź\nТелефон: 880 101 188\nE-mail: m.tlumacz.ua@gmail.com",
        "en": "Name: Andrzejewska Agata\nAddress: ul. Narutowicza 94/17, 90-139 Łódź\nPhone: (42) 635-16-90",
        "pl": "lodz_sworn_translator_contact"
    },

    "krakow_sworn_translator_contact": {
        "uk": "Ім’я: Anna Starzec\nТелефон: +48 782 334 670\nСайт: https://oldmastersolution.pl/",
        "en": "Name: Jabłonowska Ewa\nPhone: +48 602-753-992\nE-mail: ewa@edjtranslations.com.pl",
        "pl": "krakow_sworn_translator_contact"
    },

    "technical_acceptance_contact": {
        "uk": '''Domio співпрацює з перевіреною фірмою PewnyLokal, яка проводить професійний огляд житла перед покупкою 🧰

📎 Контакт фірми: https://pewnylokal.pl/ukrainian''',
        "en": '''Domio cooperates with the trusted company PewnyLokal, which performs professional home inspections before purchase 🧰

📎 Company contact: https://pewnylokal.pl/english''',

        "pl": '''Domio współpracuje ze sprawdzoną firmą PewnyLokal, która przeprowadza profesjonalną inspekcję mieszkania przed zakupem 🧰

📎 Kontakt firmy: https://pewnylokal.pl/rezerwacja''',
    }

}

VIDEO_IDS = {
    "instruction_rent": {
        "uk": "BAACAgQAAxkBAAIIe2kXNwkGfhYcLVCUDJsNCIEkuwG6AAKKFwACqgK4UF3KgCCeJ7XFNgQ",
        "en": "BAACAgQAAxkBAAIIfWkXNyCdG0doq-daPc8iJjG8BHFGAAKSFwACqgK4UHwrQqarCyXLNgQ",
        "pl": "BAACAgQAAxkBAAIIg2kXN099j10fBgUEKRZUwO1ZFZ3jAAJWGwACqnC5UFUXdaaNYtceNgQ"
    },
    "instruction_sale": {
        "uk": "BAACAgQAAxkBAAIIdGkXNIPZQVQBCsrIVtkchB9GqSktAAKJFwACqgK4UJ2gNrSQ4ignNgQ",
        "en": "BAACAgQAAxkBAAIIf2kXNzTiPVTtfmZjzGQmoqr7bYUSAAKUFwACqgK4UEifRyYD9fHWNgQ",
        "pl": "BAACAgQAAxkBAAIIgWkXN0FBRuEjizHk52c09S2aYCJIAAJVGwACqnC5UBpDkg0gq9KgNgQ"
    }

}

GUIDE_URLS = {
    'rent': { # райд по оренде недвижимости
        "uk": "https://drive.google.com/file/d/1uQbxKew903rURIvrMNybnZDSbWmr9H3V/view?usp=drive_link",
        "en": "https://drive.google.com/file/d/1uQbxKew903rURIvrMNybnZDSbWmr9H3V/view?usp=drive_link",
        "pl": "https://drive.google.com/file/d/1uQbxKew903rURIvrMNybnZDSbWmr9H3V/view?usp=drive_link",
    },
    'sale': { # файл Крок за кроком: як купити нерухомість у Польщі 
        "uk": "https://drive.google.com/file/d/1uQbxKew903rURIvrMNybnZDSbWmr9H3V/view?usp=drive_link",
        "en": "https://drive.google.com/file/d/1uQbxKew903rURIvrMNybnZDSbWmr9H3V/view?usp=drive_link",
        "pl": "https://drive.google.com/file/d/1uQbxKew903rURIvrMNybnZDSbWmr9H3V/view?usp=drive_link",
    },
    'guides_sale': { # файл содержания книги Крок за кроком: як купити нерухомість у Польщі 
        "uk": "https://drive.google.com/file/d/1uQbxKew903rURIvrMNybnZDSbWmr9H3V/view?usp=drive_link",
        "en": "https://drive.google.com/file/d/1uQbxKew903rURIvrMNybnZDSbWmr9H3V/view?usp=drive_link",
        "pl": "https://drive.google.com/file/d/1uQbxKew903rURIvrMNybnZDSbWmr9H3V/view?usp=drive_link",
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
    "cancel": {
        "uk": "❌ Відмінити",
        "en": "❌ Cancel",
        "pl": "❌ Anuluj",
    },
    "skip": {
        "uk": "Залишити заявку без коментарів",
        "en": "Leave the request without comments",
        "pl": "Zostaw zgłoszenie bez komentarzy",
    },
    "next": {
        "uk": "➡️ Далі",
        "en": "➡️ Next",
        "pl": "➡️ Dalej",
    },
    "go": {
        "uk": "Поїхали?",
        "en": "Let's go?",
        "pl": "Jedziemy?",
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
        "uk": f"{subscribe_prices['test']['price']} зл / 3 дні",
        "en": f"{subscribe_prices['test']['price']} PLN / 3 days",
        "pl": f"{subscribe_prices['test']['price']} zł / 3 dni",
    },
    "subscribe_main_2week_btn": {
        "uk": f"{subscribe_prices['2week']['price']} зл / 2 тижні",
        "en": f"{subscribe_prices['2week']['price']} PLN / 2 weeks",
        "pl": f"{subscribe_prices['2week']['price']} zł / 2 tyg.",
    },
    "subscribe_main_month_btn": {
        "uk": f"{subscribe_prices['month']['price']} зл / міс",
        "en": f"{subscribe_prices['month']['price']} PLN / mo",
        "pl": f"{subscribe_prices['month']['price']} zł / mies.",
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
    "guide_rent_btn": {
        "uk": "Оренда",
        "en": "Rent",
        "pl": "Wynajem"
    },
    "guide_sale_btn": {
        "uk": "Як крок по кроку купити нерухомість в Польщі",
        "en": "How to buy property in Poland — step by step",
        "pl": "Jak kupić nieruchomość krok po kroku w Polsce"
    },
    "download": {
        "uk": "📥 Скачати",
        "en": "📥 Download",
        "pl": "📥 Pobierz"
    },
    "comission_owner_btn": {
        "uk": "Без комісії",
        "en": "No commission",
        "pl": "Bez prowizji"
    },
    "comission_rieltor_btn": {
        "uk": "З комісією",
        "en": "With commission",
        "pl": "Z prowizją"
    },
    "comission_all_btn": {
        "uk": "Всі оголошення",
        "en": "All listings",
        "pl": "Wszystkie ogłoszenia"
    },
    "repair_turnkey": {
        "uk": "🏠 Ремонт “під ключ”",
        "en": "🏠 Turnkey renovation",
        "pl": "🏠 Remont pod klucz"
    },
    "plumber": {
        "uk": "🚰 Сантехнік / гідравлік",
        "en": "🚰 Plumber / hydraulic",
        "pl": "🚰 Hydraulik"
    },
    "custom_furniture": {
        "uk": "🛋 Майстер меблів на замовлення",
        "en": "🛋 Custom furniture maker",
        "pl": "🛋 Meblarz na zamówienie"
    },
    "electrician": {
        "uk": "🔌 Електрик",
        "en": "🔌 Electrician",
        "pl": "🔌 Elektryk"
    },
    "small_repairs": {
        "uk": "🧹 Дрібний ремонт",
        "en": "🧹 Minor / small repairs",
        "pl": "🧹 Drobny remont"
    },
    "notary": {
        "uk": "🖋️ Нотаріус",
        "en": "🖋️ Notary public",
        "pl": "🖋️ Notariusz"
    },
    "sworn_translator": {
        "uk": "🗣️ Присяжний перекладач",
        "en": "🗣️ Sworn translator",
        "pl": "🗣️ Tłumacz przysięgły"
    },
    "insurance_agent": {
        "uk": "🏡 Страховий агент",
        "en": "🏡 Insurance agent",
        "pl": "🏡 Agent ubezpieczeniowy"
    },
    "moving_transport": {
        "uk": "🚚 Транспорт при переїзді",
        "en": "🚚 Moving transport",
        "pl": "🚚 Transport przy przeprowadzce"
    },
    "cleaning": {
        "uk": "🧹 Прибирання",
        "en": "🧹 Cleaning",
        "pl": "🧹 Sprzątanie"
    },
    "interior_furnishing": {
        "uk": "🪑 Облаштування інтер’єру",
        "en": "🪑 Interior furnishing / design",
        "pl": "🪑 Aranżacja wnętrz"
    },
    "property_appraisal": {
        "uk": "🏠 Оцінка нерухомості (Rzeczoznawca)",
        "en": "🏠 Property appraisal (Rzeczoznawca)",
        "pl": "🏠 Wycena nieruchomości (Rzeczoznawca)"
    },
    "technical_acceptance": {
        "uk": "🏠 Технічний прийом квартири",
        "en": "🏠 Technical inspection / handover of the apartment",
        "pl": "🏠 Odbiór techniczny mieszkania"
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

def guid(lang: Lang | None, key: str) -> str:
    """Возвращает айди видео по ключу и языку с fallback на uk."""
    return GUIDE_URLS.get(key, {}).get(lang or "uk", GUIDE_URLS.get(key, {}).get("uk"))


def contact_key(lang: Lang | None, key: str) -> str:
    """Возвращает айди видео по ключу и языку с fallback на uk."""
    return CONTACTS.get(key, {}).get(lang or "uk", CONTACTS.get(key, {}).get("uk"))
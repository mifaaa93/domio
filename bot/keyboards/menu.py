from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from bot.texts import btn

from db.models import City, District


def get_main_menu(lang: str | None = None) -> ReplyKeyboardMarkup:
    """
    Возвращает основное меню (reply-клавиатура) с локализованными кнопками.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f"{btn(lang, 'search')}"),
                KeyboardButton(text=f"{btn(lang, 'subscribe')}"),
            ],
            [
                KeyboardButton(text=f"{btn(lang, 'how_to_use')}"),
                KeyboardButton(text=f"{btn(lang, 'favorites')}"),
            ],
            [
                KeyboardButton(text=f"{btn(lang, 'guides')}"),
                KeyboardButton(text=f"{btn(lang, 'contact_agent')}"),
            ],
            [
                KeyboardButton(text=f"{btn(lang, 'mortgage')}"),
                KeyboardButton(text=f"{btn(lang, 'builders_services')}"),
            ],
            [
                KeyboardButton(text=f"{btn(lang, 'earn_with_domio')}"),
            ],
            [
                KeyboardButton(text=f"{btn(lang, 'reviews')}"),
                KeyboardButton(text=f"{btn(lang, 'help')}"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder=btn(lang, "placeholder_main_menu"),
    )


def get_search_type_keyboard(lang: str | None = None) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора типа аренды
    """
    rows = [
            [
                InlineKeyboardButton(text=f"{btn(lang, 'rent_btn')}", callback_data="search_type|rent"),
            ],
            [
                InlineKeyboardButton(text=f"{btn(lang, 'sale_btn')}", callback_data="search_type|sale"),
            ]
        ]
    rows.append(
        [InlineKeyboardButton(text=f"{btn(lang, 'back')}", callback_data="main_menu")]
    )
    return InlineKeyboardMarkup(
        inline_keyboard=rows
    )


def get_estate_type_keyboard(lang: str | None = None, deal_type: str= None) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора типа недвижимости
    """
    rows = [
            [
                InlineKeyboardButton(text=f"{btn(lang, 'apartment_btn')}", callback_data="estate_type|apartment"),
            ],
            [
                InlineKeyboardButton(text=f"{btn(lang, 'house_btn')}", callback_data="estate_type|house"),
            ]
        ]
    if deal_type == "rent":
        rows.append([InlineKeyboardButton(text=f"{btn(lang, 'room_btn')}", callback_data="estate_type|room")])
        
    rows.append(
        [InlineKeyboardButton(text=f"{btn(lang, 'back')}", callback_data="back_from|estate_type")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_market_type_keyboard(lang: str | None = None) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора рынка (первичный, вторичный)
    """
    rows = [
            [
                InlineKeyboardButton(text=f"{btn(lang, 'secondary_btn')}", callback_data="market_type|secondary"),
            ],
            [
                InlineKeyboardButton(text=f"{btn(lang, 'primary_btn')}", callback_data="market_type|primary"),
            ]
        ]
    rows.append(
        [InlineKeyboardButton(text=f"{btn(lang, 'back')}", callback_data="back_from|market_type")]
    )
    return InlineKeyboardMarkup(
        inline_keyboard=rows
    )



def get_select_city_keyboard(lang: str | None = None, cities: list[City] = []) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора города (по два в ряд)
    """
    rows: list[list[InlineKeyboardButton]] = []

    # группируем по 2 города в ряд
    for i in range(0, len(cities), 2):
        pair = cities[i:i + 2]
        row = [
            InlineKeyboardButton(
                text=city.get_name_local(lang),
                callback_data=f"select_city|{city.id}"
            )
            for city in pair
        ]
        rows.append(row)

    # кнопка "Назад"
    rows.append([
        InlineKeyboardButton(text=btn(lang, "back"), callback_data="back_from|select_city")
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_select_district_keyboard(
        lang: str | None = None,
        all_districts: list[District]=[],
        selected_districts:  list[District]=[]) -> InlineKeyboardMarkup:
    '''
    '''
    rows: list[list[InlineKeyboardButton]] = []

    # группируем по 2 города в ряд
    per_row = 3
    for i in range(0, len(all_districts), per_row):
        pair = all_districts[i:i + per_row]
        row = [
            InlineKeyboardButton(
                text=district.get_name_local(lang),
                callback_data=f"select_city|{district.id}"
            )
            for district in pair
        ]
        rows.append(row)

    rows.append([
        InlineKeyboardButton(text=btn(lang, "all_district_btn"), callback_data="back_from|select_district")
    ])
    # кнопка "Назад"
    rows.append([
        InlineKeyboardButton(text=btn(lang, "back"), callback_data="back_from|select_district"),
        InlineKeyboardButton(text=btn(lang, "next"), callback_data="back_from|select_district")
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)
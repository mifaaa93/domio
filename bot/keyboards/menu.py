from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from bot.texts import btn, marker_ok
from bot.utils.helpers import add_query_params
from config import METERS_LIST, MINIAPP_URL
from db.models import City, District, User


def get_main_menu(user: User) -> ReplyKeyboardMarkup:
    """
    Возвращает основное меню (reply-клавиатура) с локализованными кнопками.
    """
    lang = user.language_code
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
                KeyboardButton(text=f"{btn(lang, 'settings')}"),
            ],
        ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
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


def get_comissiom_type_keyboard(lang: str | None = None) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора типа аренды
    """
    rows = [
            [
                InlineKeyboardButton(text=f"{btn(lang, 'comission_owner_btn')}", callback_data="comissiom_type|owner"),
            ],
            [
                InlineKeyboardButton(text=f"{btn(lang, 'comission_rieltor_btn')}", callback_data="comissiom_type|rieltor"),
            ],
            [
                InlineKeyboardButton(text=f"{btn(lang, 'comission_all_btn')}", callback_data="comissiom_type|all"),
            ]
        ]
    rows.append(
        [InlineKeyboardButton(text=f"{btn(lang, 'back')}", callback_data="back_from|comissiom_type")]
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


def get_select_city_keyboard(
        lang: str | None = None,
        cities: list[City] = [],
        callback: str="select_city",
        back: bool=True) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора города (по два в ряд)
    """
    cities = cities or []

    builder = InlineKeyboardBuilder()

    for city in cities:
        builder.button(
            text=city.get_name_local(lang),
            callback_data=f"{callback}|{city.id}",
        )

    # упаковать по 2 в ряд
    builder.adjust(2)

    # кнопка "Назад" отдельной строкой
    if back:
        builder.row(
            InlineKeyboardButton(text=btn(lang, "back"), callback_data="back_from|select_city")
        )

    return builder.as_markup()


def get_select_district_keyboard(
    lang: str | None = None,
    all_districts: list[District] | None = None,
    selected_districts: list[District] | None = None
) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора районов.
    selected_districts — всегда список District.
    """
    all_districts = all_districts or []
    selected_districts = selected_districts or []

    # Быстрые проверки по id
    selected_ids = {d.id for d in selected_districts}

    builder = InlineKeyboardBuilder()

    for district in all_districts:
        title = (
            f"{marker_ok} {district.get_name_local(lang)}"
            if district.id in selected_ids
            else district.get_name_local(lang)
        )
        builder.button(
            text=title,
            callback_data=f"select_district|{district.id}",
        )

    # по 3 в ряд (поменяй на 2/4 при желании)
    builder.adjust(3)

    # "Все районы"
    builder.row(
        InlineKeyboardButton(
            text=btn(lang, "all_district_btn"),
            callback_data="next_select_district|all",
        )
    )

    # Назад / Далее
    builder.row(
        InlineKeyboardButton(text=btn(lang, "back"), callback_data="back_from|select_district"),
        InlineKeyboardButton(text=btn(lang, "next"), callback_data="next_select_district|"),
    )

    return builder.as_markup()


def get_area_from_keyboard(lang: str | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for meters in METERS_LIST:
        builder.button(
            text=btn(lang, "area_from_btn").format(meters=meters),
            callback_data=f"area_from|{meters}",
        )
    # Упаковка по 2 в ряд (поменяй на 3 — будет по три в ряд)
    builder.adjust(2)  # или builder.adjust(3)
    # кнопка любой площади
    builder.row(
        InlineKeyboardButton(text=btn(lang, "any_area_btn"), callback_data="area_from|")
    )
    # Кнопка "Назад" отдельной строкой
    builder.row(
        InlineKeyboardButton(text=btn(lang, "back"), callback_data="back_from|area_from")
    )
    

    return builder.as_markup()


def get_area_to_keyboard(lang: str | None = None, min_area: int=0) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора максимальной площади
    """
    builder = InlineKeyboardBuilder()

    for meters in METERS_LIST:
        if meters > min_area:
            builder.button(
                text=btn(lang, "area_to_btn").format(meters=meters),
                callback_data=f"area_to|{meters}",
            )

    # Упаковка по 2 в ряд (поменяй на 3 — будет по три в ряд)
    builder.adjust(2)  # или builder.adjust(3)

    # кнопка любой площади
    builder.row(
        InlineKeyboardButton(text=btn(lang, "any_area_btn"), callback_data="area_to|")
    )
    # Кнопка "Назад" отдельной строкой
    builder.row(
        InlineKeyboardButton(text=btn(lang, "back"), callback_data="back_from|area_to")
    )

    return builder.as_markup()


def get_rooms_count_keyboard(lang: str | None = None, selected: list[int] = []) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора количества комнат
    """
    builder = InlineKeyboardBuilder()
    selected = selected or []
    for counter in range(1, 6):
        if counter in selected:
            text = f'{marker_ok} {btn(lang, f"rooms_count_btn{counter}")}'
        else:
            text = btn(lang, f"rooms_count_btn{counter}")
        builder.button(
                text=text,
                callback_data=f"rooms_count|{counter}",
            )
    # Упаковка по 2 в ряд (поменяй на 3 — будет по три в ряд)
    builder.adjust(2)  # или builder.adjust(3)

    builder.row(
        InlineKeyboardButton(text=btn(lang, "back"), callback_data="back_from|rooms_count"),
        InlineKeyboardButton(text=btn(lang, "next"), callback_data="rooms_count|"),
    )
    

    return builder.as_markup()


def get_min_price_keyboard(lang: str | None = None) -> InlineKeyboardMarkup:
    """клавиатура при вводе минимальной стоимости цены"""
    builder = InlineKeyboardBuilder()

    # кнопка любой площади
    builder.row(
        InlineKeyboardButton(text=btn(lang, "any_price_btn"), callback_data="min_price|")
    )
    # Кнопка "Назад" отдельной строкой
    builder.row(
        InlineKeyboardButton(text=btn(lang, "back"), callback_data="back_from|min_price")
    )
    
    return builder.as_markup()


def get_max_price_keyboard(lang: str | None = None) -> InlineKeyboardMarkup:
    """клавиатура при вводе макс цены"""
    builder = InlineKeyboardBuilder()

    # кнопка любой площади
    builder.row(
        InlineKeyboardButton(text=btn(lang, "any_price_btn"), callback_data="max_price|")
    )
    # Кнопка "Назад" отдельной строкой
    builder.row(
        InlineKeyboardButton(text=btn(lang, "back"), callback_data="back_from|max_price")
    )
    
    return builder.as_markup()


def get_child_keyboard(lang: str | None = None) -> InlineKeyboardMarkup:
    """клавиатура выбора дети есть нету"""
    builder = InlineKeyboardBuilder()

    # кнопка любой площади
    builder.row(
        InlineKeyboardButton(text=btn(lang, "yes_btn"), callback_data="child|yes"),
        InlineKeyboardButton(text=btn(lang, "no_btn"), callback_data="child|no")
    )
    # Кнопка "Назад" отдельной строкой
    builder.row(
        InlineKeyboardButton(text=btn(lang, "back"), callback_data="back_from|child")
    )
    
    return builder.as_markup()


def get_pets_keyboard(lang: str | None = None) -> InlineKeyboardMarkup:
    """клавиатура выбора дети есть нету"""
    builder = InlineKeyboardBuilder()

    # кнопка любой площади
    builder.row(
        InlineKeyboardButton(text=btn(lang, "yes_btn"), callback_data="pets|yes"),
        InlineKeyboardButton(text=btn(lang, "no_btn"), callback_data="pets|no")
    )
    # Кнопка "Назад" отдельной строкой
    builder.row(
        InlineKeyboardButton(text=btn(lang, "back"), callback_data="back_from|pets")
    )
    
    return builder.as_markup()


def get_results_keyboard(lang: str | None = None, search_id: int=None) -> InlineKeyboardMarkup:
    """просмотра результатов"""
    builder = InlineKeyboardBuilder()
    params = {
        "type": "listing",
        "search_id": search_id,
        "lang": lang,
        }
    url = add_query_params(MINIAPP_URL, params)
    builder.row(
        InlineKeyboardButton(text=btn(lang, "result_btn"), web_app=WebAppInfo(url=url))
    )
    # Кнопка заполнить фильтр заново
    builder.row(
        InlineKeyboardButton(text=btn(lang, "refresh_btn"), callback_data="back_from|market_type")
    )
    
    return builder.as_markup()


def get_favorites_keyboard(lang: str | None = None,) -> InlineKeyboardMarkup:
    """просмотра результатов"""
    builder = InlineKeyboardBuilder()
    params = {
        "type": "saved",
        "lang": lang,
        }
    url = add_query_params(MINIAPP_URL, params)
    builder.row(
        InlineKeyboardButton(text=btn(lang, "my_favorites_btn"), web_app=WebAppInfo(url=url))
    )
    
    return builder.as_markup()
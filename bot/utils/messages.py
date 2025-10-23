from bot.utils.sender import send_or_edit_message
from bot.utils.images import get_image
from bot.texts import t
from bot.keyboards.lang import get_language_keyboard
from bot.keyboards.menu import *
from aiogram.types import Message, CallbackQuery
from db.models import User, District, City


async def send_language_prompt(target: Message | CallbackQuery, user: User, try_edit: bool=False) -> Message:
    lang = user.language_code
    key = "choose_language"
    return await send_or_edit_message(
        target,
        key="choose_language",
        lang=lang,
        text=t(lang, key),
        keyboard=get_language_keyboard(),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def send_language_set(target: Message | CallbackQuery, user: User, try_edit: bool=True) -> Message:
    lang = user.language_code
    key = "language_set"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def send_main_menu(target: Message | CallbackQuery, user: User, try_edit: bool=False) -> Message:
    lang = user.language_code
    key = "main_menu"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_main_menu(lang),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def start_search(target: Message | CallbackQuery, user: User, try_edit: bool=False) -> Message:
    """
    Обери тип пошуку
    """
    lang = user.language_code
    key = "search_type"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_search_type_keyboard(lang),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def estate_type(target: Message | CallbackQuery, user: User, try_edit: bool=True, deal_type: str='rent') -> Message:
    """
    Обери тип нерухомості
    """
    lang = user.language_code
    key = "estate_type"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_estate_type_keyboard(lang, deal_type),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def market_type(target: Message | CallbackQuery, user: User, try_edit: bool=True) -> Message:
    """
    Обери тип ринку
    """
    lang = user.language_code
    key = "market_type"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_market_type_keyboard(lang),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def select_city(target: Message | CallbackQuery, user: User, try_edit: bool=True, cities: list=[City]) -> Message:
    '''
    выбор города
    '''
    lang = user.language_code
    key = "select_city"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_select_city_keyboard(lang, cities),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def select_district(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=True,
        all_districts: list[District]=[],
        selected_districts:  list[District]=[]) -> Message:
    '''
    выбор райнов
    '''
    lang = user.language_code
    key = "select_district"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_select_district_keyboard(lang, all_districts, selected_districts),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )
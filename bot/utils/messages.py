from bot.utils.sender import send_or_edit_message
from bot.texts import t
from bot.keyboards.lang import get_language_keyboard
from bot.keyboards.menu import get_main_menu

from aiogram.types import Message, CallbackQuery

async def send_language_prompt(target: Message | CallbackQuery, lang: str=None, try_edit: bool=False):
    await send_or_edit_message(
        target,
        key="choose_language",
        lang=lang,
        text=t(lang, "choose_language"),
        keyboard=get_language_keyboard(),
        try_edit=try_edit,
        media_type="photo"
    )

async def send_language_set(target: Message | CallbackQuery, lang: str=None, try_edit: bool=True):

    await send_or_edit_message(
        target,
        key="language_set",
        lang=lang,
        text=t(lang, "language_set"),
        keyboard=None,
        try_edit=try_edit,
        media_type="photo"
    )

async def send_main_menu(target: Message | CallbackQuery, lang: str=None):

    await send_or_edit_message(
        target,
        key="main_menu",
        lang=lang,
        text=t(lang, "main_menu"),
        keyboard=get_main_menu(lang),
        try_edit=False,
        media_type="photo"
    )


from bot.utils.sender import send_or_edit_message
from bot.utils.images import get_image
from bot.texts import t
from bot.keyboards.lang import get_language_keyboard
from bot.keyboards.menu import get_main_menu


from aiogram.types import Message, CallbackQuery

async def send_language_prompt(target: Message | CallbackQuery, lang: str=None, try_edit: bool=False):
    key = "choose_language"
    await send_or_edit_message(
        target,
        key="choose_language",
        lang=lang,
        text=t(lang, key),
        keyboard=get_language_keyboard(),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )

async def send_language_set(target: Message | CallbackQuery, lang: str=None, try_edit: bool=True):
    
    key = "language_set"
    await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )

async def send_main_menu(target: Message | CallbackQuery, lang: str=None):

    key = "main_menu"
    await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_main_menu(lang),
        try_edit=False,
        photo=get_image(lang, key)
    )


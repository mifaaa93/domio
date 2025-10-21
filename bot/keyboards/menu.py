from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.texts import btn


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
